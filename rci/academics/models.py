# rci/academics/models.py
from django.db import models


class Program(models.Model):
    """Academic programs (BSCS, ABM, HUMSS, etc.)"""
    LEVEL_CHOICES = [
        ('SHS', 'Senior High School'),
        ('College', 'College'),
        ('Bachelor', 'Bachelor'),
        ('Masteral', 'Masteral'),
    ]

    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    passing_grade = models.DecimalField(max_digits=3, decimal_places=2, default=3.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'programs'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.level})"


class Curriculum(models.Model):
    """CHED/DepEd curriculum versions"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='curricula')
    version = models.CharField(max_length=50, help_text="e.g. 'CHED 2021 Rev'")
    effective_sy = models.CharField(max_length=20, help_text="e.g. 'AY 2021-2022'")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curricula'
        verbose_name_plural = 'Curricula'
        ordering = ['-effective_sy']

    def __str__(self):
        return f"{self.program.name} - {self.version} ({self.effective_sy})"


class Subject(models.Model):
    """Academic subjects with recommended year/sem and type"""
    TYPE_CHOICES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    code = models.CharField(max_length=50, unique=True, help_text="e.g. 'CS101'")
    title = models.CharField(max_length=255, help_text="e.g. 'Intro to Computing'")
    description = models.TextField(blank=True, null=True)
    units = models.DecimalField(max_digits=3, decimal_places=1)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='minor')
    recommended_year = models.IntegerField(null=True, blank=True, help_text="e.g. 1, 2, 3, 4")
    recommended_sem = models.IntegerField(null=True, blank=True, help_text="1 = 1st sem, 2 = 2nd sem")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"


class Prereq(models.Model):
    """Links subjects with their prerequisites"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='prerequisites')
    prereq_subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='required_for')

    class Meta:
        db_table = 'prereqs'
        unique_together = ['subject', 'prereq_subject']
        verbose_name = 'Prerequisite'
        verbose_name_plural = 'Prerequisites'

    def __str__(self):
        return f"{self.subject.code} requires {self.prereq_subject.code}"


class CurriculumSubject(models.Model):
    """Curriculum-to-subject mapping for versioned programs"""
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='curriculum_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='curriculum_mappings')
    year_level = models.IntegerField()
    term_no = models.IntegerField()
    is_recommended = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curriculum_subjects'
        ordering = ['year_level', 'term_no']

    def __str__(self):
        return f"{self.curriculum.version} - {self.subject.code} (Y{self.year_level} T{self.term_no})"
