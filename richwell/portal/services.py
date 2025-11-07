"""
Business Logic Services for Richwell Portal

This module contains service classes that encapsulate business logic,
separating it from views for better maintainability and testability.
"""

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from .models import (
    Student, StudentSubject, Subject, Section, Term, Grade,
    Prerequisite, Setting, AuditTrail, Curriculum, CurriculumSubject
)


class EnrollmentService:
    """
    Service for handling student enrollment logic
    """

    @staticmethod
    def can_enroll_in_subject(student: Student, subject: Subject, term: Term) -> Tuple[bool, str]:
        """
        Check if a student can enroll in a subject
        Returns (can_enroll, reason)
        """
        # Check if already enrolled
        if StudentSubject.objects.filter(student=student, subject=subject, term=term).exists():
            return False, f"Already enrolled in {subject.code}"

        # Check prerequisites
        prerequisites = Prerequisite.objects.filter(subject=subject).select_related('prereq_subject')
        for prereq in prerequisites:
            has_passed = Grade.objects.filter(
                student_subject__student=student,
                subject=prereq.prereq_subject,
                grade__in=['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']
            ).exists()

            if not has_passed:
                return False, f"Prerequisite not met: {prereq.prereq_subject.code}"

        # Check unit cap for freshmen
        if student.is_freshman():
            max_units = Setting.get_int('freshman_max_units', 15)
            current_units = EnrollmentService.get_enrolled_units(student, term)

            if current_units + subject.units > max_units:
                return False, f"Unit limit exceeded. Maximum {max_units} units allowed."

        return True, "OK"

    @staticmethod
    def get_enrolled_units(student: Student, term: Term) -> Decimal:
        """
        Get total units enrolled by student in a term
        """
        from django.db.models import Sum
        result = StudentSubject.objects.filter(
            student=student,
            term=term,
            status__in=['enrolled', 'completed']
        ).aggregate(total=Sum('subject__units'))
        return result['total'] or Decimal('0.0')

    @staticmethod
    def get_recommended_subjects(student: Student, term: Term) -> List[Subject]:
        """
        Get recommended subjects for a student based on curriculum
        """
        if not student.curriculum:
            return []

        # Get student's current year level (estimate based on completed subjects)
        completed_count = StudentSubject.objects.filter(
            student=student,
            status='completed'
        ).count()

        # Rough estimate: 8 subjects per year
        estimated_year = min((completed_count // 8) + 1, 6)

        # Get curriculum subjects for estimated year
        curriculum_subjects = CurriculumSubject.objects.filter(
            curriculum=student.curriculum,
            year_level=estimated_year,
            is_recommended=True
        ).select_related('subject')

        # Filter to subjects not yet taken
        taken_subject_ids = StudentSubject.objects.filter(
            student=student
        ).values_list('subject_id', flat=True)

        recommended = []
        for cs in curriculum_subjects:
            if cs.subject.id not in taken_subject_ids:
                can_enroll, _ = EnrollmentService.can_enroll_in_subject(
                    student, cs.subject, term
                )
                if can_enroll:
                    recommended.append(cs.subject)

        return recommended

    @staticmethod
    def validate_enrollment(student: Student, section: Section) -> Tuple[bool, Optional[str]]:
        """
        Validate if a student can enroll in a section
        Returns (is_valid, error_message)
        """
        # Check subject prerequisites
        can_enroll, reason = EnrollmentService.can_enroll_in_subject(
            student, section.subject, section.term
        )
        if not can_enroll:
            return False, reason

        # Check section capacity
        if section.status == 'full' or section.is_full():
            return False, f"Section {section.section_code} is full"

        return True, None

    @staticmethod
    @transaction.atomic
    def enroll_student(student: Student, section: Section, term: Term, actor=None) -> StudentSubject:
        """
        Enroll a student in a section
        """
        # Validate enrollment
        is_valid, error_msg = EnrollmentService.validate_enrollment(student, section)
        if not is_valid:
            raise ValueError(error_msg)

        # Create enrollment
        enrollment = StudentSubject.objects.create(
            student=student,
            subject=section.subject,
            term=term,
            section=section,
            professor=section.professor,
            status='enrolled'
        )

        # Update section status
        section.update_status()

        # Log enrollment
        if actor:
            AuditTrail.objects.create(
                actor=actor,
                action='enroll_student',
                entity='StudentSubject',
                entity_id=enrollment.id,
                new_value_json={
                    'student': student.user.username,
                    'subject': section.subject.code,
                    'section': section.section_code
                }
            )

        return enrollment

    @staticmethod
    @transaction.atomic
    def drop_enrollment(enrollment: StudentSubject, actor=None) -> None:
        """
        Drop a student enrollment
        """
        section = enrollment.section
        subject_code = enrollment.subject.code

        # Log before deletion
        if actor:
            AuditTrail.objects.create(
                actor=actor,
                action='drop_enrollment',
                entity='StudentSubject',
                entity_id=enrollment.id,
                old_value_json={
                    'student': enrollment.student.user.username,
                    'subject': subject_code
                }
            )

        enrollment.delete()

        # Update section status
        if section:
            section.update_status()


class GradeService:
    """
    Service for handling grade-related logic
    """

    @staticmethod
    @transaction.atomic
    def post_grade(student_subject: StudentSubject, grade_value: str, professor, actor=None) -> Grade:
        """
        Post or update a grade for a student
        """
        # Validate grade value
        valid_grades = ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50',
                       '2.75', '3.00', '4.00', '5.00', 'INC', 'DRP', 'P']
        if grade_value not in valid_grades:
            raise ValueError(f"Invalid grade value: {grade_value}")

        # Get or create grade
        grade_obj, created = Grade.objects.get_or_create(
            student_subject=student_subject,
            defaults={
                'subject': student_subject.subject,
                'professor': professor,
                'grade': grade_value
            }
        )

        # If updating, log the change
        if not created:
            old_grade = grade_obj.grade
            grade_obj.grade = grade_value
            grade_obj.professor = professor
            grade_obj.save()

            if actor:
                AuditTrail.objects.create(
                    actor=actor,
                    action='update_grade',
                    entity='Grade',
                    entity_id=grade_obj.id,
                    old_value_json={'grade': old_grade},
                    new_value_json={'grade': grade_value}
                )

        # Update student subject status
        GradeService.update_enrollment_status(student_subject, grade_value)

        return grade_obj

    @staticmethod
    def update_enrollment_status(student_subject: StudentSubject, grade_value: str) -> None:
        """
        Update enrollment status based on grade
        """
        if grade_value in ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']:
            student_subject.status = 'completed'
        elif grade_value in ['5.00', 'DRP']:
            student_subject.status = 'failed'
        elif grade_value == 'INC':
            student_subject.status = 'inc'
        elif grade_value == '4.00':
            student_subject.status = 'repeat_required'

        student_subject.save()

    @staticmethod
    def is_passing(grade_value: float) -> bool:
        """
        Check if a numeric grade is passing (3.0 or below)
        """
        return grade_value <= 3.0

    @staticmethod
    def calculate_gpa(student: Student) -> Optional[Decimal]:
        """
        Calculate student's GPA based on all completed subjects
        """
        completed = StudentSubject.objects.filter(
            student=student,
            status='completed'
        ).select_related('subject')

        total_grade_points = Decimal('0.0')
        total_units = Decimal('0.0')

        for enrollment in completed:
            try:
                grade = Grade.objects.get(student_subject=enrollment)

                # Try numeric_grade first, then fall back to grade field
                if grade.numeric_grade is not None:
                    grade_value = Decimal(str(grade.numeric_grade))
                elif grade.grade:
                    if grade.grade in ['P', 'INC', 'DRP']:
                        continue
                    grade_value = Decimal(grade.grade)
                else:
                    continue

                total_grade_points += grade_value * enrollment.subject.units
                total_units += enrollment.subject.units
            except (Grade.DoesNotExist, ValueError, TypeError):
                continue

        if total_units > 0:
            return round(total_grade_points / total_units, 2)
        return None

    @staticmethod
    def check_inc_expiration(grade: Grade) -> Dict:
        """
        Check if an INC grade has expired
        Returns dict with expiration info
        """
        if grade.grade != 'INC':
            return {'is_inc': False}

        # Get deadline months
        deadline_months = grade.subject.get_inc_deadline_months()

        # Calculate expiration date
        posted_date = grade.posted_at.date()
        expiration_date = posted_date + timedelta(days=deadline_months * 30)

        # Calculate days remaining
        today = timezone.now().date()
        days_remaining = (expiration_date - today).days

        # Determine status
        if days_remaining < 0:
            status = 'expired'
        elif days_remaining <= 30:
            status = 'critical'
        else:
            status = 'active'

        return {
            'is_inc': True,
            'posted_date': posted_date,
            'expiration_date': expiration_date,
            'days_remaining': days_remaining,
            'deadline_months': deadline_months,
            'status': status
        }


class TermService:
    """
    Service for term management logic
    """

    @staticmethod
    @transaction.atomic
    def activate_term(term, actor=None) -> None:
        """
        Activate a term (deactivates all others)
        Args:
            term: Term object or term ID
            actor: User performing the action (optional)
        """
        # Handle both Term object and ID
        if isinstance(term, int):
            term = Term.objects.get(id=term)

        # Deactivate all other terms
        Term.objects.exclude(id=term.id).update(is_active=False)

        # Activate this term
        term.is_active = True
        term.save()

        # Log activation
        if actor:
            AuditTrail.objects.create(
                actor=actor,
                action='activate_term',
                entity='Term',
                entity_id=term.id,
                new_value_json={'name': term.name, 'is_active': True}
            )

    @staticmethod
    def get_active_term() -> Optional[Term]:
        """
        Get the currently active term
        """
        return Term.objects.filter(is_active=True).first()

    @staticmethod
    def is_enrollment_open(term: Term) -> bool:
        """
        Check if enrollment is open for a term
        """
        if not term.is_active:
            return False

        return term.is_enrollment_open()


class SectionService:
    """
    Service for section management logic
    """

    @staticmethod
    def get_enrollment_count(section: Section) -> int:
        """
        Get number of students enrolled in a section
        """
        return StudentSubject.objects.filter(section=section).count()

    @staticmethod
    def update_section_status(section: Section) -> None:
        """
        Update section status based on enrollment
        """
        section.update_status()

    @staticmethod
    def is_section_available(section: Section) -> bool:
        """
        Check if section is available for enrollment
        """
        return section.status == 'open' and not section.is_full()

    @staticmethod
    def get_section_availability(section: Section) -> Dict:
        """
        Get section availability information
        Returns dict with capacity, enrolled, and available counts
        """
        enrolled = SectionService.get_enrollment_count(section)
        return {
            'capacity': section.capacity,
            'enrolled': enrolled,
            'available': section.capacity - enrolled
        }


class AdmissionService:
    """
    Service for admission-related logic
    """

    @staticmethod
    @transaction.atomic
    def admit_student(user_data: Dict, student_data: Dict, actor=None) -> Student:
        """
        Admit a new student (create user and student profile)
        """
        from .models import User

        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data.get('email', ''),
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            role='student'
        )

        # Create student profile
        student = Student.objects.create(
            user=user,
            program=student_data['program'],
            curriculum=student_data['curriculum'],
            status=student_data.get('status', 'active')
        )

        # Log admission
        if actor:
            AuditTrail.objects.create(
                actor=actor,
                action='admit_student',
                entity='Student',
                entity_id=student.id,
                new_value_json={
                    'username': user.username,
                    'program': student.program.name,
                    'curriculum': student.curriculum.version
                }
            )

        return student


