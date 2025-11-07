from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import models
from .decorators import (
    student_required, professor_required, registrar_required,
    dean_required, admission_staff_required, admin_required
)


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

    from .models import Student, Term, Section, StudentSubject
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


@login_required
def bulk_grade_upload(request, section_id):
    """
    Upload grades in bulk via CSV for a section
    """
    if not request.user.is_professor():
        messages.error(request, 'Access denied: Professors only')
        return redirect('dashboard')

    from .models import Section, StudentSubject, Grade, AuditTrail
    from .forms import BulkGradeUploadForm
    import csv
    import io

    try:
        section = Section.objects.get(id=section_id, professor=request.user)
    except Section.DoesNotExist:
        messages.error(request, 'Section not found or access denied.')
        return redirect('professor_dashboard')

    if request.method == 'POST':
        form = BulkGradeUploadForm(request.POST, request.FILES, section=section, professor=request.user)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            success_count = 0
            error_count = 0
            errors = []

            for row in reader:
                try:
                    student_id = row.get('student_id', '').strip()
                    grade_value = row.get('grade', '').strip()

                    if not student_id or not grade_value:
                        errors.append(f"Missing data in row: {row}")
                        error_count += 1
                        continue

                    # Find enrollment
                    enrollment = StudentSubject.objects.filter(
                        section=section,
                        student__user__username=student_id
                    ).first()

                    if not enrollment:
                        errors.append(f"Student {student_id} not found in this section")
                        error_count += 1
                        continue

                    # Validate grade
                    valid_grades = ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', '4.00', '5.00', 'INC', 'DRP', 'P']
                    if grade_value not in valid_grades:
                        errors.append(f"Invalid grade '{grade_value}' for student {student_id}")
                        error_count += 1
                        continue

                    # Create or update grade
                    grade_obj, created = Grade.objects.get_or_create(
                        student_subject=enrollment,
                        defaults={
                            'subject': enrollment.subject,
                            'professor': request.user,
                            'grade': grade_value
                        }
                    )

                    if not created:
                        old_grade = grade_obj.grade
                        grade_obj.grade = grade_value
                        grade_obj.save()

                        # Log grade change
                        AuditTrail.objects.create(
                            actor=request.user,
                            action='bulk_update_grade',
                            entity='Grade',
                            entity_id=grade_obj.id,
                            old_value_json={'grade': old_grade},
                            new_value_json={'grade': grade_value}
                        )

                    # Update enrollment status
                    if grade_value in ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']:
                        enrollment.status = 'completed'
                    elif grade_value in ['5.00', 'DRP']:
                        enrollment.status = 'failed'
                    elif grade_value == 'INC':
                        enrollment.status = 'inc'
                    elif grade_value == '4.00':
                        enrollment.status = 'repeat_required'
                    enrollment.save()

                    success_count += 1

                except Exception as e:
                    errors.append(f"Error processing row {row}: {str(e)}")
                    error_count += 1

            if success_count > 0:
                messages.success(request, f'Successfully uploaded {success_count} grades')
            if error_count > 0:
                messages.warning(request, f'{error_count} errors occurred. See details below.')
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)

            return redirect('section_students', section_id=section.id)
    else:
        form = BulkGradeUploadForm(section=section, professor=request.user)

    context = {
        'form': form,
        'section': section,
    }

    return render(request, 'portal/bulk_grade_upload.html', context)


# ============= TERM MANAGEMENT =============

@login_required
def term_management(request):
    """
    Registrar term management - list all terms
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Term

    terms = Term.objects.all().order_by('-start_date')

    context = {
        'terms': terms,
    }

    return render(request, 'portal/term_management.html', context)


@login_required
def term_create(request):
    """
    Create a new term
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Term, AuditTrail
    from django import forms

    class TermForm(forms.ModelForm):
        class Meta:
            model = Term
            fields = ['name', 'start_date', 'end_date', 'add_drop_deadline', 'grade_encoding_deadline', 'is_active']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'add_drop_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'grade_encoding_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            }

    if request.method == 'POST':
        form = TermForm(request.POST)
        if form.is_valid():
            term = form.save(commit=False)

            # If this term is set as active, deactivate all other terms
            if term.is_active:
                Term.objects.filter(is_active=True).update(is_active=False)

            term.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='create_term',
                entity='Term',
                entity_id=term.id,
                new_value_json={'name': term.name, 'start_date': str(term.start_date)}
            )

            messages.success(request, f'Term "{term.name}" created successfully')
            return redirect('term_management')
    else:
        form = TermForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'portal/term_form.html', context)


