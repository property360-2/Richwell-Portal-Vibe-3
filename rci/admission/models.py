# rci/admission/models.py
from django.db import models
from django.conf import settings
from academics.models import Program, Curriculum


class AdmissionApplication(models.Model):
    """Admission applications for prospective students"""
    APPLICANT_TYPE_CHOICES = [
        ('freshman', 'Freshman'),
        ('transferee', 'Transferee'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    birth_date = models.DateField()

    # Application Details
    applicant_type = models.CharField(max_length=20, choices=APPLICANT_TYPE_CHOICES)
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='applications')

    # For Transferees
    previous_school = models.CharField(max_length=255, blank=True, null=True)
    credits_earned = models.IntegerField(null=True, blank=True, help_text="Number of units completed")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_applications'
    )

    # Generated User (after approval)
    generated_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admission_application'
    )

    # Documents
    documents_json = models.JSONField(default=dict, blank=True, help_text='Uploaded documents')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'admission_applications'
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_applicant_type_display()} ({self.status})"

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class TransfereeCredit(models.Model):
    """Credits granted to transferee students"""
    application = models.ForeignKey(
        AdmissionApplication,
        on_delete=models.CASCADE,
        related_name='credited_subjects'
    )
    subject_code = models.CharField(max_length=50)
    subject_title = models.CharField(max_length=255)
    units = models.DecimalField(max_digits=3, decimal_places=1)
    grade = models.CharField(max_length=10, help_text="Grade from previous school")
    credited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='credited_subjects'
    )
    credited_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transferee_credits'
        ordering = ['subject_code']

    def __str__(self):
        return f"{self.subject_code} - {self.subject_title} ({self.units} units)"
