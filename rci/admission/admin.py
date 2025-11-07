# rci/admission/admin.py
from django.contrib import admin
from .models import AdmissionApplication, TransfereeCredit


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'applicant_type', 'program', 'needs_registrar_review', 'generated_user', 'application_date']
    list_filter = ['applicant_type', 'needs_registrar_review', 'program', 'application_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['application_date', 'generated_user']
    ordering = ['-application_date']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'email', 'phone', 'address', 'birth_date')
        }),
        ('Application Details', {
            'fields': ('applicant_type', 'program', 'previous_school', 'credits_earned')
        }),
        ('System Information', {
            'fields': ('application_date', 'generated_user', 'needs_registrar_review', 'notes', 'documents_json')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Only admins can delete applications
        return request.user.is_superuser


@admin.register(TransfereeCredit)
class TransfereeCreditAdmin(admin.ModelAdmin):
    list_display = ['application', 'subject_code', 'subject_title', 'units', 'grade', 'credited_date']
    list_filter = ['credited_date']
    search_fields = ['application__first_name', 'application__last_name', 'subject_code', 'subject_title']
    readonly_fields = ['credited_date', 'credited_by']
    ordering = ['-credited_date']

    fieldsets = (
        ('Application', {
            'fields': ('application',)
        }),
        ('Subject Information', {
            'fields': ('subject_code', 'subject_title', 'units', 'grade')
        }),
        ('Credit Information', {
            'fields': ('credited_date', 'credited_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.credited_by:
            obj.credited_by = request.user
        super().save_model(request, obj, form, change)
