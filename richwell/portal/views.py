from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import models


def login_view(request):
    """
    Handle user login with role-based redirects
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            # Role-based redirect
            if user.is_student():
                return redirect('student_dashboard')
            elif user.is_professor():
                return redirect('professor_dashboard')
            elif user.is_registrar():
                return redirect('registrar_dashboard')
            elif user.is_dean():
                return redirect('dean_dashboard')
            elif user.is_admission_staff():
                return redirect('admission_dashboard')
            elif user.is_admin_user():
                return redirect('admin:index')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'portal/login.html')


def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    """
    Generic dashboard that redirects to role-specific dashboard
    """
    user = request.user

    if user.is_student():
        return redirect('student_dashboard')
    elif user.is_professor():
        return redirect('professor_dashboard')
    elif user.is_registrar():
        return redirect('registrar_dashboard')
    elif user.is_dean():
        return redirect('dean_dashboard')
    elif user.is_admission_staff():
        return redirect('admission_dashboard')
    elif user.is_admin_user():
        return redirect('admin:index')

    return render(request, 'portal/dashboard.html')


@login_required
def student_dashboard(request):
    """
    Student dashboard - view enrollments, grades, transcript
    """
    if not request.user.is_student():
        messages.error(request, 'Access denied: Students only')
        return redirect('dashboard')

    from .models import Student, StudentSubject, Grade, Term

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please contact the registrar.')
        return redirect('dashboard')

    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get current enrollments
    current_enrollments = StudentSubject.objects.filter(
        student=student,
        term=active_term
    ).select_related('subject', 'section', 'professor', 'term')

    # Get all grades
    all_grades = Grade.objects.filter(
        student_subject__student=student
    ).select_related('subject', 'professor', 'student_subject__term').order_by('-posted_at')

    # Calculate GPA
    passing_grades = all_grades.filter(grade__in=['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00'])
    if passing_grades.exists():
        total_grade = sum(float(g.grade) for g in passing_grades)
        gpa = total_grade / passing_grades.count()
    else:
        gpa = None

    context = {
        'student': student,
        'active_term': active_term,
        'current_enrollments': current_enrollments,
        'all_grades': all_grades,
        'gpa': gpa,
    }

    return render(request, 'portal/student_dashboard.html', context)


@login_required
def professor_dashboard(request):
    """
    Professor dashboard - view assigned sections and manage grades
    """
    if not request.user.is_professor():
        messages.error(request, 'Access denied: Professors only')
        return redirect('dashboard')

    from .models import Section, Term

    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get professor's sections for active term
    sections = Section.objects.filter(
        professor=request.user,
        term=active_term
    ).select_related('subject', 'term').prefetch_related('studentsubject_set')

    # Get all professor's sections (past and current)
    all_sections = Section.objects.filter(
        professor=request.user
    ).select_related('subject', 'term').order_by('-term__start_date')[:10]

    context = {
        'active_term': active_term,
        'sections': sections,
        'all_sections': all_sections,
    }

    return render(request, 'portal/professor_dashboard.html', context)


@login_required
def registrar_dashboard(request):
    """
    Registrar dashboard - manage enrollments, terms, and reports
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Term, StudentSubject, Student, Section
    from django.db.models import Count

    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get enrollment statistics
    total_students = Student.objects.filter(status='active').count()
    current_enrollments = StudentSubject.objects.filter(term=active_term).count() if active_term else 0

    # Get sections with enrollment counts
    sections = Section.objects.filter(
        term=active_term
    ).select_related('subject', 'professor').annotate(
        enrolled=Count('studentsubject')
    ).order_by('subject__code') if active_term else []

    # Recent enrollments
    recent_enrollments = StudentSubject.objects.select_related(
        'student__user', 'subject', 'section', 'term'
    ).order_by('-created_at')[:10]

    context = {
        'active_term': active_term,
        'total_students': total_students,
        'current_enrollments': current_enrollments,
        'sections': sections,
        'recent_enrollments': recent_enrollments,
    }

    return render(request, 'portal/registrar_dashboard.html', context)


@login_required
def dean_dashboard(request):
    """
    Dean dashboard - view program analytics and manage approvals
    """
    if not request.user.is_dean():
        messages.error(request, 'Access denied: Dean only')
        return redirect('dashboard')

    from .models import Program, Student, Grade, Term

    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get program statistics
    programs = Program.objects.annotate(
        student_count=models.Count('student', filter=models.Q(student__status='active'))
    ).order_by('name')

    # Get recent grades needing review (INC grades)
    inc_grades = Grade.objects.filter(
        grade='INC'
    ).select_related('student_subject__student__user', 'subject', 'professor').order_by('-posted_at')[:10]

    # Total active students
    total_students = Student.objects.filter(status='active').count()

    context = {
        'active_term': active_term,
        'programs': programs,
        'total_students': total_students,
        'inc_grades': inc_grades,
    }

    return render(request, 'portal/dean_dashboard.html', context)


@login_required
def admission_dashboard(request):
    """
    Admission dashboard - process applications and manage new students
    """
    if not request.user.is_admission_staff():
        messages.error(request, 'Access denied: Admission staff only')
        return redirect('dashboard')

    from .models import Student, Program
    from django.db.models import Count

    # Get recent students (newly created)
    recent_students = Student.objects.select_related(
        'user', 'program', 'curriculum'
    ).order_by('-created_at')[:20]

    # Get students by program
    program_stats = Program.objects.annotate(
        student_count=Count('student')
    ).order_by('name')

    context = {
        'recent_students': recent_students,
        'program_stats': program_stats,
    }

    return render(request, 'portal/admission_dashboard.html', context)