@login_required
def term_edit(request, term_id):
    """
    Edit an existing term
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Term, AuditTrail
    from django import forms

    try:
        term = Term.objects.get(id=term_id)
    except Term.DoesNotExist:
        messages.error(request, 'Term not found.')
        return redirect('term_management')

    class TermForm(forms.ModelForm):
        class Meta:
            model = Term
            fields = ['name', 'start_date', 'end_date', 'add_drop_deadline', 'grade_encoding_deadline', 'is_active']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'add_drop_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'grade_encoding_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            }

    if request.method == 'POST':
        form = TermForm(request.POST, instance=term)
        if form.is_valid():
            old_values = {
                'name': term.name,
                'start_date': str(term.start_date),
                'is_active': term.is_active
            }

            term = form.save(commit=False)

            # If this term is set as active, deactivate all other terms
            if term.is_active:
                Term.objects.exclude(id=term.id).filter(is_active=True).update(is_active=False)

            term.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_term',
                entity='Term',
                entity_id=term.id,
                old_value_json=old_values,
                new_value_json={'name': term.name, 'start_date': str(term.start_date), 'is_active': term.is_active}
            )

            messages.success(request, f'Term "{term.name}" updated successfully')
            return redirect('term_management')
    else:
        form = TermForm(instance=term)

    context = {
        'form': form,
        'term': term,
        'action': 'Edit',
    }

    return render(request, 'portal/term_form.html', context)


@login_required
def term_delete(request, term_id):
    """
    Delete a term (with confirmation)
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Term, AuditTrail

    try:
        term = Term.objects.get(id=term_id)
    except Term.DoesNotExist:
        messages.error(request, 'Term not found.')
        return redirect('term_management')

    # Check if term has enrollments
    if term.student_enrollments.exists():
        messages.error(request, 'Cannot delete term with existing enrollments. Archive it instead.')
        return redirect('term_management')

    if request.method == 'POST':
        term_name = term.name

        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='delete_term',
            entity='Term',
            entity_id=term.id,
            old_value_json={'name': term.name, 'start_date': str(term.start_date)}
        )

        term.delete()
        messages.success(request, f'Term "{term_name}" deleted successfully')
        return redirect('term_management')

    context = {
        'term': term,
    }

    return render(request, 'portal/term_confirm_delete.html', context)


# ============= SECTION MANAGEMENT =============

@login_required
def section_management(request):
    """
    Registrar section management - list all sections
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Section, Term
    from django.db.models import Count

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()

    # Get all terms for filter
    terms = Term.objects.all().order_by('-start_date')

    # Filter by term
    term_filter = request.GET.get('term', None)
    if term_filter:
        try:
            selected_term = Term.objects.get(id=term_filter)
        except Term.DoesNotExist:
            selected_term = active_term
    else:
        selected_term = active_term

    sections = Section.objects.filter(
        term=selected_term
    ).select_related('subject', 'professor', 'term').annotate(
        enrolled=Count('student_enrollments')
    ).order_by('subject__code') if selected_term else []

    context = {
        'sections': sections,
        'terms': terms,
        'selected_term': selected_term,
        'active_term': active_term,
    }

    return render(request, 'portal/section_management.html', context)


@login_required
def section_create(request):
    """
    Create a new section
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Section, Subject, Term, User, AuditTrail
    from django import forms

    class SectionForm(forms.ModelForm):
        class Meta:
            model = Section
            fields = ['subject', 'term', 'professor', 'section_code', 'capacity', 'status']
            widgets = {
                'subject': forms.Select(attrs={'class': 'form-control'}),
                'term': forms.Select(attrs={'class': 'form-control'}),
                'professor': forms.Select(attrs={'class': 'form-control'}),
                'section_code': forms.TextInput(attrs={'class': 'form-control'}),
                'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
                'status': forms.Select(attrs={'class': 'form-control'}),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Limit professor choices to users with professor role
            self.fields['professor'].queryset = User.objects.filter(role='professor')

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='create_section',
                entity='Section',
                entity_id=section.id,
                new_value_json={
                    'section_code': section.section_code,
                    'subject': section.subject.code,
                    'term': section.term.name
                }
            )

            messages.success(request, f'Section "{section.section_code}" created successfully')
            return redirect('section_management')
    else:
        form = SectionForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'portal/section_form.html', context)


@login_required
def section_edit(request, section_id):
    """
    Edit an existing section
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Section, User, AuditTrail
    from django import forms

    try:
        section = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        messages.error(request, 'Section not found.')
        return redirect('section_management')

    class SectionForm(forms.ModelForm):
        class Meta:
            model = Section
            fields = ['subject', 'term', 'professor', 'section_code', 'capacity', 'status']
            widgets = {
                'subject': forms.Select(attrs={'class': 'form-control'}),
                'term': forms.Select(attrs={'class': 'form-control'}),
                'professor': forms.Select(attrs={'class': 'form-control'}),
                'section_code': forms.TextInput(attrs={'class': 'form-control'}),
                'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
                'status': forms.Select(attrs={'class': 'form-control'}),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['professor'].queryset = User.objects.filter(role='professor')

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            old_values = {
                'section_code': section.section_code,
                'capacity': section.capacity,
                'professor': section.professor.username
            }

            section = form.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_section',
                entity='Section',
                entity_id=section.id,
                old_value_json=old_values,
                new_value_json={
                    'section_code': section.section_code,
                    'capacity': section.capacity,
                    'professor': section.professor.username
                }
            )

            messages.success(request, f'Section "{section.section_code}" updated successfully')
            return redirect('section_management')
    else:
        form = SectionForm(instance=section)

    context = {
        'form': form,
        'section': section,
        'action': 'Edit',
    }

    return render(request, 'portal/section_form.html', context)


@login_required
def section_delete(request, section_id):
    """
    Delete a section (with confirmation)
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Section, AuditTrail

    try:
        section = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        messages.error(request, 'Section not found.')
        return redirect('section_management')

    # Check if section has enrollments
    if section.student_enrollments.exists():
        messages.error(request, 'Cannot delete section with existing enrollments.')
        return redirect('section_management')

    if request.method == 'POST':
        section_code = section.section_code

        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='delete_section',
            entity='Section',
            entity_id=section.id,
            old_value_json={'section_code': section.section_code, 'subject': section.subject.code}
        )

        section.delete()
        messages.success(request, f'Section "{section_code}" deleted successfully')
        return redirect('section_management')

    context = {
        'section': section,
    }

    return render(request, 'portal/section_confirm_delete.html', context)


