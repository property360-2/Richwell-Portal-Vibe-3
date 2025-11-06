"""
View mixins for class-based views
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require specific user role(s)
    Usage: class MyView(RoleRequiredMixin, View):
               required_role = 'student'  # or ['student', 'professor']
    """
    required_role = None
    permission_denied_message = 'Access denied'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Handle single role or list of roles
        required_roles = self.required_role if isinstance(self.required_role, list) else [self.required_role]

        if request.user.role not in required_roles:
            messages.error(request, self.permission_denied_message)
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require student role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_student():
            messages.error(request, 'Access denied: Students only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class ProfessorRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require professor role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_professor():
            messages.error(request, 'Access denied: Professors only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class RegistrarRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require registrar role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_registrar():
            messages.error(request, 'Access denied: Registrar only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class DeanRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require dean role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_dean():
            messages.error(request, 'Access denied: Dean only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class AdmissionStaffRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require admission staff role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_admission_staff():
            messages.error(request, 'Access denied: Admission staff only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require admin role
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_admin_user():
            messages.error(request, 'Access denied: Admin only')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class AuditTrailMixin:
    """
    Mixin to automatically create audit trail for create/update/delete operations
    """
    audit_action = None  # Override in subclass: 'create', 'update', 'delete'
    audit_entity = None  # Override in subclass: e.g., 'Student'

    def form_valid(self, form):
        """
        Override form_valid to add audit trail
        """
        from .models import AuditTrail
        import json

        response = super().form_valid(form)

        if self.audit_action and self.audit_entity and self.request.user.is_authenticated:
            entity_id = getattr(self.object, 'id', None)

            # Capture old and new values for updates
            old_values = {}
            new_values = {}

            if self.audit_action == 'update' and hasattr(form, 'changed_data'):
                for field in form.changed_data:
                    if hasattr(form.instance, field):
                        new_values[field] = str(getattr(form.instance, field))

            AuditTrail.objects.create(
                actor=self.request.user,
                action=self.audit_action,
                entity=self.audit_entity,
                entity_id=entity_id,
                old_value_json=old_values if old_values else None,
                new_value_json=new_values if new_values else None
            )

        return response


class EnrollmentPeriodRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require enrollment period to be open
    """
    def dispatch(self, request, *args, **kwargs):
        from .models import Term

        if not request.user.is_authenticated:
            return self.handle_no_permission()

        active_term = Term.objects.filter(is_active=True).first()

        if not active_term:
            messages.error(request, 'No active enrollment term')
            return redirect('dashboard')

        if not active_term.is_enrollment_open():
            messages.warning(request, 'Enrollment period has closed')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class PaginationMixin:
    """
    Mixin to add pagination support
    """
    paginate_by = 20  # Default items per page

    def get_paginate_by(self, queryset):
        """
        Allow paginate_by to be overridden via GET parameter
        """
        return self.request.GET.get('per_page', self.paginate_by)


class SearchMixin:
    """
    Mixin to add search functionality
    """
    search_fields = []  # Override in subclass: ['field1', 'field2__subfield']

    def get_queryset(self):
        """
        Filter queryset based on search query
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()

        if search_query and self.search_fields:
            from django.db.models import Q
            q_objects = Q()

            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})

            queryset = queryset.filter(q_objects)

        return queryset


class FilterMixin:
    """
    Mixin to add filtering functionality
    """
    filter_fields = {}  # Override in subclass: {'field': 'param_name'}

    def get_queryset(self):
        """
        Filter queryset based on GET parameters
        """
        queryset = super().get_queryset()

        for field, param in self.filter_fields.items():
            value = self.request.GET.get(param)
            if value:
                queryset = queryset.filter(**{field: value})

        return queryset


class ExportMixin:
    """
    Mixin to add export functionality (CSV, PDF)
    """
    export_fields = []  # Fields to include in export
    export_filename = 'export'

    def export_csv(self, queryset):
        """
        Export queryset to CSV
        """
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.export_filename}.csv"'

        writer = csv.writer(response)

        # Write header
        writer.writerow(self.export_fields)

        # Write data
        for obj in queryset:
            row = [getattr(obj, field, '') for field in self.export_fields]
            writer.writerow(row)

        return response
