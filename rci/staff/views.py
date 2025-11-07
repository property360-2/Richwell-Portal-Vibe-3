# rci/staff/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from enrollment.models import Student, Section, Term, StudentSubject
from academics.models import Subject, Program, Curriculum
from admission.models import AdmissionApplication
from users.models import User
from audit.models import AuditTrail


def check_staff_access(user):
    """Check if user has staff management access"""
    return user.role in ['admin', 'registrar', 'dean']


def check_admission_access(user):
    """Check if user has admission access"""
    return user.role in ['admin', 'admission']


# ==================== STUDENTS MANAGEMENT ====================

@login_required
def students_list_view(request):
    """View all students with search and filtering"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    students = Student.objects.select_related('user', 'program', 'curriculum').all()

    # Search functionality
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(student_id__icontains=search)
        )

    # Filter by program
    program_filter = request.GET.get('program', '')
    if program_filter:
        students = students.filter(program_id=program_filter)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        students = students.filter(status=status_filter)

    programs = Program.objects.all()

    context = {
        'students': students,
        'programs': programs,
        'search': search,
        'selected_program': program_filter,
        'selected_status': status_filter,
    }
    return render(request, 'staff/students_list.html', context)


@login_required
def student_detail_view(request, student_id):
    """View detailed student information"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    student = get_object_or_404(Student.objects.select_related('user', 'program', 'curriculum'), id=student_id)

    # Get enrolled subjects
    enrolled = StudentSubject.objects.filter(student=student).select_related(
        'subject', 'term'
    ).order_by('-term__start_date')

    # Get enrollments with sections
    enrollments = StudentSubject.objects.filter(student=student).select_related(
        'subject', 'section', 'term'
    ).order_by('-term__start_date')

    # Calculate statistics
    total_units = sum(ss.subject.units for ss in enrolled if ss.status == 'completed')
    completed_subjects = enrolled.filter(status='completed').count()
    enrolled_subjects = enrolled.filter(status='enrolled').count()

    context = {
        'student': student,
        'enrolled': enrolled,
        'enrollments': enrollments,
        'total_units': total_units,
        'completed_subjects': completed_subjects,
        'enrolled_subjects': enrolled_subjects,
    }
    return render(request, 'staff/student_detail.html', context)


# ==================== SECTIONS MANAGEMENT ====================

@login_required
def sections_list_view(request):
    """View all sections with filtering"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    sections = Section.objects.select_related('subject', 'term', 'professor').annotate(
        enrolled_count=Count('enrollments')
    ).all()

    # Filter by term
    term_filter = request.GET.get('term', '')
    if term_filter:
        sections = sections.filter(term_id=term_filter)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        sections = sections.filter(status=status_filter)

    terms = Term.objects.all().order_by('-start_date')

    context = {
        'sections': sections,
        'terms': terms,
        'selected_term': term_filter,
        'selected_status': status_filter,
    }
    return render(request, 'staff/sections_list.html', context)


@login_required
def section_detail_view(request, section_id):
    """View section details and enrolled students"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    section = get_object_or_404(
        Section.objects.select_related('subject', 'term', 'professor'),
        id=section_id
    )

    enrollments = StudentSubject.objects.filter(section=section).select_related(
        'student__user', 'subject'
    ).order_by('student__user__last_name')

    context = {
        'section': section,
        'enrollments': enrollments,
        'enrolled_count': enrollments.count(),
        'available_slots': section.capacity - enrollments.count(),
    }
    return render(request, 'staff/section_detail.html', context)


# ==================== TERM MANAGEMENT ====================

@login_required
def terms_list_view(request):
    """View all terms"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    terms = Term.objects.annotate(
        sections_count=Count('sections'),
        enrollments_count=Count('sections__enrollments')
    ).order_by('-start_date')

    context = {
        'terms': terms,
    }
    return render(request, 'staff/terms_list.html', context)


@login_required
def term_detail_view(request, term_id):
    """View term details"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    term = get_object_or_404(Term, id=term_id)

    sections = Section.objects.filter(term=term).select_related('subject', 'professor').annotate(
        enrolled_count=Count('enrollments')
    )

    enrollments = StudentSubject.objects.filter(term=term).select_related(
        'student__user', 'subject', 'section'
    )

    # Statistics
    total_sections = sections.count()
    total_enrollments = enrollments.count()
    unique_students = enrollments.values('student').distinct().count()

    context = {
        'term': term,
        'sections': sections,
        'total_sections': total_sections,
        'total_enrollments': total_enrollments,
        'unique_students': unique_students,
    }
    return render(request, 'staff/term_detail.html', context)


# ==================== ENROLLMENT OVERVIEW ====================

@login_required
def enrollments_overview_view(request):
    """Overview of all enrollments"""
    if not check_staff_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    enrollments = StudentSubject.objects.select_related(
        'student__user', 'subject', 'section', 'term'
    ).order_by('-created_at')

    # Filter by term
    term_filter = request.GET.get('term', '')
    if term_filter:
        enrollments = enrollments.filter(term_id=term_filter)

    # Filter by section
    section_filter = request.GET.get('section', '')
    if section_filter:
        enrollments = enrollments.filter(section_id=section_filter)

    # Search by student
    search = request.GET.get('search', '')
    if search:
        enrollments = enrollments.filter(
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__student_id__icontains=search)
        )

    terms = Term.objects.all().order_by('-start_date')

    # Limit to recent 100 by default
    enrollments = enrollments[:100]

    context = {
        'enrollments': enrollments,
        'terms': terms,
        'selected_term': term_filter,
        'search': search,
    }
    return render(request, 'staff/enrollments_overview.html', context)


# ==================== APPLICATIONS MANAGEMENT ====================

@login_required
def applications_list_view(request):
    """View all admission applications"""
    if not check_admission_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    applications = AdmissionApplication.objects.select_related('program').order_by('-submitted_at')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        applications = applications.filter(student_type=type_filter)

    # Search
    search = request.GET.get('search', '')
    if search:
        applications = applications.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    context = {
        'applications': applications,
        'selected_status': status_filter,
        'selected_type': type_filter,
        'search': search,
    }
    return render(request, 'staff/applications_list.html', context)


@login_required
def application_detail_view(request, application_id):
    """View application details"""
    if not check_admission_access(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    application = get_object_or_404(AdmissionApplication.objects.select_related('program'), id=application_id)

    context = {
        'application': application,
    }
    return render(request, 'staff/application_detail.html', context)