# ============= PROGRAM & CURRICULUM MANAGEMENT =============

@login_required
def program_management(request):
    """
    Registrar program management - list all programs
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Program
    from django.db.models import Count

    programs = Program.objects.annotate(
        student_count=Count('students'),
        curriculum_count=Count('curricula')
    ).order_by('name')

    context = {
        'programs': programs,
    }

    return render(request, 'portal/program_management.html', context)


@login_required
def program_create(request):
    """
    Create a new program
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Program, AuditTrail
    from django import forms

    class ProgramForm(forms.ModelForm):
        class Meta:
            model = Program
            fields = ['name', 'level', 'passing_grade']
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'level': forms.Select(attrs={'class': 'form-control'}),
                'passing_grade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            }

    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='create_program',
                entity='Program',
                entity_id=program.id,
                new_value_json={'name': program.name, 'level': program.level}
            )

            messages.success(request, f'Program "{program.name}" created successfully')
            return redirect('program_management')
    else:
        form = ProgramForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'portal/program_form.html', context)


@login_required
def program_edit(request, program_id):
    """
    Edit an existing program
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Program, AuditTrail
    from django import forms

    try:
        program = Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        messages.error(request, 'Program not found.')
        return redirect('program_management')

    class ProgramForm(forms.ModelForm):
        class Meta:
            model = Program
            fields = ['name', 'level', 'passing_grade']
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'level': forms.Select(attrs={'class': 'form-control'}),
                'passing_grade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            }

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            old_values = {'name': program.name, 'level': program.level}
            program = form.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_program',
                entity='Program',
                entity_id=program.id,
                old_value_json=old_values,
                new_value_json={'name': program.name, 'level': program.level}
            )

            messages.success(request, f'Program "{program.name}" updated successfully')
            return redirect('program_management')
    else:
        form = ProgramForm(instance=program)

    context = {
        'form': form,
        'program': program,
        'action': 'Edit',
    }

    return render(request, 'portal/program_form.html', context)


# ============= SETTINGS MANAGEMENT =============

@login_required
def settings_management(request):
    """
    Admin settings management
    """
    if not request.user.is_admin_user() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Admin or Registrar only')
        return redirect('dashboard')

    from .models import Setting

    settings = Setting.objects.all().order_by('key_name')

    context = {
        'settings': settings,
    }

    return render(request, 'portal/settings_management.html', context)


@login_required
def setting_edit(request, setting_id):
    """
    Edit a setting value
    """
    if not request.user.is_admin_user() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Admin or Registrar only')
        return redirect('dashboard')

    from .models import Setting, AuditTrail
    from django import forms

    try:
        setting = Setting.objects.get(id=setting_id)
    except Setting.DoesNotExist:
        messages.error(request, 'Setting not found.')
        return redirect('settings_management')

    class SettingForm(forms.ModelForm):
        class Meta:
            model = Setting
            fields = ['value_text', 'description']
            widgets = {
                'value_text': forms.TextInput(attrs={'class': 'form-control'}),
                'description': forms.TextInput(attrs={'class': 'form-control'}),
            }

    if request.method == 'POST':
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            old_value = setting.value_text
            setting = form.save(commit=False)
            setting.updated_by = request.user
            setting.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_setting',
                entity='Setting',
                entity_id=setting.id,
                old_value_json={'key_name': setting.key_name, 'value': old_value},
                new_value_json={'key_name': setting.key_name, 'value': setting.value_text}
            )

            messages.success(request, f'Setting "{setting.key_name}" updated successfully')
            return redirect('settings_management')
    else:
        form = SettingForm(instance=setting)

    context = {
        'form': form,
        'setting': setting,
    }

    return render(request, 'portal/setting_form.html', context)


# ============= CURRICULUM MANAGEMENT =============

@login_required
def curriculum_management(request):
    """
    Registrar curriculum management - list all curricula
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum

    curricula = Curriculum.objects.select_related('program').all().order_by('program__name', '-effective_sy')

    context = {
        'curricula': curricula,
    }

    return render(request, 'portal/curriculum_management.html', context)