class SettingsService:
    """
    Service for system settings management
    """

    @staticmethod
    def get_setting(key: str, default=None):
        """
        Get a setting value
        """
        return Setting.get_value(key, default)

    @staticmethod
    def is_enrollment_open() -> bool:
        """
        Check if enrollment is currently open
        """
        value = SettingsService.get_setting('enrollment_open', 'false')
        return value.lower() == 'true'

    @staticmethod
    @transaction.atomic
    def update_setting(key: str, value: str, actor=None) -> Setting:
        """
        Update a setting value
        """
        setting, created = Setting.objects.get_or_create(
            key_name=key,
            defaults={'value_text': value}
        )

        if not created:
            old_value = setting.value_text
            setting.value_text = value
            if actor:
                setting.updated_by = actor
            setting.save()

            # Log update
            if actor:
                AuditTrail.objects.create(
                    actor=actor,
                    action='update_setting',
                    entity='Setting',
                    entity_id=setting.id,
                    old_value_json={'key': key, 'value': old_value},
                    new_value_json={'key': key, 'value': value}
                )

        return setting


class ReportService:
    """
    Service for generating reports and analytics
    """

    @staticmethod
    def get_enrollment_statistics(term: Term = None) -> Dict:
        """
        Get enrollment statistics for a term
        """
        if term is None:
            term = TermService.get_active_term()

        if not term:
            return {}

        from django.db.models import Count

        total_enrollments = StudentSubject.objects.filter(term=term).count()
        unique_students = StudentSubject.objects.filter(term=term).values('student').distinct().count()

        sections_stats = Section.objects.filter(term=term).annotate(
            enrolled=Count('studentsubject')
        ).aggregate(
            total_sections=Count('id'),
            open_sections=Count('id', filter=models.Q(status='open')),
            full_sections=Count('id', filter=models.Q(status='full'))
        )

        return {
            'term': term.name,
            'total_enrollments': total_enrollments,
            'unique_students': unique_students,
            'total_sections': sections_stats['total_sections'],
            'open_sections': sections_stats['open_sections'],
            'full_sections': sections_stats['full_sections']
        }

    @staticmethod
    def get_grade_distribution(term: Term = None, subject: Subject = None) -> Dict:
        """
        Get grade distribution statistics
        """
        grades = Grade.objects.all()

        if term:
            grades = grades.filter(student_subject__term=term)

        if subject:
            grades = grades.filter(subject=subject)

        from django.db.models import Count
        distribution = grades.values('grade').annotate(count=Count('id')).order_by('-count')

        passing_count = grades.filter(
            grade__in=['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']
        ).count()

        failing_count = grades.filter(grade__in=['5.00', 'DRP']).count()
        inc_count = grades.filter(grade='INC').count()

        total = grades.count()
        passing_rate = (passing_count / total * 100) if total > 0 else 0

        return {
            'distribution': list(distribution),
            'passing_count': passing_count,
            'failing_count': failing_count,
            'inc_count': inc_count,
            'total': total,
            'passing_rate': round(passing_rate, 2)
        }
