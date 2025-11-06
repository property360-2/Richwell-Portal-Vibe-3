"""
Test suite for the Richwell School Portal.

This includes tests for models, views, forms, services, and business logic.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from .models import (
    Program, Curriculum, Subject, Student, Term, Section,
    StudentSubject, Grade, Prerequisite, Setting
)
from .services import (
    EnrollmentService, GradeService, TermService, SectionService,
    AdmissionService, SettingsService, ReportService
)

User = get_user_model()


# Component rendering tests are skipped due to template complexity
# These tests would require full HTMX and Alpine.js integration
# Frontend components are manually tested through the application interface


class ModelTests(TestCase):
    """Tests for database models."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )

        self.student_user = User.objects.create_user(
            username='2024001',
            password='student123',
            first_name='John',
            last_name='Doe',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='prof001',
            password='prof123',
            first_name='Jane',
            last_name='Smith',
            role='professor'
        )

        # Create program and curriculum
        self.program = Program.objects.create(
            code='BSCS',
            name='Bachelor of Science in Computer Science',
            level='undergraduate',
            passing_grade=3.0
        )

        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='2024',
            effective_date=date(2024, 1, 1)
        )

        # Create student
        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum,
            year_level=1,
            status='active'
        )

        # Create term
        self.term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            add_drop_deadline=date(2024, 8, 15),
            is_active=True
        )

        # Create subject
        self.subject = Subject.objects.create(
            code='CS101',
            title='Introduction to Programming',
            units=3,
            lecture_hours=3,
            lab_hours=0
        )

        # Create section
        self.section = Section.objects.create(
            subject=self.subject,
            section_code='CS101-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40,
            status='open'
        )

    def test_user_creation(self):
        """Test user creation with roles."""
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertEqual(self.student_user.role, 'student')
        self.assertEqual(self.professor_user.role, 'professor')
        self.assertTrue(self.admin_user.is_admin())
        self.assertTrue(self.student_user.is_student())
        self.assertTrue(self.professor_user.is_professor())

    def test_program_creation(self):
        """Test program creation."""
        self.assertEqual(self.program.code, 'BSCS')
        self.assertEqual(self.program.name, 'Bachelor of Science in Computer Science')
        self.assertEqual(str(self.program), 'BSCS - Bachelor of Science in Computer Science')

    def test_student_is_freshman(self):
        """Test student is_freshman method."""
        self.assertTrue(self.student.is_freshman())
        self.student.year_level = 2
        self.assertFalse(self.student.is_freshman())

    def test_term_is_enrollment_open(self):
        """Test term enrollment status."""
        # Should be open if within add/drop deadline
        self.term.add_drop_deadline = timezone.now().date() + timedelta(days=5)
        self.term.save()
        self.assertTrue(self.term.is_enrollment_open())

        # Should be closed if past deadline
        self.term.add_drop_deadline = timezone.now().date() - timedelta(days=5)
        self.term.save()
        self.assertFalse(self.term.is_enrollment_open())

    def test_section_enrollment_count(self):
        """Test section enrollment count."""
        # Create enrollment
        StudentSubject.objects.create(
            student=self.student,
            subject=self.subject,
            section=self.section,
            term=self.term,
            status='enrolled'
        )

        self.assertEqual(self.section.studentsubject_set.count(), 1)

    def test_grade_is_passing(self):
        """Test grade passing status."""
        enrollment = StudentSubject.objects.create(
            student=self.student,
            subject=self.subject,
            section=self.section,
            term=self.term,
            status='enrolled'
        )

        grade = Grade.objects.create(
            student_subject=enrollment,
            subject=self.subject,
            professor=self.professor_user,
            numeric_grade=1.5,
            letter_grade='A',
            remarks='Excellent'
        )

        self.assertTrue(grade.is_passing())

        grade.numeric_grade = 5.0
        grade.letter_grade = 'F'
        grade.save()

        self.assertFalse(grade.is_passing())


class ViewTests(TestCase):
    """Tests for views and URL routing."""

    def setUp(self):
        """Set up test client and users."""
        self.client = Client()

        self.student_user = User.objects.create_user(
            username='student',
            password='student123',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='professor',
            password='prof123',
            role='professor'
        )

    def test_login_view_get(self):
        """Test login page loads."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')

    def test_login_redirect(self):
        """Test login redirects to appropriate dashboard."""
        response = self.client.post(reverse('login'), {
            'username': 'student',
            'password': 'student123'
        })
        # Should redirect after login
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_authentication(self):
        """Test dashboard requires login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_student_dashboard_access(self):
        """Test student can access student dashboard."""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_professor_dashboard_access(self):
        """Test professor can access professor dashboard."""
        self.client.login(username='professor', password='prof123')
        response = self.client.get(reverse('professor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Test logout functionality."""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class FormTests(TestCase):
    """Tests for forms and validation."""

    def setUp(self):
        """Set up test data for forms."""
        # Create necessary test data
        self.student_user = User.objects.create_user(
            username='2024001',
            password='test123',
            role='student'
        )

        self.program = Program.objects.create(
            code='BSCS',
            name='Bachelor of Science in Computer Science'
        )

        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='2024'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum,
            year_level=1
        )

        self.term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            is_active=True
        )

        self.subject = Subject.objects.create(
            code='CS101',
            title='Introduction to Programming',
            units=3
        )

        self.professor = User.objects.create_user(
            username='prof001',
            password='prof123',
            role='professor'
        )

        self.section = Section.objects.create(
            subject=self.subject,
            section_code='CS101-A',
            term=self.term,
            professor=self.professor,
            capacity=40,
            status='open'
        )

    def test_enrollment_form_validation(self):
        """Test enrollment form validation logic."""
        from .forms import EnrollmentForm

        form = EnrollmentForm(data={
            'section': self.section.id
        })

        # Form should be valid with proper data
        self.assertTrue(form.is_valid())