@login_required
def curriculum_create(request):
    """
    Create a new curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum, Program, AuditTrail
    from django import forms

    class CurriculumForm(forms.ModelForm):
        class Meta:
            model = Curriculum
            fields = ['program', 'version', 'effective_sy', 'active']
            widgets = {
                'program': forms.Select(attrs={'class': 'form-control'}),
                'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CHED 2021 Rev'}),
                'effective_sy': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., AY 2021-2022'}),
            }

    if request.method == 'POST':
        form = CurriculumForm(request.POST)
        if form.is_valid():
            curriculum = form.save(commit=False)

            # If this curriculum is set as active, deactivate other curricula for the same program
            if curriculum.active:
                Curriculum.objects.filter(program=curriculum.program, active=True).update(active=False)

            curriculum.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='create_curriculum',
                entity='Curriculum',
                entity_id=curriculum.id,
                new_value_json={'program': curriculum.program.name, 'version': curriculum.version}
            )

            messages.success(request, f'Curriculum "{curriculum.version}" created successfully')
            return redirect('curriculum_management')
    else:
        form = CurriculumForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'portal/curriculum_form.html', context)


@login_required
def curriculum_edit(request, curriculum_id):
    """
    Edit an existing curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum, AuditTrail
    from django import forms

    try:
        curriculum = Curriculum.objects.get(id=curriculum_id)
    except Curriculum.DoesNotExist:
        messages.error(request, 'Curriculum not found.')
        return redirect('curriculum_management')

    class CurriculumForm(forms.ModelForm):
        class Meta:
            model = Curriculum
            fields = ['program', 'version', 'effective_sy', 'active']
            widgets = {
                'program': forms.Select(attrs={'class': 'form-control'}),
                'version': forms.TextInput(attrs={'class': 'form-control'}),
                'effective_sy': forms.TextInput(attrs={'class': 'form-control'}),
            }

    if request.method == 'POST':
        form = CurriculumForm(request.POST, instance=curriculum)
        if form.is_valid():
            old_values = {'version': curriculum.version, 'active': curriculum.active}
            curriculum = form.save(commit=False)

            # If this curriculum is set as active, deactivate other curricula for the same program
            if curriculum.active:
                Curriculum.objects.filter(program=curriculum.program, active=True).exclude(id=curriculum.id).update(active=False)

            curriculum.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_curriculum',
                entity='Curriculum',
                entity_id=curriculum.id,
                old_value_json=old_values,
                new_value_json={'version': curriculum.version, 'active': curriculum.active}
            )

            messages.success(request, f'Curriculum "{curriculum.version}" updated successfully')
            return redirect('curriculum_management')
    else:
        form = CurriculumForm(instance=curriculum)

    context = {
        'form': form,
        'curriculum': curriculum,
        'action': 'Edit',
    }

    return render(request, 'portal/curriculum_form.html', context)


@login_required
def curriculum_delete(request, curriculum_id):
    """
    Delete a curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum, AuditTrail

    try:
        curriculum = Curriculum.objects.get(id=curriculum_id)
    except Curriculum.DoesNotExist:
        messages.error(request, 'Curriculum not found.')
        return redirect('curriculum_management')

    # Check if curriculum has students
    if curriculum.students.exists():
        messages.error(request, f'Cannot delete curriculum "{curriculum.version}" - it has students assigned to it')
        return redirect('curriculum_management')

    if request.method == 'POST':
        curriculum_version = curriculum.version

        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='delete_curriculum',
            entity='Curriculum',
            entity_id=curriculum.id,
            old_value_json={'version': curriculum.version, 'program': curriculum.program.name}
        )

        curriculum.delete()
        messages.success(request, f'Curriculum "{curriculum_version}" deleted successfully')
        return redirect('curriculum_management')

    context = {
        'curriculum': curriculum,
    }

    return render(request, 'portal/curriculum_confirm_delete.html', context)


# ============= SUBJECT MANAGEMENT =============

@login_required
def subject_management(request):
    """
    Registrar subject management - list all subjects
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject

    subjects = Subject.objects.select_related('program').all().order_by('program__name', 'code')

    # Filter by program if specified
    program_id = request.GET.get('program')
    if program_id:
        subjects = subjects.filter(program_id=program_id)

    context = {
        'subjects': subjects,
    }

    return render(request, 'portal/subject_management.html', context)


@login_required
def subject_create(request):
    """
    Create a new subject
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject, AuditTrail
    from django import forms

    class SubjectForm(forms.ModelForm):
        class Meta:
            model = Subject
            fields = ['program', 'code', 'title', 'description', 'units', 'type', 'recommended_year', 'recommended_sem', 'active']
            widgets = {
                'program': forms.Select(attrs={'class': 'form-control'}),
                'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101'}),
                'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Introduction to Computing'}),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'units': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
                'type': forms.Select(attrs={'class': 'form-control'}),
                'recommended_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
                'recommended_sem': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
            }

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='create_subject',
                entity='Subject',
                entity_id=subject.id,
                new_value_json={'code': subject.code, 'title': subject.title}
            )

            messages.success(request, f'Subject "{subject.code}" created successfully')
            return redirect('subject_management')
    else:
        form = SubjectForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'portal/subject_form.html', context)


@login_required
def subject_edit(request, subject_id):
    """
    Edit an existing subject
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject, AuditTrail
    from django import forms

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('subject_management')

    class SubjectForm(forms.ModelForm):
        class Meta:
            model = Subject
            fields = ['program', 'code', 'title', 'description', 'units', 'type', 'recommended_year', 'recommended_sem', 'active']
            widgets = {
                'program': forms.Select(attrs={'class': 'form-control'}),
                'code': forms.TextInput(attrs={'class': 'form-control'}),
                'title': forms.TextInput(attrs={'class': 'form-control'}),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'units': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
                'type': forms.Select(attrs={'class': 'form-control'}),
                'recommended_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
                'recommended_sem': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
            }

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            old_values = {'code': subject.code, 'title': subject.title, 'units': float(subject.units)}
            subject = form.save()

            # Log update
            AuditTrail.objects.create(
                actor=request.user,
                action='update_subject',
                entity='Subject',
                entity_id=subject.id,
                old_value_json=old_values,
                new_value_json={'code': subject.code, 'title': subject.title, 'units': float(subject.units)}
            )

            messages.success(request, f'Subject "{subject.code}" updated successfully')
            return redirect('subject_management')
    else:
        form = SubjectForm(instance=subject)

    context = {
        'form': form,
        'subject': subject,
        'action': 'Edit',
    }

    return render(request, 'portal/subject_form.html', context)


