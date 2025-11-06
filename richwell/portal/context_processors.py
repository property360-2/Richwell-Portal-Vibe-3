"""
Context processors to make data available globally in templates
"""

from .models import Term, Setting


def active_term(request):
    """
    Add active term to template context
    """
    term = Term.objects.filter(is_active=True).first()
    return {
        'active_term': term
    }


def user_role(request):
    """
    Add user role information to template context
    """
    if request.user.is_authenticated:
        return {
            'is_student': request.user.is_student(),
            'is_professor': request.user.is_professor(),
            'is_registrar': request.user.is_registrar(),
            'is_dean': request.user.is_dean(),
            'is_admission_staff': request.user.is_admission_staff(),
            'is_admin': request.user.is_admin_user(),
            'user_role': request.user.role,
            'user_full_name': request.user.get_full_name() or request.user.username
        }
    return {
        'is_student': False,
        'is_professor': False,
        'is_registrar': False,
        'is_dean': False,
        'is_admission_staff': False,
        'is_admin': False,
        'user_role': None,
        'user_full_name': ''
    }


def system_settings(request):
    """
    Add commonly used system settings to template context
    """
    return {
        'enrollment_open': Setting.get_bool('enrollment_open', False),
        'admission_link_enabled': Setting.get_bool('admission_link_enabled', False),
        'system_name': Setting.get_value('system_name', 'Richwell School Portal'),
        'timezone': Setting.get_value('timezone', 'Asia/Manila'),
    }


def navigation_counts(request):
    """
    Add navigation badge counts to template context
    (e.g., pending approvals, ungraded assignments)
    """
    counts = {}

    if request.user.is_authenticated:
        if request.user.is_professor():
            # Count sections with ungraded students
            from .models import Section, StudentSubject, Grade
            from django.db.models import Count, Q

            active_term = Term.objects.filter(is_active=True).first()
            if active_term:
                sections = Section.objects.filter(
                    professor=request.user,
                    term=active_term
                )

                ungraded_count = 0
                for section in sections:
                    enrollments = StudentSubject.objects.filter(section=section)
                    for enrollment in enrollments:
                        if not Grade.objects.filter(student_subject=enrollment).exists():
                            ungraded_count += 1

                counts['ungraded_students'] = ungraded_count

        elif request.user.is_registrar():
            # Count open sections
            from .models import Section

            active_term = Term.objects.filter(is_active=True).first()
            if active_term:
                counts['open_sections'] = Section.objects.filter(
                    term=active_term,
                    status='open'
                ).count()

        elif request.user.is_dean():
            # Count INC grades
            from .models import Grade

            counts['inc_grades'] = Grade.objects.filter(grade='INC').count()

    return {
        'nav_counts': counts
    }


def enrollment_status(request):
    """
    Add enrollment status information for students
    """
    if request.user.is_authenticated and request.user.is_student():
        from .models import Student, StudentSubject
        from decimal import Decimal

        try:
            student = Student.objects.get(user=request.user)
            active_term = Term.objects.filter(is_active=True).first()

            if active_term:
                # Get current enrollments
                current_enrollments = StudentSubject.objects.filter(
                    student=student,
                    term=active_term
                )

                # Calculate units
                total_units = sum(e.subject.units for e in current_enrollments)

                # Get freshman max units
                max_units = Setting.get_int('freshman_max_units', 15) if student.is_freshman() else 30

                return {
                    'student_profile': student,
                    'enrolled_units': total_units,
                    'max_units': max_units,
                    'can_enroll_more': total_units < max_units,
                    'enrollment_count': current_enrollments.count()
                }
        except Student.DoesNotExist:
            pass

    return {
        'student_profile': None,
        'enrolled_units': 0,
        'max_units': 0,
        'can_enroll_more': False,
        'enrollment_count': 0
    }
