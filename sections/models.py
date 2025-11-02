from django.db import models
from core.mixins import TimeStampMixin, ArchiveMixin
from courses.models import Course
from terms.models import Term
from users.models import User
from subjects.models import Subject


class Section(TimeStampMixin, ArchiveMixin):
    code = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="sections")
    professors = models.ManyToManyField(
        User,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="sections",
        blank=True,
    )
    capacity = models.PositiveIntegerField(default=30)
    slots_remaining = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.code} ({self.course.code})"


class AssignedSubject(TimeStampMixin, ArchiveMixin):
    """
    Represents subjects assigned to a specific section,
    and optionally to one or more professors.
    """

    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="assigned_subjects"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="assigned_subjects"
    )
    professors = models.ManyToManyField(
        User,
        limit_choices_to={"role": "PROFESSOR"},
        related_name="assigned_subjects",
        blank=True,
    )

    class Meta:
        unique_together = ("section", "subject")

    def __str__(self):
        profs = ", ".join(p.username for p in self.professors.all()[:3]) or "TBA"
        return f"{self.subject.code} in {self.section.code} ({profs})"