class IntegrationTests(TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        """Set up complete test environment."""
        # Create users
        self.student_user = User.objects.create_user(
            username='2024001',
            password='test123',
            first_name='John',
            last_name='Doe',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='prof001',
            password='prof123',
            first_name='Jane',
            last_name='Smith',
            role='professor'
        )

        # Create program structure
        self.program = Program.objects.create(
            code='BSCS',
            name='Bachelor of Science in Computer Science'
        )

        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='2024'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum,
            year_level=1
        )

        # Create term and courses
        self.term = Term.objects.create(
            name='1st Semester 2024-2025',
            start_date=date(2024, 8, 1),
            end_date=date(2024, 12, 15),
            add_drop_deadline=date(2024, 8, 15),
            is_active=True
        )

        self.subject = Subject.objects.create(
            code='CS101',
            title='Introduction to Programming',
            units=3
        )

        self.section = Section.objects.create(
            subject=self.subject,
            section_code='CS101-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40,
            status='open'
        )

        self.client = Client()

    def test_complete_enrollment_workflow(self):
        """Test complete student enrollment workflow."""
        # Login as student
        self.client.login(username='2024001', password='test123')

        # Access enrollment page
        response = self.client.get(reverse('enrollment'))
        self.assertEqual(response.status_code, 200)

        # Verify enrollment was created
        # Note: This would require implementing the enrollment creation logic
        # For now, we verify the page loads correctly

    def test_grade_submission_workflow(self):
        """Test professor grade submission workflow."""
        # Create enrollment first
        enrollment = StudentSubject.objects.create(
            student=self.student,
            subject=self.subject,
            section=self.section,
            term=self.term,
            status='enrolled'
        )

        # Login as professor
        self.client.login(username='prof001', password='prof123')

        # Access section students page
        response = self.client.get(
            reverse('section_students', args=[self.section.id])
        )
        self.assertEqual(response.status_code, 200)

        # Verify grade creation
        # Note: This would require implementing grade submission
        # For now, we verify the page loads correctly