@login_required
def subject_delete(request, subject_id):
    """
    Delete a subject
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject, AuditTrail

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('subject_management')

    # Check if subject has sections or enrollments
    if subject.sections.exists() or subject.student_enrollments.exists():
        messages.error(request, f'Cannot delete subject "{subject.code}" - it has existing sections or enrollments')
        return redirect('subject_management')

    if request.method == 'POST':
        subject_code = subject.code

        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='delete_subject',
            entity='Subject',
            entity_id=subject.id,
            old_value_json={'code': subject.code, 'title': subject.title}
        )

        subject.delete()
        messages.success(request, f'Subject "{subject_code}" deleted successfully')
        return redirect('subject_management')

    context = {
        'subject': subject,
    }

    return render(request, 'portal/subject_confirm_delete.html', context)


# ============= CURRICULUM SUBJECT MAPPING =============

@login_required
def curriculum_subjects(request, curriculum_id):
    """
    Manage subjects mapped to a curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum, CurriculumSubject, Subject

    try:
        curriculum = Curriculum.objects.select_related('program').get(id=curriculum_id)
    except Curriculum.DoesNotExist:
        messages.error(request, 'Curriculum not found.')
        return redirect('curriculum_management')

    # Get all curriculum subjects organized by year and term
    curriculum_subjects = CurriculumSubject.objects.filter(
        curriculum=curriculum
    ).select_related('subject').order_by('year_level', 'term_no')

    # Get available subjects for this program that aren't already mapped
    mapped_subject_ids = curriculum_subjects.values_list('subject_id', flat=True)
    available_subjects = Subject.objects.filter(
        program=curriculum.program,
        active=True
    ).exclude(id__in=mapped_subject_ids)

    context = {
        'curriculum': curriculum,
        'curriculum_subjects': curriculum_subjects,
        'available_subjects': available_subjects,
    }

    return render(request, 'portal/curriculum_subjects.html', context)


@login_required
def curriculum_subject_add(request, curriculum_id):
    """
    Add a subject to a curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Curriculum, CurriculumSubject, Subject, AuditTrail
    from django import forms

    try:
        curriculum = Curriculum.objects.get(id=curriculum_id)
    except Curriculum.DoesNotExist:
        messages.error(request, 'Curriculum not found.')
        return redirect('curriculum_management')

    class CurriculumSubjectForm(forms.ModelForm):
        subject = forms.ModelChoiceField(
            queryset=Subject.objects.filter(program=curriculum.program, active=True),
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        class Meta:
            model = CurriculumSubject
            fields = ['subject', 'year_level', 'term_no', 'is_recommended']
            widgets = {
                'year_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
                'term_no': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
            }

    if request.method == 'POST':
        form = CurriculumSubjectForm(request.POST)
        if form.is_valid():
            curriculum_subject = form.save(commit=False)
            curriculum_subject.curriculum = curriculum
            curriculum_subject.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='add_curriculum_subject',
                entity='CurriculumSubject',
                entity_id=curriculum_subject.id,
                new_value_json={
                    'curriculum': curriculum.version,
                    'subject': curriculum_subject.subject.code,
                    'year_level': curriculum_subject.year_level,
                    'term_no': curriculum_subject.term_no
                }
            )

            messages.success(request, f'Subject "{curriculum_subject.subject.code}" added to curriculum')
            return redirect('curriculum_subjects', curriculum_id=curriculum.id)
    else:
        form = CurriculumSubjectForm()

    context = {
        'form': form,
        'curriculum': curriculum,
        'action': 'Add',
    }

    return render(request, 'portal/curriculum_subject_form.html', context)


@login_required
def curriculum_subject_remove(request, curriculum_subject_id):
    """
    Remove a subject from a curriculum
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import CurriculumSubject, AuditTrail

    try:
        curriculum_subject = CurriculumSubject.objects.select_related('curriculum', 'subject').get(id=curriculum_subject_id)
    except CurriculumSubject.DoesNotExist:
        messages.error(request, 'Curriculum subject mapping not found.')
        return redirect('curriculum_management')

    curriculum_id = curriculum_subject.curriculum.id

    if request.method == 'POST':
        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='remove_curriculum_subject',
            entity='CurriculumSubject',
            entity_id=curriculum_subject.id,
            old_value_json={
                'curriculum': curriculum_subject.curriculum.version,
                'subject': curriculum_subject.subject.code
            }
        )

        curriculum_subject.delete()
        messages.success(request, f'Subject removed from curriculum')
        return redirect('curriculum_subjects', curriculum_id=curriculum_id)

    context = {
        'curriculum_subject': curriculum_subject,
    }

    return render(request, 'portal/curriculum_subject_confirm_delete.html', context)


