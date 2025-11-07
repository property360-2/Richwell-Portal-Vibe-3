# rci/grades/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from .models import Grade
from enrollment.models import Section, StudentSubject, Student
from audit.models import AuditTrail
import json


# Professor Views

@login_required
def professor_sections_view(request):
    """View all sections assigned to this professor"""
    if request.user.role != 'professor':
        messages.error(request, 'Only professors can access grade management.')
        return redirect('dashboard')

    # Get all sections assigned to this professor
    sections = Section.objects.filter(
        professor=request.user
    ).select_related('subject', 'term').annotate(
        student_count=Count('student_subjects')
    ).order_by('-term__is_active', 'subject__code')

    context = {
        'sections': sections,
    }

    return render(request, 'grades/professor_sections.html', context)


@login_required
def section_grades_view(request, section_id):
    """View and manage grades for a specific section"""
    if request.user.role != 'professor':
        messages.error(request, 'Only professors can access grade management.')
        return redirect('dashboard')

    # Get section and verify professor ownership
    section = get_object_or_404(Section, id=section_id)

    if section.professor != request.user:
        messages.error(request, 'You can only manage grades for your assigned sections.')
        return redirect('grades:professor_sections')

    # Get all student enrollments for this section
    enrollments = StudentSubject.objects.filter(
        section=section
    ).select_related(
        'student', 'student__user', 'subject'
    ).prefetch_related('grade').order_by('student__user__last_name', 'student__user__first_name')

    # Get term and check if grade encoding is still allowed
    term = section.term
    from django.utils import timezone
    can_encode = term.is_active or timezone.now().date() <= term.grade_encoding_deadline

    # Prepare student data with grades
    student_data = []
    for enrollment in enrollments:
        grade_obj = None
        try:
            grade_obj = enrollment.grade
        except Grade.DoesNotExist:
            pass

        student_data.append({
            'enrollment': enrollment,
            'student': enrollment.student,
            'grade': grade_obj,
            'has_grade': grade_obj is not None,
        })

    context = {
        'section': section,
        'student_data': student_data,
        'can_encode': can_encode,
        'term': term,
    }

    return render(request, 'grades/section_grades.html', context)


@login_required
def submit_grade_view(request, enrollment_id):
    """Submit or update a grade for a student"""
    if request.method != 'POST':
        return redirect('grades:professor_sections')

    if request.user.role != 'professor':
        messages.error(request, 'Only professors can submit grades.')
        return redirect('dashboard')

    # Get enrollment
    enrollment = get_object_or_404(StudentSubject, id=enrollment_id)
    section = enrollment.section

    # Verify professor ownership
    if section.professor != request.user:
        messages.error(request, 'You can only submit grades for your assigned sections.')
        return redirect('grades:professor_sections')

    # Check if encoding is still allowed
    from django.utils import timezone
    term = section.term
    if not term.is_active and timezone.now().date() > term.grade_encoding_deadline:
        messages.error(request, f'Grade encoding deadline has passed ({term.grade_encoding_deadline}).')
        return redirect('grades:section_grades', section_id=section.id)

    # Get form data
    grade_value = request.POST.get('grade', '').strip()
    remarks = request.POST.get('remarks', '').strip()

    if not grade_value:
        messages.error(request, 'Grade is required.')
        return redirect('grades:section_grades', section_id=section.id)

    # Validate grade value
    valid_grades = ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', '3.25', '3.50', '3.75', '4.00', '5.00', 'INC', 'DRP']
    if grade_value not in valid_grades:
        messages.error(request, f'Invalid grade value: {grade_value}')
        return redirect('grades:section_grades', section_id=section.id)

    # Save grade with audit trail
    with transaction.atomic():
        # Get or create grade
        try:
            grade_obj = Grade.objects.get(student_subject=enrollment)
            old_grade = grade_obj.grade
            grade_obj.grade = grade_value
            grade_obj.remarks = remarks
            grade_obj.save()

            # Log change in audit trail
            AuditTrail.objects.create(
                actor=request.user,
                action='update_grade',
                entity='Grade',
                entity_id=grade_obj.id,
                old_value_json={'grade': old_grade},
                new_value_json={'grade': grade_value},
                notes=f"Updated grade for {enrollment.student.user.get_full_name()} in {section.subject.code}"
            )

            messages.success(
                request,
                f'Grade updated to {grade_value} for {enrollment.student.user.get_full_name()}'
            )

        except Grade.DoesNotExist:
            grade_obj = Grade.objects.create(
                student_subject=enrollment,
                subject=section.subject,
                professor=request.user,
                grade=grade_value,
                remarks=remarks
            )

            # Log creation in audit trail
            AuditTrail.objects.create(
                actor=request.user,
                action='create_grade',
                entity='Grade',
                entity_id=grade_obj.id,
                old_value_json={},
                new_value_json={'grade': grade_value},
                notes=f"Created grade for {enrollment.student.user.get_full_name()} in {section.subject.code}"
            )

            messages.success(
                request,
                f'Grade {grade_value} submitted for {enrollment.student.user.get_full_name()}'
            )

    return redirect('grades:section_grades', section_id=section.id)


# Student Views

@login_required
def student_grades_view(request):
    """View student's own grades"""
    if request.user.role != 'student':
        messages.error(request, 'Only students can view grades.')
        return redirect('dashboard')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get all enrollments with grades
    enrollments = StudentSubject.objects.filter(
        student=student
    ).select_related(
        'subject', 'section', 'term', 'professor'
    ).prefetch_related('grade').order_by('-term__start_date', 'subject__code')

    # Organize by term
    terms_data = {}
    for enrollment in enrollments:
        term_name = enrollment.term.name
        if term_name not in terms_data:
            terms_data[term_name] = {
                'term': enrollment.term,
                'enrollments': [],
                'total_units': 0,
                'completed_units': 0,
                'gpa_points': 0,
                'gpa_units': 0,
            }

        # Get grade
        grade_obj = None
        try:
            grade_obj = enrollment.grade
        except Grade.DoesNotExist:
            pass

        terms_data[term_name]['enrollments'].append({
            'enrollment': enrollment,
            'grade': grade_obj,
        })

        # Calculate units and GPA
        terms_data[term_name]['total_units'] += float(enrollment.subject.units)

        if grade_obj:
            if enrollment.status == 'completed':
                terms_data[term_name]['completed_units'] += float(enrollment.subject.units)

            # Calculate GPA (only for numeric grades)
            try:
                grade_value = float(grade_obj.grade)
                terms_data[term_name]['gpa_points'] += grade_value * float(enrollment.subject.units)
                terms_data[term_name]['gpa_units'] += float(enrollment.subject.units)
            except ValueError:
                pass  # Non-numeric grade (INC, DRP)

    # Calculate GPA for each term
    for term_name, data in terms_data.items():
        if data['gpa_units'] > 0:
            data['term_gpa'] = round(data['gpa_points'] / data['gpa_units'], 2)
        else:
            data['term_gpa'] = None

    # Calculate overall GPA
    total_gpa_points = sum(data['gpa_points'] for data in terms_data.values())
    total_gpa_units = sum(data['gpa_units'] for data in terms_data.values())
    overall_gpa = round(total_gpa_points / total_gpa_units, 2) if total_gpa_units > 0 else None

    # Calculate total completed units
    total_completed_units = sum(data['completed_units'] for data in terms_data.values())

    context = {
        'student': student,
        'terms_data': terms_data,
        'overall_gpa': overall_gpa,
        'total_completed_units': total_completed_units,
    }

    return render(request, 'grades/student_grades.html', context)
