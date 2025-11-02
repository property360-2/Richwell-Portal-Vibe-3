from django.db import models
from core.mixins import TimeStampMixin, ArchiveMixin

class Course(TimeStampMixin, ArchiveMixin):
    SECTOR_CHOICES = [
        ("SHS", "Senior High School"),
        ("TVET", "Technical-Vocational Education and Training"),
        ("COLLEGE", "Higher Education / College"),
    ]

    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default="COLLEGE")

    def __str__(self):
        return f"{self.code} – {self.title}"