# ============= PREREQUISITE MANAGEMENT =============

@login_required
def prerequisite_management(request, subject_id):
    """
    Manage prerequisites for a subject
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject, Prerequisite

    try:
        subject = Subject.objects.select_related('program').get(id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('subject_management')

    # Get all prerequisites for this subject
    prerequisites = Prerequisite.objects.filter(
        subject=subject
    ).select_related('prereq_subject')

    # Get available subjects for prerequisites (same program, excluding self and existing prerequisites)
    existing_prereq_ids = prerequisites.values_list('prereq_subject_id', flat=True)
    available_prereqs = Subject.objects.filter(
        program=subject.program,
        active=True
    ).exclude(id=subject.id).exclude(id__in=existing_prereq_ids)

    context = {
        'subject': subject,
        'prerequisites': prerequisites,
        'available_prereqs': available_prereqs,
    }

    return render(request, 'portal/prerequisite_management.html', context)


@login_required
def prerequisite_add(request, subject_id):
    """
    Add a prerequisite to a subject
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Subject, Prerequisite, AuditTrail
    from django import forms

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('subject_management')

    class PrerequisiteForm(forms.ModelForm):
        prereq_subject = forms.ModelChoiceField(
            queryset=Subject.objects.filter(program=subject.program, active=True).exclude(id=subject.id),
            widget=forms.Select(attrs={'class': 'form-control'}),
            label='Prerequisite Subject'
        )

        class Meta:
            model = Prerequisite
            fields = ['prereq_subject']

    if request.method == 'POST':
        form = PrerequisiteForm(request.POST)
        if form.is_valid():
            prerequisite = form.save(commit=False)
            prerequisite.subject = subject
            prerequisite.save()

            # Log creation
            AuditTrail.objects.create(
                actor=request.user,
                action='add_prerequisite',
                entity='Prerequisite',
                entity_id=prerequisite.id,
                new_value_json={
                    'subject': subject.code,
                    'prereq_subject': prerequisite.prereq_subject.code
                }
            )

            messages.success(request, f'Prerequisite "{prerequisite.prereq_subject.code}" added')
            return redirect('prerequisite_management', subject_id=subject.id)
    else:
        form = PrerequisiteForm()

    context = {
        'form': form,
        'subject': subject,
        'action': 'Add',
    }

    return render(request, 'portal/prerequisite_form.html', context)


@login_required
def prerequisite_remove(request, prerequisite_id):
    """
    Remove a prerequisite
    """
    if not request.user.is_registrar():
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')

    from .models import Prerequisite, AuditTrail

    try:
        prerequisite = Prerequisite.objects.select_related('subject', 'prereq_subject').get(id=prerequisite_id)
    except Prerequisite.DoesNotExist:
        messages.error(request, 'Prerequisite not found.')
        return redirect('subject_management')

    subject_id = prerequisite.subject.id

    if request.method == 'POST':
        # Log deletion
        AuditTrail.objects.create(
            actor=request.user,
            action='remove_prerequisite',
            entity='Prerequisite',
            entity_id=prerequisite.id,
            old_value_json={
                'subject': prerequisite.subject.code,
                'prereq_subject': prerequisite.prereq_subject.code
            }
        )

        prerequisite.delete()
        messages.success(request, 'Prerequisite removed successfully')
        return redirect('prerequisite_management', subject_id=subject_id)

    context = {
        'prerequisite': prerequisite,
    }

    return render(request, 'portal/prerequisite_confirm_delete.html', context)


# ============= STUDENT ADMISSION PROCESSING =============

@login_required
def admission_processing(request):
    """
    Admission staff dashboard for processing student applications
    """
    if not request.user.is_admission_staff():
        messages.error(request, 'Access denied: Admission staff only')
        return redirect('dashboard')

    from .models import Student, User

    # Get all students without profiles (potential new applicants)
    # For now, list all students with their status
    students = Student.objects.select_related('user', 'program', 'curriculum').all().order_by('-created_at')

    # Count by status
    active_count = students.filter(status='active').count()
    inactive_count = students.filter(status='inactive').count()
    graduated_count = students.filter(status='graduated').count()

    context = {
        'students': students,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'graduated_count': graduated_count,
    }

    return render(request, 'portal/admission_processing.html', context)


