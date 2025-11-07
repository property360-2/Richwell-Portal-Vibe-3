# rci/grades/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from enrollment.models import StudentSubject
from academics.models import Subject


class Grade(models.Model):
    """Professor-submitted grades per subject"""
    student_subject = models.OneToOneField(
        StudentSubject,
        on_delete=models.CASCADE,
        related_name='grade'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submitted_grades'
    )
    grade = models.CharField(max_length=10, help_text="e.g. '1.75', 'INC', '5.00'")
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # INC tracking
    inc_posted_date = models.DateField(null=True, blank=True, help_text="Date when INC grade was given")

    # Audit trail
    remarks = models.TextField(blank=True, help_text="Additional notes or reasons for grade/changes")

    class Meta:
        db_table = 'grades'
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.student_subject.student.user.username} - {self.subject.code}: {self.grade}"

    @property
    def is_passing(self):
        """Check if grade is passing (less than or equal to program passing grade)"""
        try:
            grade_value = float(self.grade)
            passing_grade = self.subject.program.passing_grade
            return grade_value <= passing_grade
        except ValueError:
            # Handle non-numeric grades like 'INC', 'DRP', etc.
            return False

    @property
    def is_incomplete(self):
        """Check if grade is incomplete"""
        return self.grade.upper() == 'INC'

    @property
    def inc_expiration_date(self):
        """Calculate INC expiration date based on subject type"""
        if not self.is_incomplete or not self.inc_posted_date:
            return None

        # Major: 6 months, Minor: 1 year
        if self.subject.type == 'major':
            return self.inc_posted_date + timedelta(days=180)  # ~6 months
        else:  # minor or other
            return self.inc_posted_date + timedelta(days=365)  # 1 year

    @property
    def is_inc_expired(self):
        """Check if INC has expired"""
        if not self.is_incomplete:
            return False

        expiration = self.inc_expiration_date
        if not expiration:
            return False

        return timezone.now().date() > expiration

    def check_and_update_expired_inc(self):
        """Check if INC is expired and update status to repeat_required"""
        if self.is_inc_expired:
            self.student_subject.status = 'repeat_required'
            self.student_subject.save()
            return True
        return False

    def save(self, *args, **kwargs):
        """Override save to update StudentSubject status based on grade"""
        # Set inc_posted_date if grade is being set to INC
        if self.is_incomplete and not self.inc_posted_date:
            self.inc_posted_date = timezone.now().date()

        # Clear inc_posted_date if grade is no longer INC
        if not self.is_incomplete and self.inc_posted_date:
            self.inc_posted_date = None

        super().save(*args, **kwargs)

        # Update the student subject status based on grade
        if self.is_incomplete:
            self.student_subject.status = 'inc'
        elif self.is_passing:
            self.student_subject.status = 'completed'
        else:
            self.student_subject.status = 'failed'

        self.student_subject.save()

        # Check if INC is expired
        self.check_and_update_expired_inc()