# ============= ENROLLMENT SYSTEM =============

@login_required
def enrollment_view(request):
    """
    Student enrollment page with available sections
    """
    if not request.user.is_student():
        messages.error(request, 'Access denied: Students only')
        return redirect('dashboard')

    from .models import Student, Term, Section
    from .forms import EnrollmentForm

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()

    if not active_term:
        messages.error(request, 'No active enrollment term.')
        return redirect('student_dashboard')

    if not active_term.is_enrollment_open():
        messages.warning(request, 'Enrollment period has closed.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, student=student, term=active_term)
        if form.is_valid():
            section = form.cleaned_data['section']

            # Create enrollment
            StudentSubject.objects.create(
                student=student,
                subject=section.subject,
                term=active_term,
                section=section,
                professor=section.professor,
                status='enrolled'
            )

            # Update section status
            section.update_status()

            messages.success(request, f'Successfully enrolled in {section.subject.code} - {section.section_code}')
            return redirect('enrollment')
    else:
        form = EnrollmentForm(student=student, term=active_term)

    # Get available sections grouped by subject
    available_sections = Section.objects.filter(
        term=active_term,
        status='open'
    ).select_related('subject', 'professor').order_by('subject__code')

    # Get current enrollments
    current_enrollments = StudentSubject.objects.filter(
        student=student,
        term=active_term
    ).select_related('subject', 'section')

    # Calculate current units
    current_units = sum(e.subject.units for e in current_enrollments)

    context = {
        'form': form,
        'student': student,
        'active_term': active_term,
        'available_sections': available_sections,
        'current_enrollments': current_enrollments,
        'current_units': current_units,
    }

    return render(request, 'portal/enrollment.html', context)


@login_required
def drop_enrollment(request, enrollment_id):
    """
    Drop an enrollment (only during add/drop period)
    """
    if not request.user.is_student():
        messages.error(request, 'Access denied: Students only')
        return redirect('dashboard')

    from .models import StudentSubject, Term

    try:
        enrollment = StudentSubject.objects.get(id=enrollment_id, student__user=request.user)
    except StudentSubject.DoesNotExist:
        messages.error(request, 'Enrollment not found.')
        return redirect('enrollment')

    # Check if enrollment is still open
    if not enrollment.term.is_enrollment_open():
        messages.error(request, 'Add/drop period has closed.')
        return redirect('enrollment')

    # Delete enrollment
    section = enrollment.section
    subject_code = enrollment.subject.code
    enrollment.delete()

    # Update section status
    section.update_status()

    messages.success(request, f'Successfully dropped {subject_code}')
    return redirect('enrollment')


# ============= GRADE MANAGEMENT =============

@login_required
def section_students(request, section_id):
    """
    View students enrolled in a section (for professors)
    """
    if not request.user.is_professor():
        messages.error(request, 'Access denied: Professors only')
        return redirect('dashboard')

    from .models import Section, StudentSubject, Grade

    try:
        section = Section.objects.get(id=section_id, professor=request.user)
    except Section.DoesNotExist:
        messages.error(request, 'Section not found or access denied.')
        return redirect('professor_dashboard')

    # Get enrolled students with their grades
    enrollments = StudentSubject.objects.filter(
        section=section
    ).select_related('student__user', 'student__program', 'subject').order_by('student__user__last_name', 'student__user__first_name')

    # Enrich enrollments with grade info
    enrollment_list = []
    for enrollment in enrollments:
        try:
            grade = Grade.objects.get(student_subject=enrollment)
        except Grade.DoesNotExist:
            grade = None

        enrollment_list.append({
            'enrollment': enrollment,
            'grade': grade,
        })

    context = {
        'section': section,
        'enrollment_list': enrollment_list,
    }

    return render(request, 'portal/section_students.html', context)


@login_required
def grade_student(request, enrollment_id):
    """
    Enter or update a grade for a student
    """
    if not request.user.is_professor():
        messages.error(request, 'Access denied: Professors only')
        return redirect('dashboard')

    from .models import StudentSubject
    from .forms import GradeEntryForm

    try:
        enrollment = StudentSubject.objects.get(id=enrollment_id, professor=request.user)
    except StudentSubject.DoesNotExist:
        messages.error(request, 'Enrollment not found or access denied.')
        return redirect('professor_dashboard')

    if request.method == 'POST':
        form = GradeEntryForm(request.POST, student_subject=enrollment, professor=request.user)
        if form.is_valid():
            grade = form.save()
            messages.success(request, f'Grade {grade.grade} saved for {enrollment.student.user.get_full_name()}')
            return redirect('section_students', section_id=enrollment.section.id)
    else:
        # Pre-populate form if grade exists
        try:
            existing_grade = Grade.objects.get(student_subject=enrollment)
            form = GradeEntryForm(
                initial={'grade': existing_grade.grade},
                student_subject=enrollment,
                professor=request.user
            )
        except Grade.DoesNotExist:
            form = GradeEntryForm(student_subject=enrollment, professor=request.user)

    context = {
        'form': form,
        'enrollment': enrollment,
    }

    return render(request, 'portal/grade_entry.html', context)