@login_required
def student_admit(request):
    """
    Admit a new student
    """
    if not request.user.is_admission_staff() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Admission staff or Registrar only')
        return redirect('dashboard')

    from .models import Student, User, Program, Curriculum, AuditTrail
    from django import forms

    class UserForm(forms.ModelForm):
        password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

        class Meta:
            model = User
            fields = ['username', 'first_name', 'last_name', 'email', 'password']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'form-control'}),
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
            }

    class StudentForm(forms.ModelForm):
        class Meta:
            model = Student
            fields = ['program', 'curriculum', 'status']
            widgets = {
                'program': forms.Select(attrs={'class': 'form-control'}),
                'curriculum': forms.Select(attrs={'class': 'form-control'}),
                'status': forms.Select(attrs={'class': 'form-control'}),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter curriculum to show only active ones
            self.fields['curriculum'].queryset = Curriculum.objects.filter(active=True).select_related('program')

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)

        if user_form.is_valid() and student_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.role = 'student'
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Create student profile
            student = student_form.save(commit=False)
            student.user = user
            student.save()

            # Log admission
            AuditTrail.objects.create(
                actor=request.user,
                action='admit_student',
                entity='Student',
                entity_id=student.id,
                new_value_json={
                    'username': user.username,
                    'program': student.program.name,
                    'curriculum': student.curriculum.version
                }
            )

            messages.success(request, f'Student "{user.username}" admitted successfully')
            return redirect('admission_processing')
    else:
        user_form = UserForm()
        student_form = StudentForm()

    context = {
        'user_form': user_form,
        'student_form': student_form,
        'action': 'Admit',
    }

    return render(request, 'portal/student_admit.html', context)


@login_required
def student_status_update(request, student_id):
    """
    Update student status (active, inactive, graduated)
    """
    if not request.user.is_admission_staff() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Admission staff or Registrar only')
        return redirect('dashboard')

    from .models import Student, AuditTrail

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('admission_processing')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Student.STATUS_CHOICES):
            old_status = student.status
            student.status = new_status
            student.save()

            # Log status change
            AuditTrail.objects.create(
                actor=request.user,
                action='update_student_status',
                entity='Student',
                entity_id=student.id,
                old_value_json={'status': old_status},
                new_value_json={'status': new_status}
            )

            messages.success(request, f'Student status updated to "{new_status}"')
        else:
            messages.error(request, 'Invalid status')

    return redirect('admission_processing')


# ============= ADVANCED REPORTING =============

@login_required
def reports_dashboard(request):
    """
    Advanced reporting dashboard
    """
    if not request.user.is_dean() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Dean or Registrar only')
        return redirect('dashboard')

    from .models import Program, Term, Grade, StudentSubject
    from django.db.models import Count, Avg, Q
    from decimal import Decimal

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()

    # Overall statistics
    total_students = StudentSubject.objects.filter(status='enrolled').values('student').distinct().count()
    total_enrollments = StudentSubject.objects.filter(status='enrolled').count()

    # Grade distribution
    grades = Grade.objects.all()
    passing_grades = grades.filter(grade__in=['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']).count()
    failing_grades = grades.filter(grade__in=['5.00', 'DRP']).count()
    inc_grades = grades.filter(grade='INC').count()

    # Program-wise enrollment
    program_stats = Program.objects.annotate(
        enrollment_count=Count('subjects__student_enrollments', filter=Q(subjects__student_enrollments__status='enrolled'))
    ).order_by('-enrollment_count')

    context = {
        'active_term': active_term,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'passing_grades': passing_grades,
        'failing_grades': failing_grades,
        'inc_grades': inc_grades,
        'program_stats': program_stats,
    }

    return render(request, 'portal/reports_dashboard.html', context)


@login_required
def report_grade_distribution(request):
    """
    Detailed grade distribution report
    """
    if not request.user.is_dean() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Dean or Registrar only')
        return redirect('dashboard')

    from .models import Grade, Term, Subject
    from django.db.models import Count

    # Filter options
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    grades = Grade.objects.all()

    if term_id:
        grades = grades.filter(student_subject__term_id=term_id)

    if subject_id:
        grades = grades.filter(subject_id=subject_id)

    # Count by grade value
    grade_counts = grades.values('grade').annotate(count=Count('id')).order_by('-count')

    # Get filter options
    terms = Term.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('code')

    context = {
        'grade_counts': grade_counts,
        'terms': terms,
        'subjects': subjects,
        'selected_term': term_id,
        'selected_subject': subject_id,
    }

    return render(request, 'portal/report_grade_distribution.html', context)


@login_required
def report_student_performance(request):
    """
    Student performance report (GPA, completion rates, etc.)
    """
    if not request.user.is_dean() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Dean or Registrar only')
        return redirect('dashboard')

    from .models import Student, StudentSubject, Grade
    from django.db.models import Count, Q
    from decimal import Decimal

    # Get all students with their stats
    students = Student.objects.select_related('user', 'program').all()

    student_data = []
    for student in students:
        # Get all completed subjects with grades
        completed = StudentSubject.objects.filter(
            student=student,
            status='completed'
        ).select_related('grade_record')

        # Calculate GPA
        total_grade_points = Decimal('0.0')
        total_units = Decimal('0.0')

        for ss in completed:
            if hasattr(ss, 'grade_record'):
                try:
                    grade_value = Decimal(ss.grade_record.grade)
                    total_grade_points += grade_value * ss.subject.units
                    total_units += ss.subject.units
                except (ValueError, TypeError):
                    pass

        gpa = (total_grade_points / total_units) if total_units > 0 else Decimal('0.0')

        # Count enrollments by status
        enrolled_count = StudentSubject.objects.filter(student=student, status='enrolled').count()
        completed_count = completed.count()
        failed_count = StudentSubject.objects.filter(student=student, status='failed').count()
        inc_count = StudentSubject.objects.filter(student=student, status='inc').count()

        student_data.append({
            'student': student,
            'gpa': round(gpa, 2),
            'enrolled_count': enrolled_count,
            'completed_count': completed_count,
            'failed_count': failed_count,
            'inc_count': inc_count,
        })

    # Sort by GPA descending
    student_data.sort(key=lambda x: x['gpa'], reverse=True)

    context = {
        'student_data': student_data,
    }

    return render(request, 'portal/report_student_performance.html', context)