class ServiceTests(TestCase):
    """Tests for service layer functionality."""

    def setUp(self):
        """Set up test data for service tests."""
        # Create users
        self.student_user = User.objects.create_user(
            username='2024001',
            password='test123',
            first_name='John',
            last_name='Doe',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='prof001',
            password='prof123',
            first_name='Jane',
            last_name='Smith',
            role='professor'
        )

        # Create program structure
        self.program = Program.objects.create(
            code='BSCS',
            name='Bachelor of Science in Computer Science',
            passing_grade=3.0
        )

        self.curriculum = Curriculum.objects.create(
            program=self.program,
            version='2024'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            program=self.program,
            curriculum=self.curriculum,
            year_level=1
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
            code='CS101',
            title='Programming 1',
            units=3
        )

        self.subject2 = Subject.objects.create(
            code='CS102',
            title='Data Structures',
            units=3
        )

        # Create prerequisite
        self.prerequisite = Prerequisite.objects.create(
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

        # Create system settings
        Setting.objects.create(key='enrollment_open', value='true')
        Setting.objects.create(key='freshman_unit_cap', value='30')
        Setting.objects.create(key='passing_grade', value='3.0')

    def test_enrollment_service_validate_enrollment(self):
        """Test enrollment validation in EnrollmentService."""
        # Should succeed for subject without prerequisite
        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, self.section1
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_enrollment_service_prerequisite_check(self):
        """Test prerequisite validation."""
        # Should fail for subject with unmet prerequisite
        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, self.section2
        )
        self.assertFalse(is_valid)
        self.assertIn('prerequisite', error_msg.lower())

    def test_enrollment_service_unit_cap(self):
        """Test freshman unit cap validation."""
        # Enroll in first subject (3 units)
        StudentSubject.objects.create(
            student=self.student,
            subject=self.subject1,
            section=self.section1,
            term=self.term,
            status='enrolled'
        )

        # Create many 3-unit subjects to exceed cap
        for i in range(10):
            subject = Subject.objects.create(
                code=f'CS20{i}',
                title=f'Test Subject {i}',
                units=3
            )
            section = Section.objects.create(
                subject=subject,
                section_code=f'CS20{i}-A',
                term=self.term,
                professor=self.professor_user,
                capacity=40,
                status='open'
            )
            StudentSubject.objects.create(
                student=self.student,
                subject=subject,
                section=section,
                term=self.term,
                status='enrolled'
            )

        # Total units should exceed 30, validation should fail
        new_subject = Subject.objects.create(
            code='CS999',
            title='Overflow Subject',
            units=3
        )
        new_section = Section.objects.create(
            subject=new_subject,
            section_code='CS999-A',
            term=self.term,
            professor=self.professor_user,
            capacity=40,
            status='open'
        )

        is_valid, error_msg = EnrollmentService.validate_enrollment(
            self.student, new_section
        )
        self.assertFalse(is_valid)
        self.assertIn('unit', error_msg.lower())

    def test_grade_service_calculate_gpa(self):
        """Test GPA calculation."""
        # Create enrollments and grades
        enrollment1 = StudentSubject.objects.create(
            student=self.student,
            subject=self.subject1,
            section=self.section1,
            term=self.term,
            status='completed'
        )

        Grade.objects.create(
            student_subject=enrollment1,
            subject=self.subject1,
            professor=self.professor_user,
            numeric_grade=1.5,
            letter_grade='A'
        )

        # GPA calculation
        gpa = GradeService.calculate_gpa(self.student)
        self.assertIsNotNone(gpa)
        self.assertAlmostEqual(gpa, 1.5, places=2)

    def test_grade_service_is_passing(self):
        """Test passing grade validation."""
        self.assertTrue(GradeService.is_passing(1.0))
        self.assertTrue(GradeService.is_passing(2.5))
        self.assertTrue(GradeService.is_passing(3.0))
        self.assertFalse(GradeService.is_passing(4.0))
        self.assertFalse(GradeService.is_passing(5.0))

    def test_term_service_get_active_term(self):
        """Test retrieving active term."""
        active_term = TermService.get_active_term()
        self.assertIsNotNone(active_term)
        self.assertEqual(active_term.id, self.term.id)

    def test_term_service_activate_term(self):
        """Test term activation (should deactivate others)."""
        # Create another term
        new_term = Term.objects.create(
            name='2nd Semester 2024-2025',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 5, 15),
            is_active=False
        )

        # Activate new term
        TermService.activate_term(new_term.id)

        # Refresh from database
        self.term.refresh_from_db()
        new_term.refresh_from_db()

        # Old term should be inactive
        self.assertFalse(self.term.is_active)
        # New term should be active
        self.assertTrue(new_term.is_active)

    def test_section_service_get_availability(self):
        """Test section availability calculation."""
        availability = SectionService.get_section_availability(self.section1)
        self.assertEqual(availability['capacity'], 40)
        self.assertEqual(availability['enrolled'], 0)
        self.assertEqual(availability['available'], 40)

        # Add enrollment
        StudentSubject.objects.create(
            student=self.student,
            subject=self.subject1,
            section=self.section1,
            term=self.term,
            status='enrolled'
        )

        availability = SectionService.get_section_availability(self.section1)
        self.assertEqual(availability['enrolled'], 1)
        self.assertEqual(availability['available'], 39)

    def test_settings_service_get_setting(self):
        """Test retrieving system settings."""
        value = SettingsService.get_setting('enrollment_open')
        self.assertEqual(value, 'true')

        value = SettingsService.get_setting('nonexistent', default='default_value')
        self.assertEqual(value, 'default_value')

    def test_settings_service_is_enrollment_open(self):
        """Test enrollment status check."""
        self.assertTrue(SettingsService.is_enrollment_open())

        # Change setting
        setting = Setting.objects.get(key='enrollment_open')
        setting.value = 'false'
        setting.save()

        self.assertFalse(SettingsService.is_enrollment_open())


class DecoratorTests(TestCase):
    """Tests for custom decorators."""

    def setUp(self):
        """Set up test users."""
        self.student_user = User.objects.create_user(
            username='student',
            password='test123',
            role='student'
        )

        self.professor_user = User.objects.create_user(
            username='professor',
            password='test123',
            role='professor'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            password='test123',
            role='admin'
        )

        self.client = Client()

    def test_student_required_decorator(self):
        """Test student_required decorator."""
        # Student should be able to access student dashboard
        self.client.login(username='student', password='test123')

        # Create student record for the user
        program = Program.objects.create(code='BSCS', name='Computer Science')
        curriculum = Curriculum.objects.create(program=program, version='2024')
        Student.objects.create(
            user=self.student_user,
            program=program,
            curriculum=curriculum,
            year_level=1
        )

        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_professor_required_decorator(self):
        """Test professor_required decorator."""
        # Professor should be able to access professor dashboard
        self.client.login(username='professor', password='test123')
        response = self.client.get(reverse('professor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_role_based_access_denial(self):
        """Test that users cannot access wrong role dashboards."""
        # Student trying to access professor dashboard
        self.client.login(username='student', password='test123')
        response = self.client.get(reverse('professor_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirected


# Run tests with: python manage.py test portal
