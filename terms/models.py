from django.db import models
from core.mixins import TimeStampMixin

class Term(TimeStampMixin):
    school_year = models.CharField(max_length=9)  # e.g. 2025-2026
    semester = models.CharField(max_length=20, choices=[("1st", "1st"), ("2nd", "2nd"), ("Summer", "Summer")])
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ("school_year", "semester")

    def __str__(self):
        return f"{self.school_year} ({self.semester})"