# ============= INC GRADE EXPIRATION TRACKING =============

@login_required
def inc_grade_tracking(request):
    """
    Track INC grades and their expiration deadlines
    """
    if not request.user.is_dean() and not request.user.is_registrar():
        messages.error(request, 'Access denied: Dean or Registrar only')
        return redirect('dashboard')

    from .models import Grade, StudentSubject
    from django.utils import timezone
    from datetime import timedelta

    # Get all INC grades
    inc_grades = Grade.objects.filter(
        grade='INC'
    ).select_related('student_subject__student__user', 'subject', 'student_subject__term')

    # Calculate expiration status
    today = timezone.now().date()
    inc_data = []

    for grade in inc_grades:
        # Get deadline in months based on subject type
        deadline_months = grade.subject.get_inc_deadline_months()

        # Calculate expiration date
        posted_date = grade.posted_at.date()
        expiration_date = posted_date + timedelta(days=deadline_months * 30)  # Approximate

        # Calculate days remaining
        days_remaining = (expiration_date - today).days

        # Determine status
        if days_remaining < 0:
            status = 'expired'
            status_class = 'danger'
        elif days_remaining <= 30:
            status = 'critical'
            status_class = 'warning'
        else:
            status = 'active'
            status_class = 'success'

        inc_data.append({
            'grade': grade,
            'student': grade.student_subject.student,
            'posted_date': posted_date,
            'expiration_date': expiration_date,
            'days_remaining': days_remaining,
            'deadline_months': deadline_months,
            'status': status,
            'status_class': status_class,
        })

    # Sort by days remaining (expired first, then by urgency)
    inc_data.sort(key=lambda x: x['days_remaining'])

    context = {
        'inc_data': inc_data,
        'total_count': len(inc_data),
        'expired_count': len([x for x in inc_data if x['status'] == 'expired']),
        'critical_count': len([x for x in inc_data if x['status'] == 'critical']),
    }

    return render(request, 'portal/inc_grade_tracking.html', context)


# ===========================
# EXPORT VIEWS
# ===========================

from .exports import PDFExporter, CSVExporter, ExcelExporter


@login_required
@student_required
def export_cor_pdf(request):
    """Export Certificate of Registration as PDF."""
    student = request.user.student_profile
    term = TermService.get_active_term()

    if not term:
        messages.error(request, 'No active term found.')
        return redirect('student_dashboard')

    return PDFExporter.generate_cor(student, term)


@login_required
@professor_required
def export_section_roster_pdf(request, section_id):
    """Export section roster as PDF."""
    section = get_object_or_404(Section, id=section_id)

    # Verify professor is assigned to this section
    if section.professor != request.user:
        messages.error(request, 'You are not assigned to this section.')
        return redirect('professor_dashboard')

    return PDFExporter.generate_section_roster(section)


@login_required
@professor_required
def export_section_grades_csv(request, section_id):
    """Export section grades as CSV."""
    section = get_object_or_404(Section, id=section_id)

    # Verify professor is assigned to this section
    if section.professor != request.user:
        messages.error(request, 'You are not assigned to this section.')
        return redirect('professor_dashboard')

    return CSVExporter.export_grades(section)


@login_required
@professor_required
def export_section_grades_excel(request, section_id):
    """Export section grades as Excel."""
    section = get_object_or_404(Section, id=section_id)

    # Verify professor is assigned to this section
    if section.professor != request.user:
        messages.error(request, 'You are not assigned to this section.')
        return redirect('professor_dashboard')

    return ExcelExporter.export_grades_excel(section)


@login_required
@registrar_required
def export_enrollment_report_csv(request):
    """Export enrollment report as CSV."""
    term = TermService.get_active_term()

    if not term:
        messages.error(request, 'No active term found.')
        return redirect('registrar_dashboard')

    return CSVExporter.export_enrollment_report(term)


# ===========================
# PASSWORD MANAGEMENT VIEWS
# ===========================

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash


@login_required
def change_password(request):
    """Allow users to change their password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/change_password.html', {'form': form})


@login_required
@admin_required
def reset_user_password(request, user_id):
    """Admin can reset any user's password."""
    user_to_reset = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Generate temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Set the password
        user_to_reset.set_password(temp_password)
        user_to_reset.save()

        messages.success(request, f'Password reset for {user_to_reset.username}. Temporary password: {temp_password}')
        return redirect('dashboard')

    return render(request, 'portal/reset_user_password.html', {'user_to_reset': user_to_reset})
