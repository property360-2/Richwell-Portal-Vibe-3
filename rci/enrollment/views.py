# rci/enrollment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.db import transaction
from django.http import HttpResponse
from .models import Student, Term, Section, StudentSubject
from academics.models import CurriculumSubject, Subject, Prereq
from settingsapp.models import Setting
from grades.models import Grade


@login_required
def enrollment_home_view(request):
    """Main enrollment page showing available subjects for student"""
    # Only students can access
    if request.user.role != 'student':
        messages.error(request, 'Only students can access enrollment.')
        return redirect('dashboard')

    # Check if enrollment is open
    enrollment_open = Setting.get_bool('enrollment_open', default=True)

    if not enrollment_open:
        return render(request, 'enrollment/enrollment_closed.html')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()

    if not active_term:
        messages.warning(request, 'No active enrollment term.')
        return render(request, 'enrollment/no_active_term.html')

    # Get currently enrolled subjects for this term
    enrolled_subjects = StudentSubject.objects.filter(
        student=student,
        term=active_term,
        status='enrolled'
    ).select_related('subject', 'section', 'professor')

    # Calculate current total units
    current_units = enrolled_subjects.aggregate(
        total=Sum('subject__units')
    )['total'] or 0

    # Get unit cap (30 for freshmen, could be different for others)
    unit_cap = Setting.get_int('freshman_unit_cap', default=30)

    # Get student's year level (estimate from total completed units)
    completed_units = StudentSubject.objects.filter(
        student=student,
        status='completed'
    ).aggregate(total=Sum('subject__units'))['total'] or 0

    # Estimate year level (rough calculation: 30 units per year)
    estimated_year = min((completed_units // 30) + 1, 4)

    # Get recommended subjects for this year level and term
    recommended_subjects = CurriculumSubject.objects.filter(
        curriculum=student.curriculum,
        year_level=estimated_year,
        term_no=1,  # Assuming current term is Term 1, could be dynamic
        is_recommended=True
    ).select_related('subject')

    # Get available sections for recommended subjects
    available_subjects = []
    for curr_subject in recommended_subjects:
        subject = curr_subject.subject

        # Check if already enrolled
        already_enrolled = enrolled_subjects.filter(subject=subject).exists()
        if already_enrolled:
            continue

        # Check if already completed
        already_completed = StudentSubject.objects.filter(
            student=student,
            subject=subject,
            status='completed'
        ).exists()
        if already_completed:
            continue

        # Check prerequisites
        prereqs_met, missing_prereqs = check_prerequisites(student, subject)

        # Get available sections
        sections = Section.objects.filter(
            subject=subject,
            term=active_term,
            status='open'
        ).select_related('professor')

        # Filter out full sections
        available_sections = [s for s in sections if not s.is_full]

        if available_sections:
            available_subjects.append({
                'subject': subject,
                'sections': available_sections,
                'prereqs_met': prereqs_met,
                'missing_prereqs': missing_prereqs,
                'recommended': True
            })

    # Get all other eligible subjects (not recommended but can be taken)
    all_subjects = Subject.objects.filter(
        program=student.program,
        active=True
    ).exclude(
        id__in=[es['subject'].id for es in available_subjects]
    ).exclude(
        id__in=enrolled_subjects.values_list('subject_id', flat=True)
    )

    other_subjects = []
    for subject in all_subjects:
        # Check if already completed
        already_completed = StudentSubject.objects.filter(
            student=student,
            subject=subject,
            status='completed'
        ).exists()
        if already_completed:
            continue

        # Check prerequisites
        prereqs_met, missing_prereqs = check_prerequisites(student, subject)

        # Get available sections
        sections = Section.objects.filter(
            subject=subject,
            term=active_term,
            status='open'
        ).select_related('professor')

        # Filter out full sections
        available_sections = [s for s in sections if not s.is_full]

        if available_sections:
            other_subjects.append({
                'subject': subject,
                'sections': available_sections,
                'prereqs_met': prereqs_met,
                'missing_prereqs': missing_prereqs,
                'recommended': False
            })

    context = {
        'student': student,
        'active_term': active_term,
        'enrolled_subjects': enrolled_subjects,
        'current_units': current_units,
        'unit_cap': unit_cap,
        'remaining_units': unit_cap - current_units,
        'available_subjects': available_subjects,
        'other_subjects': other_subjects,
        'estimated_year': estimated_year,
    }

    return render(request, 'enrollment/enrollment.html', context)


@login_required
def auto_enroll_view(request):
    """Automatically enroll student in recommended subjects"""
    if request.method != 'POST':
        return redirect('enrollment:home')

    # Only students can auto-enroll
    if request.user.role != 'student':
        messages.error(request, 'Only students can use auto-enrollment.')
        return redirect('dashboard')

    # Check if enrollment is open
    enrollment_open = Setting.get_bool('enrollment_open', default=True)
    if not enrollment_open:
        messages.error(request, 'Enrollment is currently closed.')
        return redirect('enrollment:home')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()
    if not active_term:
        messages.error(request, 'No active enrollment term.')
        return redirect('enrollment:home')

    # Get unit cap
    unit_cap = Setting.get_int('freshman_unit_cap', default=30)

    # Calculate current enrolled units
    current_units = StudentSubject.objects.filter(
        student=student,
        term=active_term,
        status='enrolled'
    ).aggregate(total=Sum('subject__units'))['total'] or 0

    # Get student's year level
    completed_units = StudentSubject.objects.filter(
        student=student,
        status='completed'
    ).aggregate(total=Sum('subject__units'))['total'] or 0
    estimated_year = min((completed_units // 30) + 1, 4)

    # Determine current semester (you can make this dynamic based on term name/dates)
    # For now, assuming semester 1
    current_semester = 1
    if 'second' in active_term.name.lower() or '2nd' in active_term.name.lower():
        current_semester = 2

    # Get recommended subjects for this year and semester
    recommended_subjects = CurriculumSubject.objects.filter(
        curriculum=student.curriculum,
        year_level=estimated_year,
        term_no=current_semester,
        is_recommended=True
    ).select_related('subject').order_by('subject__code')

    enrolled_count = 0
    skipped_subjects = []
    enrolled_subjects = []

    with transaction.atomic():
        for curr_subject in recommended_subjects:
            subject = curr_subject.subject

            # Check if would exceed unit cap
            if current_units + subject.units > unit_cap:
                skipped_subjects.append({
                    'subject': subject,
                    'reason': f'Would exceed unit cap ({unit_cap} units)'
                })
                continue

            # Check if already enrolled
            already_enrolled = StudentSubject.objects.filter(
                student=student,
                subject=subject,
                term=active_term,
                status='enrolled'
            ).exists()
            if already_enrolled:
                continue

            # Check if already completed
            already_completed = StudentSubject.objects.filter(
                student=student,
                subject=subject,
                status='completed'
            ).exists()
            if already_completed:
                continue

            # Check prerequisites
            prereqs_met, missing_prereqs = check_prerequisites(student, subject)
            if not prereqs_met:
                prereq_names = ', '.join([p.code for p in missing_prereqs])
                skipped_subjects.append({
                    'subject': subject,
                    'reason': f'Missing prerequisites: {prereq_names}'
                })
                continue

            # Get first available section with capacity
            available_section = Section.objects.filter(
                subject=subject,
                term=active_term,
                status='open'
            ).select_related('professor').first()

            if not available_section:
                skipped_subjects.append({
                    'subject': subject,
                    'reason': 'No available sections'
                })
                continue

            if available_section.is_full:
                skipped_subjects.append({
                    'subject': subject,
                    'reason': 'All sections are full'
                })
                continue

            # Enroll the student
            StudentSubject.objects.create(
                student=student,
                subject=subject,
                term=active_term,
                section=available_section,
                professor=available_section.professor,
                status='enrolled'
            )

            enrolled_subjects.append({
                'subject': subject,
                'section': available_section
            })
            current_units += subject.units
            enrolled_count += 1

    # Show success messages
    if enrolled_count > 0:
        enrolled_list = ', '.join([f"{e['subject'].code}" for e in enrolled_subjects])
        messages.success(
            request,
            f'Successfully auto-enrolled in {enrolled_count} subject(s): {enrolled_list}'
        )

    if skipped_subjects:
        for skipped in skipped_subjects:
            messages.warning(
                request,
                f'Skipped {skipped["subject"].code}: {skipped["reason"]}'
            )

    if enrolled_count == 0 and not skipped_subjects:
        messages.info(request, 'No recommended subjects available for auto-enrollment.')

    return redirect('enrollment:home')


@login_required
def enroll_subject_view(request, section_id):
    """Enroll student in a subject section"""
    if request.method != 'POST':
        return redirect('enrollment:home')

    # Only students can enroll
    if request.user.role != 'student':
        messages.error(request, 'Only students can enroll in subjects.')
        return redirect('dashboard')

    # Check if enrollment is open
    enrollment_open = Setting.get_bool('enrollment_open', default=True)
    if not enrollment_open:
        messages.error(request, 'Enrollment is currently closed.')
        return redirect('enrollment:home')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get section
    section = get_object_or_404(Section, id=section_id)
    subject = section.subject
    term = section.term

    # Validation 1: Check if term is active
    if not term.is_active:
        messages.error(request, 'Cannot enroll in inactive term.')
        return redirect('enrollment:home')

    # Validation 2: Check if section is open and has capacity
    if section.status != 'open':
        messages.error(request, f'{subject.code} - Section {section.section_code} is not open for enrollment.')
        return redirect('enrollment:home')

    if section.is_full:
        messages.error(request, f'{subject.code} - Section {section.section_code} is full.')
        return redirect('enrollment:home')

    # Validation 3: Check if already enrolled in this subject for this term
    already_enrolled = StudentSubject.objects.filter(
        student=student,
        subject=subject,
        term=term,
        status='enrolled'
    ).exists()

    if already_enrolled:
        messages.warning(request, f'You are already enrolled in {subject.code} - {subject.title}.')
        return redirect('enrollment:home')

    # Validation 4: Check if already completed
    already_completed = StudentSubject.objects.filter(
        student=student,
        subject=subject,
        status='completed'
    ).exists()

    if already_completed:
        messages.warning(request, f'You have already completed {subject.code} - {subject.title}.')
        return redirect('enrollment:home')

    # Validation 5: Check prerequisites
    prereqs_met, missing_prereqs = check_prerequisites(student, subject)
    if not prereqs_met:
        prereq_names = ', '.join([p.title for p in missing_prereqs])
        messages.error(
            request,
            f'Cannot enroll in {subject.code}. Missing prerequisites: {prereq_names}'
        )
        return redirect('enrollment:home')

    # Validation 6: Check unit limit
    current_units = StudentSubject.objects.filter(
        student=student,
        term=term,
        status='enrolled'
    ).aggregate(total=Sum('subject__units'))['total'] or 0

    unit_cap = Setting.get_int('freshman_unit_cap', default=30)

    if current_units + subject.units > unit_cap:
        messages.error(
            request,
            f'Cannot enroll. This would exceed your unit limit of {unit_cap} units. '
            f'Current: {current_units}, Adding: {subject.units}, Total would be: {current_units + subject.units}'
        )
        return redirect('enrollment:home')

    # All validations passed - enroll the student
    with transaction.atomic():
        StudentSubject.objects.create(
            student=student,
            subject=subject,
            term=term,
            section=section,
            professor=section.professor,
            status='enrolled'
        )

        messages.success(
            request,
            f'Successfully enrolled in {subject.code} - {subject.title} '
            f'(Section {section.section_code}, {subject.units} units)'
        )

    return redirect('enrollment:home')


@login_required
def drop_subject_view(request, enrollment_id):
    """Drop an enrolled subject"""
    if request.method != 'POST':
        return redirect('enrollment:home')

    # Only students can drop
    if request.user.role != 'student':
        messages.error(request, 'Only students can drop subjects.')
        return redirect('dashboard')

    # Check if enrollment is open
    enrollment_open = Setting.get_bool('enrollment_open', default=True)
    if not enrollment_open:
        messages.error(request, 'Enrollment is currently closed. Cannot drop subjects.')
        return redirect('enrollment:home')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get enrollment
    enrollment = get_object_or_404(StudentSubject, id=enrollment_id, student=student)

    # Check if term is still active
    if not enrollment.term.is_active:
        messages.error(request, 'Cannot drop subjects from inactive term.')
        return redirect('enrollment:home')

    # Check if still within add/drop period
    from django.utils import timezone
    if timezone.now().date() > enrollment.term.add_drop_deadline:
        messages.error(
            request,
            f'Add/drop deadline has passed ({enrollment.term.add_drop_deadline}). '
            f'Cannot drop subjects.'
        )
        return redirect('enrollment:home')

    # Drop the subject
    subject_code = enrollment.subject.code
    subject_title = enrollment.subject.title
    units = enrollment.subject.units

    enrollment.delete()

    messages.success(
        request,
        f'Successfully dropped {subject_code} - {subject_title} ({units} units)'
    )

    return redirect('enrollment:home')


@login_required
def cor_view(request):
    """Generate Certificate of Registration (COR)"""
    # Only students can view COR
    if request.user.role != 'student':
        messages.error(request, 'Only students can view Certificate of Registration.')
        return redirect('dashboard')

    # Get student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Get active term
    active_term = Term.objects.filter(is_active=True).first()

    if not active_term:
        messages.warning(request, 'No active enrollment term.')
        return redirect('dashboard')

    # Get enrolled subjects for this term
    enrolled_subjects = StudentSubject.objects.filter(
        student=student,
        term=active_term,
        status='enrolled'
    ).select_related('subject', 'section', 'professor').order_by('subject__code')

    # Calculate total units
    total_units = enrolled_subjects.aggregate(
        total=Sum('subject__units')
    )['total'] or 0

    context = {
        'student': student,
        'term': active_term,
        'enrolled_subjects': enrolled_subjects,
        'total_units': total_units,
    }

    return render(request, 'enrollment/cor.html', context)


# Helper functions

def check_prerequisites(student, subject):
    """
    Check if student has met all prerequisites for a subject.
    Returns (met: bool, missing_prereqs: list)
    """
    # Get all prerequisites for this subject
    prereqs = Prereq.objects.filter(subject=subject).select_related('prereq_subject')

    if not prereqs.exists():
        return True, []

    missing_prereqs = []

    for prereq in prereqs:
        prereq_subject = prereq.prereq_subject

        # Check if student has completed this prerequisite
        completed = StudentSubject.objects.filter(
            student=student,
            subject=prereq_subject,
            status='completed'
        ).exists()

        # Also check if student has a passing grade
        if completed:
            # Check grade
            student_subject = StudentSubject.objects.filter(
                student=student,
                subject=prereq_subject,
                status='completed'
            ).first()

            if student_subject:
                grade = Grade.objects.filter(student_subject=student_subject).first()
                if grade and not grade.is_passing:
                    completed = False

        if not completed:
            missing_prereqs.append(prereq_subject)

    return len(missing_prereqs) == 0, missing_prereqs
