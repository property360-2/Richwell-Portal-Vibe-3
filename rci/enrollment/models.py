# rci/enrollment/models.py
from django.db import models
from django.conf import settings
from academics.models import Program, Curriculum, Subject


class Student(models.Model):
    """Student info, linked to users, program, and curriculum"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='students')
    curriculum = models.ForeignKey(Curriculum, on_delete=models.PROTECT, related_name='students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    documents_json = models.JSONField(default=dict, blank=True, help_text='{"tor":"tor.pdf","id":"id.png"}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.program.name}"


class Term(models.Model):
    """Defines semesters/trimesters per academic year"""
    name = models.CharField(max_length=50, help_text="e.g. '1st Semester AY 2025-2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    add_drop_deadline = models.DateField(null=True, blank=True)
    grade_encoding_deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'terms'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Section(models.Model):
    """Each subject offering per term (tied to a professor)"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('closed', 'Closed'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sections')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='sections')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sections',
        limit_choices_to={'role': 'professor'}
    )
    section_code = models.CharField(max_length=20, help_text="e.g. 'CS101-A'")
    capacity = models.IntegerField(default=40)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        unique_together = ['subject', 'term', 'section_code']
        ordering = ['section_code']

    def __str__(self):
        return f"{self.section_code} - {self.subject.code} ({self.term.name})"

    @property
    def enrolled_count(self):
        """Returns the number of students enrolled in this section"""
        return self.student_subjects.count()

    @property
    def is_full(self):
        """Check if section is at capacity"""
        return self.enrolled_count >= self.capacity


class StudentSubject(models.Model):
    """Student's enrolled subjects per term + section"""
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('inc', 'Incomplete'),
        ('repeat_required', 'Repeat Required'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_enrollments')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='student_subjects')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='student_subjects')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='student_subjects'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_subjects'
        ordering = ['-created_at']
        unique_together = ['student', 'subject', 'term']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.code} ({self.term.name})"
