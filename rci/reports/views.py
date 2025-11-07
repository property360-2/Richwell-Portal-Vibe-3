# rci/reports/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import Coalesce
from enrollment.models import Student, Term, Section, StudentSubject
from grades.models import Grade
from academics.models import Program, Subject
from audit.models import AuditTrail
from datetime import datetime, timedelta
from django.utils import timezone


def check_report_access(user):
    """Check if user has access to reports"""
    return user.role in ['admin', 'registrar', 'dean']


@login_required
def reports_dashboard_view(request):
    """Main reports dashboard"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    context = {
        'user': request.user,
    }

    return render(request, 'reports/dashboard.html', context)


@login_required
def enrollment_report_view(request):
    """Enrollment statistics per section, term, or program"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get filter parameters
    term_id = request.GET.get('term')
    program_id = request.GET.get('program')

    # Get all terms and programs for filters
    terms = Term.objects.all().order_by('-start_date')
    programs = Program.objects.all().order_by('name')

    # Base query
    sections_query = Section.objects.select_related('subject', 'term', 'professor', 'subject__program')

    # Apply filters
    if term_id:
        sections_query = sections_query.filter(term_id=term_id)
    if program_id:
        sections_query = sections_query.filter(subject__program_id=program_id)

    # Get sections with enrollment counts
    sections = sections_query.annotate(
        enrolled_count=Count('student_subjects', filter=Q(student_subjects__status='enrolled'))
    ).order_by('-term__is_active', 'subject__code')

    # Calculate summary statistics
    total_sections = sections.count()
    total_enrolled = StudentSubject.objects.filter(status='enrolled').count()

    if term_id:
        total_enrolled = StudentSubject.objects.filter(
            section__term_id=term_id,
            status='enrolled'
        ).count()

    # Enrollment by program
    enrollment_by_program = Student.objects.values(
        'program__name'
    ).annotate(
        student_count=Count('id')
    ).order_by('-student_count')

    context = {
        'sections': sections,
        'terms': terms,
        'programs': programs,
        'selected_term': int(term_id) if term_id else None,
        'selected_program': int(program_id) if program_id else None,
        'total_sections': total_sections,
        'total_enrolled': total_enrolled,
        'enrollment_by_program': enrollment_by_program,
    }

    return render(request, 'reports/enrollment_report.html', context)


