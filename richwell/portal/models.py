from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


# ===========================
# 1. CUSTOM USER MODEL
# ===========================

class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Extends Django's AbstractUser to include role field.
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('registrar', 'Registrar'),
        ('dean', 'Dean'),
        ('admission', 'Admission'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text='User role determining system access and permissions'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_student(self):
        return self.role == 'student'

    def is_professor(self):
        return self.role == 'professor'

    def is_registrar(self):
        return self.role == 'registrar'

    def is_dean(self):
        return self.role == 'dean'

    def is_admission_staff(self):
        return self.role == 'admission'

    def is_admin_user(self):
        return self.role == 'admin'


# ===========================
# 2. PROGRAMS
# ===========================

class Program(models.Model):
    """
    Academic programs (BSCS, ABM, HUMSS, etc.)
    """
    LEVEL_CHOICES = [
        ('SHS', 'Senior High School'),
        ('College', 'College'),
        ('Bachelor', 'Bachelor'),
        ('Masteral', 'Masteral'),
    ]

    name = models.CharField(max_length=255, help_text='Program name (e.g., BSCS, ABM)')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    passing_grade = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=3.00,
        validators=[MinValueValidator(1.00), MaxValueValidator(5.00)],
        help_text='Minimum passing grade for this program'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'programs'
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


# ===========================
# 3. CURRICULA
# ===========================

class Curriculum(models.Model):
    """
    CHED/DepEd curriculum versions for programs.
    Supports curriculum versioning for CHED updates.
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='curricula'
    )
    version = models.CharField(
        max_length=50,
        help_text='e.g., "CHED 2021 Rev", "K-12 2016"'
    )
    effective_sy = models.CharField(
        max_length=20,
        help_text='Academic year when this curriculum takes effect (e.g., "AY 2021-2022")'
    )
    active = models.BooleanField(
        default=True,
        help_text='Only one curriculum per program should be active at a time'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curricula'
        verbose_name = 'Curriculum'
        verbose_name_plural = 'Curricula'
        ordering = ['-effective_sy']
        unique_together = ['program', 'version']

    def __str__(self):
        return f"{self.program.name} - {self.version} ({self.effective_sy})"


# ===========================
# 4. SUBJECTS
# ===========================

class Subject(models.Model):
    """
    Academic subjects with recommended year/semester and type (major/minor).
    """
    TYPE_CHOICES = [
        ('major', 'Major Subject'),
        ('minor', 'Minor Subject'),
    ]

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Subject code (e.g., "CS101", "MATH101")'
    )
    title = models.CharField(
        max_length=255,
        help_text='Subject title (e.g., "Introduction to Computing")'
    )
    description = models.TextField(blank=True, null=True)
    units = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)]
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='minor',
        help_text='Major subjects have 6-month INC deadline, Minor subjects have 1-year deadline'
    )
    recommended_year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text='Recommended year level (1-6)'
    )
    recommended_sem = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text='Recommended semester (1=1st sem, 2=2nd sem, 3=Summer)'
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"

    def get_inc_deadline_months(self):
        """Returns INC deadline in months based on subject type"""
        return 6 if self.type == 'major' else 12


# ===========================
# 5. PREREQUISITES
# ===========================

class Prerequisite(models.Model):
    """
    Links subjects with their prerequisites.
    A subject can have multiple prerequisites.
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='prerequisites',
        help_text='Subject that requires prerequisites'
    )
    prereq_subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='required_for',
        help_text='Prerequisite subject that must be passed first'
    )

    class Meta:
        db_table = 'prereqs'
        verbose_name = 'Prerequisite'
        verbose_name_plural = 'Prerequisites'
        unique_together = ['subject', 'prereq_subject']

    def __str__(self):
        return f"{self.subject.code} requires {self.prereq_subject.code}"


# ===========================
# 6. CURRICULUM SUBJECTS
# ===========================

