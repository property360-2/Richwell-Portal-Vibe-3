"""
Test suite for the Richwell School Portal.

This includes tests for models, views, forms, and atomic design components.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template import Template, Context
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Program, Curriculum, Subject, Student, Term, Section,
    StudentSubject, Grade, Prerequisite
)

User = get_user_model()


class ComponentRenderingTests(TestCase):
    """Tests for atomic design component rendering."""

    def test_button_atom_renders(self):
        """Test that button atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/button.html' with text='Click Me' type='primary' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Click Me', rendered)
        self.assertIn('bg-blue-600', rendered)

    def test_badge_atom_renders(self):
        """Test that badge atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/badge.html' with text='Active' type='success' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Active', rendered)
        self.assertIn('bg-green', rendered)

    def test_checkbox_atom_renders(self):
        """Test that checkbox atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/checkbox.html' with name='agree' label='I agree' checked=True %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('I agree', rendered)
        self.assertIn('type="checkbox"', rendered)
        self.assertIn('checked', rendered)

    def test_radio_atom_renders(self):
        """Test that radio atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/radio.html' with name='choice' id='choice_a' value='a' label='Option A' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Option A', rendered)
        self.assertIn('type="radio"', rendered)
        self.assertIn('value="a"', rendered)

    def test_toggle_atom_renders(self):
        """Test that toggle atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/toggle.html' with name='notifications' label='Enable' checked=True %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Enable', rendered)
        self.assertIn('x-data', rendered)  # Alpine.js component

    def test_input_atom_renders(self):
        """Test that input atom renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/atoms/input.html' with name='email' type='email' placeholder='Enter email' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('type="email"', rendered)
        self.assertIn('Enter email', rendered)

    def test_card_molecule_renders(self):
        """Test that card molecule renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/molecules/card.html' with title='Test Card' shadow='md' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Test Card', rendered)
        self.assertIn('shadow', rendered)

    def test_alert_molecule_renders(self):
        """Test that alert molecule renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/molecules/alert.html' with message='Success!' type='success' %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Success!', rendered)
        self.assertIn('x-data', rendered)  # Alpine.js component

    def test_form_field_molecule_renders(self):
        """Test that form field molecule renders correctly."""
        template = Template(
            "{% load static %}"
            "{% include 'components/molecules/form_field.html' with label='Email' name='email' type='email' required=True %}"
        )
        context = Context({})
        rendered = template.render(context)

        self.assertIn('Email', rendered)
        self.assertIn('required', rendered)


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


# Run tests with: python manage.py test portal