@login_required
def grade_distribution_report_view(request):
    """Grade distribution and averages per subject"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get filter parameters
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    # Get all terms and subjects for filters
    terms = Term.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('code')

    # Base query
    grades_query = Grade.objects.select_related('subject', 'student_subject__term', 'student_subject__student')

    # Apply filters
    if term_id:
        grades_query = grades_query.filter(student_subject__term_id=term_id)
    if subject_id:
        grades_query = grades_query.filter(subject_id=subject_id)

    # Get grades
    grades = grades_query.order_by('subject__code', 'student_subject__student__user__last_name')

    # Calculate grade distribution
    grade_distribution = {}
    grade_ranges = {
        '1.00-1.50': (1.00, 1.50),
        '1.75-2.25': (1.75, 2.25),
        '2.50-3.00': (2.50, 3.00),
        '3.25-4.00': (3.25, 4.00),
        '5.00': (5.00, 5.00),
        'INC': None,
        'DRP': None,
    }

    for range_name in grade_ranges.keys():
        grade_distribution[range_name] = 0

    numeric_grades = []
    for grade in grades:
        try:
            grade_value = float(grade.grade)
            numeric_grades.append(grade_value)

            # Categorize grade
            if 1.00 <= grade_value <= 1.50:
                grade_distribution['1.00-1.50'] += 1
            elif 1.75 <= grade_value <= 2.25:
                grade_distribution['1.75-2.25'] += 1
            elif 2.50 <= grade_value <= 3.00:
                grade_distribution['2.50-3.00'] += 1
            elif 3.25 <= grade_value <= 4.00:
                grade_distribution['3.25-4.00'] += 1
            elif grade_value == 5.00:
                grade_distribution['5.00'] += 1
        except ValueError:
            # Non-numeric grade
            if grade.grade.upper() == 'INC':
                grade_distribution['INC'] += 1
            elif grade.grade.upper() == 'DRP':
                grade_distribution['DRP'] += 1

    # Calculate average
    average_grade = sum(numeric_grades) / len(numeric_grades) if numeric_grades else None
    if average_grade:
        average_grade = round(average_grade, 2)

    # Get subject-wise statistics
    subject_stats = Grade.objects.values(
        'subject__code',
        'subject__title'
    ).annotate(
        total_students=Count('id'),
        passing_count=Count('id', filter=Q(student_subject__status='completed')),
        failing_count=Count('id', filter=Q(student_subject__status='failed')),
        inc_count=Count('id', filter=Q(student_subject__status='inc'))
    ).order_by('subject__code')

    # Apply term filter to subject stats
    if term_id:
        subject_stats = subject_stats.filter(student_subject__term_id=term_id)

    context = {
        'grades': grades,
        'terms': terms,
        'subjects': subjects,
        'selected_term': int(term_id) if term_id else None,
        'selected_subject': int(subject_id) if subject_id else None,
        'grade_distribution': grade_distribution,
        'average_grade': average_grade,
        'total_grades': grades.count(),
        'subject_stats': subject_stats,
    }

    return render(request, 'reports/grade_distribution_report.html', context)


@login_required
def inc_tracking_report_view(request):
    """INC tracking and repeat rates"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get all INC grades
    inc_grades = Grade.objects.filter(
        grade__iexact='INC'
    ).select_related(
        'student_subject__student__user',
        'student_subject__term',
        'subject'
    ).order_by('inc_posted_date')

    # Categorize INC grades
    active_incs = []
    expired_incs = []

    for grade in inc_grades:
        if grade.is_inc_expired:
            expired_incs.append(grade)
        else:
            active_incs.append(grade)

    # Get repeat required students
    repeat_required = StudentSubject.objects.filter(
        status='repeat_required'
    ).select_related('student__user', 'subject', 'term').order_by('-term__start_date')

    # Calculate statistics
    total_incs = inc_grades.count()
    total_expired = len(expired_incs)
    total_active = len(active_incs)

    # INC by subject type
    inc_by_type = Grade.objects.filter(
        grade__iexact='INC'
    ).values('subject__type').annotate(
        count=Count('id')
    )

    context = {
        'active_incs': active_incs,
        'expired_incs': expired_incs,
        'repeat_required': repeat_required,
        'total_incs': total_incs,
        'total_expired': total_expired,
        'total_active': total_active,
        'inc_by_type': inc_by_type,
    }

    return render(request, 'reports/inc_tracking_report.html', context)


