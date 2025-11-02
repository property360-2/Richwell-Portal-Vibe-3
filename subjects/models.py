from django.db import models
from core.mixins import TimeStampMixin, ArchiveMixin
from courses.models import Course

class Subject(TimeStampMixin, ArchiveMixin):
    SUBJECT_TYPES = [("MAJOR", "Major"), ("MINOR", "Minor")]

    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    units = models.IntegerField(default=3)
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.code} – {self.title}"


class SubjectPrerequisite(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="prerequisites")
    prerequisite = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="required_for")

    class Meta:
        unique_together = ("subject", "prerequisite")

    def __str__(self):
        return f"{self.prerequisite.code} → {self.subject.code}"
