# rci/admission/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import AdmissionApplication, TransfereeCredit


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'applicant_type', 'program', 'status', 'application_date']
    list_filter = ['status', 'applicant_type', 'program', 'application_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['application_date', 'processed_date', 'processed_by', 'generated_user']
    ordering = ['-application_date']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'email', 'phone', 'address', 'birth_date')
        }),
        ('Application Details', {
            'fields': ('applicant_type', 'program', 'previous_school', 'credits_earned')
        }),
        ('Status', {
            'fields': ('status', 'notes', 'documents_json')
        }),
        ('Processing Information', {
            'fields': ('application_date', 'processed_date', 'processed_by', 'generated_user'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """Bulk approve applications"""
        count = 0
        for application in queryset.filter(status='pending'):
            application.status = 'approved'
            application.processed_date = timezone.now()
            application.processed_by = request.user
            application.save()
            count += 1
        self.message_user(request, f'{count} application(s) approved.')
    approve_applications.short_description = 'Approve selected applications'

    def reject_applications(self, request, queryset):
        """Bulk reject applications"""
        count = 0
        for application in queryset.filter(status='pending'):
            application.status = 'rejected'
            application.processed_date = timezone.now()
            application.processed_by = request.user
            application.save()
            count += 1
        self.message_user(request, f'{count} application(s) rejected.')
    reject_applications.short_description = 'Reject selected applications'


@admin.register(TransfereeCredit)
class TransfereeCreditAdmin(admin.ModelAdmin):
    list_display = ['application', 'subject_code', 'subject_title', 'units', 'grade', 'credited_date']
    list_filter = ['credited_date']
    search_fields = ['application__first_name', 'application__last_name', 'subject_code', 'subject_title']
    readonly_fields = ['credited_date', 'credited_by']
    ordering = ['-credited_date']

    def save_model(self, request, obj, form, change):
        if not obj.credited_by:
            obj.credited_by = request.user
        super().save_model(request, obj, form, change)
