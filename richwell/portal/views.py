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
