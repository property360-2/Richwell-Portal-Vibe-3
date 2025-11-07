# rci/grades/models.py
from django.db import models
from django.conf import settings
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

    def save(self, *args, **kwargs):
        """Override save to update StudentSubject status based on grade"""
        super().save(*args, **kwargs)

        # Update the student subject status based on grade
        if self.is_incomplete:
            self.student_subject.status = 'inc'
        elif self.is_passing:
            self.student_subject.status = 'completed'
        else:
            self.student_subject.status = 'failed'

        self.student_subject.save()