@login_required
def student_load_report_view(request):
    """Student load summary per term"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get filter parameters
    term_id = request.GET.get('term')
    program_id = request.GET.get('program')

    # Get all terms and programs for filters
    terms = Term.objects.all().order_by('-start_date')
    programs = Program.objects.all().order_by('name')

    # Base query - get students with their enrollments
    students_query = Student.objects.select_related('user', 'program')

    # Apply program filter
    if program_id:
        students_query = students_query.filter(program_id=program_id)

    # Get student load data
    student_loads = []
    for student in students_query:
        enrollments_query = StudentSubject.objects.filter(
            student=student,
            status='enrolled'
        ).select_related('subject')

        # Apply term filter
        if term_id:
            enrollments_query = enrollments_query.filter(term_id=term_id)

        total_units = enrollments_query.aggregate(
            total=Coalesce(Sum('subject__units'), 0)
        )['total']

        subject_count = enrollments_query.count()

        if subject_count > 0 or not term_id:  # Show all students if no term filter
            student_loads.append({
                'student': student,
                'total_units': total_units,
                'subject_count': subject_count,
            })

    # Sort by total units descending
    student_loads.sort(key=lambda x: x['total_units'], reverse=True)

    # Calculate statistics
    if student_loads:
        avg_units = sum(sl['total_units'] for sl in student_loads) / len(student_loads)
        avg_units = round(avg_units, 2)
        max_units = max(sl['total_units'] for sl in student_loads)
        min_units = min(sl['total_units'] for sl in student_loads if sl['subject_count'] > 0) if any(sl['subject_count'] > 0 for sl in student_loads) else 0
    else:
        avg_units = max_units = min_units = 0

    context = {
        'student_loads': student_loads,
        'terms': terms,
        'programs': programs,
        'selected_term': int(term_id) if term_id else None,
        'selected_program': int(program_id) if program_id else None,
        'avg_units': avg_units,
        'max_units': max_units,
        'min_units': min_units,
    }

    return render(request, 'reports/student_load_report.html', context)


@login_required
def section_utilization_report_view(request):
    """Section utilization (open vs full)"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get filter parameters
    term_id = request.GET.get('term')

    # Get all terms for filter
    terms = Term.objects.all().order_by('-start_date')

    # Base query
    sections_query = Section.objects.select_related('subject', 'term', 'professor')

    # Apply term filter
    if term_id:
        sections_query = sections_query.filter(term_id=term_id)

    # Get sections with enrollment counts
    sections = sections_query.annotate(
        enrolled_count=Count('student_subjects')
    ).order_by('subject__code')

    # Calculate utilization
    section_data = []
    for section in sections:
        utilization = (section.enrolled_count / section.capacity * 100) if section.capacity > 0 else 0
        section_data.append({
            'section': section,
            'enrolled': section.enrolled_count,
            'capacity': section.capacity,
            'available': section.capacity - section.enrolled_count,
            'utilization': round(utilization, 1),
            'is_full': section.enrolled_count >= section.capacity,
        })

    # Calculate summary statistics
    total_sections = len(section_data)
    full_sections = sum(1 for sd in section_data if sd['is_full'])
    total_capacity = sum(sd['capacity'] for sd in section_data)
    total_enrolled = sum(sd['enrolled'] for sd in section_data)
    overall_utilization = (total_enrolled / total_capacity * 100) if total_capacity > 0 else 0

    context = {
        'section_data': section_data,
        'terms': terms,
        'selected_term': int(term_id) if term_id else None,
        'total_sections': total_sections,
        'full_sections': full_sections,
        'total_capacity': total_capacity,
        'total_enrolled': total_enrolled,
        'overall_utilization': round(overall_utilization, 1),
    }

    return render(request, 'reports/section_utilization_report.html', context)


@login_required
def audit_trail_report_view(request):
    """Audit trail and system activity log"""
    if not check_report_access(request.user):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')

    # Get filter parameters
    action_type = request.GET.get('action')
    days = request.GET.get('days', '7')

    # Calculate date range
    try:
        days_int = int(days)
    except ValueError:
        days_int = 7

    start_date = timezone.now() - timedelta(days=days_int)

    # Base query
    audit_entries = AuditTrail.objects.select_related('actor').filter(
        created_at__gte=start_date
    )

    # Apply action filter
    if action_type:
        audit_entries = audit_entries.filter(action=action_type)

    # Order by most recent
    audit_entries = audit_entries.order_by('-created_at')[:100]  # Limit to 100 most recent

    # Get action types for filter
    action_types = AuditTrail.objects.values_list('action', flat=True).distinct()

    # Activity summary
    activity_summary = AuditTrail.objects.filter(
        created_at__gte=start_date
    ).values('action').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'audit_entries': audit_entries,
        'action_types': action_types,
        'selected_action': action_type,
        'selected_days': days,
        'activity_summary': activity_summary,
    }

    return render(request, 'reports/audit_trail_report.html', context)
