# rci/admission/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from .models import AdmissionApplication, TransfereeCredit
from .forms import AdmissionApplicationForm
from settingsapp.models import Setting
from users.models import User
from enrollment.models import Student, Term, Section, StudentSubject
from academics.models import CurriculumSubject, Subject
import random
import string


def admission_form_view(request):
    """Public admission form"""
    # Check if admission is enabled
    admission_enabled = Setting.get_bool('admission_link_enabled', default=True)

    if not admission_enabled:
        return render(request, 'admission/disabled.html')

    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('admission_confirmation', pk=application.pk)
    else:
        form = AdmissionApplicationForm()

    return render(request, 'admission/application_form.html', {'form': form})


def admission_confirmation_view(request, pk):
    """Confirmation page after application submission"""
    application = get_object_or_404(AdmissionApplication, pk=pk)
    return render(request, 'admission/confirmation.html', {'application': application})


@login_required
def process_application_view(request, pk):
    """Process (approve/reject) an admission application"""
    # Only admission staff, registrars, and admins can process
    if request.user.role not in ['admission', 'registrar', 'admin']:
        messages.error(request, 'You do not have permission to process applications.')
        return redirect('dashboard')

    application = get_object_or_404(AdmissionApplication, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            # Approve and create user/student
            with transaction.atomic():
                # Generate username
                base_username = f"{application.first_name.lower()}.{application.last_name.lower()}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Generate random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=application.email,
                    password=password,
                    first_name=application.first_name,
                    last_name=application.last_name,
                    role='student'
                )

                # Get active curriculum for the program
                curriculum = application.program.curricula.filter(active=True).first()

                if not curriculum:
                    messages.error(request, 'No active curriculum found for the selected program.')
                    user.delete()
                    return redirect('admin:admission_admissionapplication_change', pk)

                # Create Student
                student = Student.objects.create(
                    user=user,
                    program=application.program,
                    curriculum=curriculum,
                    status='active'
                )

                # Auto-enroll freshman students
                if application.applicant_type == 'freshman':
                    auto_enroll_freshman(student)

                # Update application
                application.status = 'approved'
                application.processed_date = timezone.now()
                application.processed_by = request.user
                application.generated_user = user
                application.save()

                messages.success(
                    request,
                    f'Application approved! Username: {username}, Temporary Password: {password} '
                    f'(Please provide these credentials to the student)'
                )

        elif action == 'reject':
            application.status = 'rejected'
            application.processed_date = timezone.now()
            application.processed_by = request.user
            application.save()
            messages.success(request, 'Application rejected.')

        return redirect('admin:admission_admissionapplication_changelist')

    return render(request, 'admission/process_application.html', {'application': application})


def auto_enroll_freshman(student):
    """
    Auto-enroll freshman student in recommended subjects (up to 30 units)
    """
    # Get current active term
    active_term = Term.objects.filter(is_active=True).first()

    if not active_term:
        return

    # Get freshman unit cap from settings
    unit_cap = Setting.get_int('freshman_unit_cap', default=30)

    # Get recommended subjects for Year 1, Term 1
    recommended_subjects = CurriculumSubject.objects.filter(
        curriculum=student.curriculum,
        year_level=1,
        term_no=1,
        is_recommended=True
    ).select_related('subject').order_by('subject__code')

    total_units = 0
    enrolled_count = 0

    for curr_subject in recommended_subjects:
        subject = curr_subject.subject

        # Check if adding this subject would exceed unit cap
        if total_units + subject.units > unit_cap:
            continue

        # Find an open section for this subject
        section = Section.objects.filter(
            subject=subject,
            term=active_term,
            status='open'
        ).first()

        if section and not section.is_full:
            # Enroll student in this subject
            StudentSubject.objects.create(
                student=student,
                subject=subject,
                term=active_term,
                section=section,
                professor=section.professor,
                status='enrolled'
            )

            total_units += subject.units
            enrolled_count += 1

    return enrolled_count