class CurriculumSubject(models.Model):
    """
    Maps subjects to specific curriculum versions.
    Enables curriculum versioning when CHED/DepEd updates requirements.
    """
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name='curriculum_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='curriculum_mappings'
    )
    year_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    term_no = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text='1=1st sem, 2=2nd sem, 3=Summer'
    )
    is_recommended = models.BooleanField(
        default=True,
        help_text='Whether this subject is recommended for this year/term'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curriculum_subjects'
        verbose_name = 'Curriculum Subject'
        verbose_name_plural = 'Curriculum Subjects'
        unique_together = ['curriculum', 'subject']
        ordering = ['year_level', 'term_no']

    def __str__(self):
        return f"{self.curriculum.version} - {self.subject.code} (Y{self.year_level} T{self.term_no})"


# ===========================
# 7. STUDENTS
# ===========================

class Student(models.Model):
    """
    Student information linked to users, programs, and curricula.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name='students'
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT,
        related_name='students',
        help_text='Curriculum version assigned to this student'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    documents_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Document uploads stored as JSON (e.g., {"tor": "tor.pdf", "id": "id.png"})'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.user.username} - {self.program.name}"

    def is_freshman(self):
        """Check if student is a freshman (no completed subjects)"""
        return not self.enrolled_subjects.filter(status='completed').exists()


# ===========================
# 8. TERMS
# ===========================

class Term(models.Model):
    """
    Academic terms/semesters with deadlines and active status.
    Only one term should be active at a time.
    """
    name = models.CharField(
        max_length=50,
        help_text='e.g., "1st Semester AY 2025-2026"'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    add_drop_deadline = models.DateField(
        blank=True,
        null=True,
        help_text='Last day for students to add or drop subjects'
    )
    grade_encoding_deadline = models.DateField(
        blank=True,
        null=True,
        help_text='Last day for professors to encode grades'
    )
    is_active = models.BooleanField(
        default=False,
        help_text='Only one term should be active at a time'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'terms'
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def is_enrollment_open(self):
        """Check if enrollment period is still open"""
        today = timezone.now().date()
        if self.add_drop_deadline:
            return today <= self.add_drop_deadline
        return today <= self.end_date


# ===========================
# 9. SECTIONS
# ===========================

class Section(models.Model):
    """
    Subject offerings per term, tied to a professor.
    Students enroll in specific sections.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('closed', 'Closed'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    professor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_sections',
        limit_choices_to={'role': 'professor'}
    )
    section_code = models.CharField(
        max_length=20,
        help_text='e.g., "CS101-A", "MATH101-B"'
    )
    capacity = models.IntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        unique_together = ['subject', 'term', 'section_code']
        ordering = ['section_code']

    def __str__(self):
        return f"{self.section_code} - {self.subject.code} ({self.term.name})"

    def enrolled_count(self):
        """Returns current enrollment count"""
        return self.student_enrollments.filter(status='enrolled').count()

    def is_full(self):
        """Check if section is at capacity"""
        return self.enrolled_count() >= self.capacity

    def update_status(self):
        """Auto-update status based on capacity"""
        if self.is_full():
            self.status = 'full'
        elif self.status == 'full' and not self.is_full():
            self.status = 'open'
        self.save()


# ===========================
# 10. STUDENT SUBJECTS
# ===========================

class StudentSubject(models.Model):
    """
    Student enrollment records per subject/term/section.
    Tracks enrollment status and completion.
    """
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('inc', 'Incomplete'),
        ('repeat_required', 'Repeat Required'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrolled_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    professor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='student_subjects',
        limit_choices_to={'role': 'professor'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_subjects'
        verbose_name = 'Student Subject'
        verbose_name_plural = 'Student Subjects'
        unique_together = ['student', 'subject', 'term']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.code} ({self.term.name})"


# ===========================
# 11. GRADES
# ===========================

class Grade(models.Model):
    """
    Professor-submitted grades for student subjects.
    """
    student_subject = models.OneToOneField(
        StudentSubject,
        on_delete=models.CASCADE,
        related_name='grade_record'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    professor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='submitted_grades',
        limit_choices_to={'role': 'professor'}
    )
    grade = models.CharField(
        max_length=10,
        help_text='e.g., "1.00", "1.75", "2.00", "3.00", "5.00", "INC"'
    )
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grades'
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.student_subject.student.user.username} - {self.subject.code}: {self.grade}"

    def is_passing(self):
        """Check if grade is passing (≤ 3.00)"""
        try:
            grade_value = float(self.grade)
            return grade_value <= 3.00
        except ValueError:
            return self.grade == 'INC' or self.grade.upper() == 'P'


# ===========================
# 12. AUDIT TRAIL
# ===========================

class AuditTrail(models.Model):
    """
    Logs all major system modifications for accountability.
    """
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_actions',
        help_text='User who performed the action'
    )
    action = models.CharField(
        max_length=100,
        help_text='Action performed (e.g., "create_enrollment", "update_grade")'
    )
    entity = models.CharField(
        max_length=100,
        help_text='Model/table affected (e.g., "StudentSubjects", "Grades")'
    )
    entity_id = models.BigIntegerField(
        help_text='ID of the affected record'
    )
    old_value_json = models.JSONField(
        blank=True,
        null=True,
        help_text='Previous values before change'
    )
    new_value_json = models.JSONField(
        blank=True,
        null=True,
        help_text='New values after change'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_trail'
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.entity}:{self.entity_id} by {self.actor}"


# ===========================
# 13. ARCHIVE
# ===========================

class Archive(models.Model):
    """
    Unified archive for any entity (students, grades, terms, etc.).
    Preserves data snapshots when terms close or students graduate.
    """
    entity = models.CharField(
        max_length=100,
        help_text='Entity type (e.g., "Students", "Grades", "Terms")'
    )
    entity_id = models.BigIntegerField(
        help_text='Original record ID'
    )
    data_snapshot = models.JSONField(
        help_text='Complete JSON snapshot of the original record'
    )
    reason = models.CharField(
        max_length=255,
        help_text='Reason for archiving (e.g., "Term Closed", "Student Graduated")'
    )
    archived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archived_records'
    )
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'archive'
        verbose_name = 'Archive'
        verbose_name_plural = 'Archives'
        ordering = ['-archived_at']

    def __str__(self):
        return f"Archived {self.entity}:{self.entity_id} - {self.reason}"


# ===========================
# 14. SETTINGS
# ===========================

class Setting(models.Model):
    """
    Global system settings for dynamic control.
    Controls admission links, enrollment windows, unit caps, etc.
    """
    key_name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Setting key (e.g., "admission_link_enabled", "enrollment_open")'
    )
    value_text = models.CharField(
        max_length=255,
        help_text='Setting value (e.g., "true", "false", "30")'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Human-readable description of this setting'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='settings_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        ordering = ['key_name']

    def __str__(self):
        return f"{self.key_name} = {self.value_text}"

    @staticmethod
    def get_value(key_name, default=None):
        """Helper method to get setting value"""
        try:
            setting = Setting.objects.get(key_name=key_name)
            return setting.value_text
        except Setting.DoesNotExist:
            return default

    @staticmethod
    def get_bool(key_name, default=False):
        """Helper method to get boolean setting"""
        value = Setting.get_value(key_name)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    @staticmethod
    def get_int(key_name, default=0):
        """Helper method to get integer setting"""
        value = Setting.get_value(key_name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
