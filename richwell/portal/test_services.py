"""
Comprehensive tests for the service layer.
Focus on business logic validation.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Program, Curriculum, Subject, Student, Term, Section,
    StudentSubject, Grade, Prerequisite, Setting
)
from .services import (
    EnrollmentService, GradeService, TermService, SectionService,
    AdmissionService, SettingsService, ReportService
)

User = get_user_model()


class EnrollmentServiceTests(TestCase):
    """Tests for EnrollmentService business logic."""

    def setUp(self):
        """Set up test data."""
        # Create program
        self.program = Program.objects.create(
            name='BS Computer Science',
            level='Bachelor'
        )

        # Create curriculum
        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='CHED 2023',
            effective_sy='AY 2023-2024'
        )

        # Create users
        self.student_user = User.objects.create_user(
            username='student001',
            password='test123',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='prof001',
            password='test123',
            role='professor'
        )

        # Create student
        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum
        )

        # Create term
        self.term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            add_drop_deadline=timezone.now().date() + timedelta(days=5),
            is_active=True
        )

        # Create subjects
        self.subject1 = Subject.objects.create(
            program=self.program,
            code='CS101',
            title='Programming 1',
            units=3,
            type='major',
            recommended_year=1,
            recommended_semester=1
        )

        self.subject2 = Subject.objects.create(
            program=self.program,
            code='CS102',
            title='Data Structures',
            units=3,
            type='major',
            recommended_year=1,
            recommended_semester=2
        )

        # Create prerequisite
        Prerequisite.objects.create(
            subject=self.subject2,
            prerequisite_subject=self.subject1
        )

        # Create sections
        self.section1 = Section.objects.create(
            subject=self.subject1,
            section_code='CS101-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40,
            status='open'
        )

        self.section2 = Section.objects.create(
            subject=self.subject2,
            section_code='CS102-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40,
            status='open'
        )

        # Create settings
        Setting.objects.create(key_name='enrollment_open', value_text='true')
        Setting.objects.create(key_name='freshman_unit_cap', value_text='30')
        Setting.objects.create(key='passing_grade', value='3.0')

    def test_validate_enrollment_success(self):
        """Test successful enrollment validation."""
        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, self.section1
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_enrollment_prerequisite_fail(self):
        """Test enrollment fails when prerequisite not met."""
        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, self.section2
        )
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIn('prerequisite', error_msg.lower())

    def test_validate_enrollment_capacity_full(self):
        """Test enrollment fails when section is full."""
        # Fill up the section
        self.section1.status = 'full'
        self.section1.save()

        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, self.section1
        )
        self.assertFalse(is_valid)
        self.assertIn('full', error_msg.lower())


class GradeServiceTests(TestCase):
    """Tests for GradeService business logic."""

    def setUp(self):
        """Set up test data."""
        # Create program
        self.program = Program.objects.create(
            name='BS Computer Science',
            level='Bachelor'
        )

        # Create curriculum
        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='CHED 2023',
            effective_sy='AY 2023-2024'
        )

        # Create users
        self.student_user = User.objects.create_user(
            username='student001',
            password='test123',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='prof001',
            password='test123',
            role='professor'
        )

        # Create student
        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum
        )

        # Create term
        self.term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            is_active=True
        )

        # Create subject
        self.subject = Subject.objects.create(
            program=self.program,
            code='CS101',
            title='Programming 1',
            units=3,
            type='major',
            recommended_year=1,
            recommended_semester=1
        )

        # Create section
        self.section = Section.objects.create(
            subject=self.subject,
            section_code='CS101-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40
        )

        # Create enrollment
        self.enrollment = StudentSubject.objects.create(
            student=self.student,
            subject=self.subject,
            section=self.section,
            term=self.term,
            status='enrolled'
        )

    def test_is_passing_grade(self):
        """Test passing grade validation."""
        self.assertTrue(GradeService.is_passing(1.0))
        self.assertTrue(GradeService.is_passing(2.5))
        self.assertTrue(GradeService.is_passing(3.0))
        self.assertFalse(GradeService.is_passing(4.0))
        self.assertFalse(GradeService.is_passing(5.0))

    def test_calculate_gpa(self):
        """Test GPA calculation."""
        # Create a grade
        Grade.objects.create(
            student_subject=self.enrollment,
            subject=self.subject,
            professor=self.professor_user,
            numeric_grade=1.5,
            letter_grade='A'
        )

        # Update enrollment status
        self.enrollment.status = 'completed'
        self.enrollment.save()

        gpa = GradeService.calculate_gpa(self.student)
        self.assertIsNotNone(gpa)
        self.assertAlmostEqual(float(gpa), 1.5, places=2)


class TermServiceTests(TestCase):
    """Tests for TermService business logic."""

    def setUp(self):
        """Set up test data."""
        self.term1 = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            is_active=True
        )

    def test_get_active_term(self):
        """Test retrieving active term."""
        active_term = TermService.get_active_term()
        self.assertIsNotNone(active_term)
        self.assertEqual(active_term.id, self.term1.id)

    def test_activate_term_deactivates_others(self):
        """Test that activating a term deactivates all others."""
        # Create second term
        term2 = Term.objects.create(
            name='2nd Semester 2024-2025',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 5, 15),
            is_active=False
        )

        # Activate the second term
        TermService.activate_term(term2.id)

        # Refresh from DB
        self.term1.refresh_from_db()
        term2.refresh_from_db()

        # Check results
        self.assertFalse(self.term1.is_active)
        self.assertTrue(term2.is_active)


class SectionServiceTests(TestCase):
    """Tests for SectionService business logic."""

    def setUp(self):
        """Set up test data."""
        # Create program
        program = Program.objects.create(
            name='BS Computer Science',
            level='Bachelor'
        )

        # Create curriculum
        curriculum = Curriculum.objects.create(
            program=program,
            version='CHED 2023',
            effective_sy='AY 2023-2024'
        )

        # Create student user and student
        student_user = User.objects.create_user(
            username='student001',
            password='test123',
            role='student'
        )

        self.student = Student.objects.create(
            user=student_user,
            program=program,
            curriculum=curriculum,
            year_level=1
        )

        # Create professor
        professor_user = User.objects.create_user(
            username='prof001',
            password='test123',
            role='professor'
        )

        # Create term
        term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            is_active=True
        )

        # Create subject
        subject = Subject.objects.create(
            program=program,
            code='CS101',
            title='Programming 1',
            units=3,
            type='major',
            recommended_year=1,
            recommended_semester=1
        )

        # Create section
        self.section = Section.objects.create(
            subject=subject,
            section_code='CS101-A',
            term=term,
            professor=professor_user,
            capacity=40,
            status='open'
        )

    def test_section_availability_empty(self):
        """Test section availability with no enrollments."""
        availability = SectionService.get_section_availability(self.section)
        self.assertEqual(availability['capacity'], 40)
        self.assertEqual(availability['enrolled'], 0)
        self.assertEqual(availability['available'], 40)

    def test_section_availability_with_enrollments(self):
        """Test section availability with enrollments."""
        # Add an enrollment
        StudentSubject.objects.create(
            student=self.student,
            subject=self.section.subject,
            section=self.section,
            term=self.section.term,
            status='enrolled'
        )

        availability = SectionService.get_section_availability(self.section)
        self.assertEqual(availability['enrolled'], 1)
        self.assertEqual(availability['available'], 39)


class SettingsServiceTests(TestCase):
    """Tests for SettingsService business logic."""

    def setUp(self):
        """Set up test data."""
        Setting.objects.create(key_name='enrollment_open', value_text='true')
        Setting.objects.create(key_name='freshman_unit_cap', value_text='30')

    def test_get_setting_existing(self):
        """Test retrieving existing setting."""
        value = SettingsService.get_setting('enrollment_open')
        self.assertEqual(value, 'true')

    def test_get_setting_nonexistent(self):
        """Test retrieving nonexistent setting with default."""
        value = SettingsService.get_setting('nonexistent_key', default='default_val')
        self.assertEqual(value, 'default_val')

    def test_is_enrollment_open_true(self):
        """Test enrollment open check when true."""
        self.assertTrue(SettingsService.is_enrollment_open())

    def test_is_enrollment_open_false(self):
        """Test enrollment open check when false."""
        setting = Setting.objects.get(key_name='enrollment_open')
        setting.value_text = 'false'
        setting.save()

        self.assertFalse(SettingsService.is_enrollment_open())


# Run with: python manage.py test portal.test_services
