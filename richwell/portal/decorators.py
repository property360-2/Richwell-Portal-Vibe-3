"""
Custom decorators for role-based access control and other utilities
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Decorator to require specific user roles
    Usage: @role_required('student', 'professor')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, f'Access denied: This page requires {" or ".join(roles)} role')
            return redirect('dashboard')
        return wrapper
    return decorator


def student_required(view_func):
    """
    Decorator to require student role
    Usage: @student_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_student():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Students only')
        return redirect('dashboard')
    return wrapper


def professor_required(view_func):
    """
    Decorator to require professor role
    Usage: @professor_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_professor():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Professors only')
        return redirect('dashboard')
    return wrapper


def registrar_required(view_func):
    """
    Decorator to require registrar role
    Usage: @registrar_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_registrar():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Registrar only')
        return redirect('dashboard')
    return wrapper


def dean_required(view_func):
    """
    Decorator to require dean role
    Usage: @dean_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_dean():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Dean only')
        return redirect('dashboard')
    return wrapper


def admission_staff_required(view_func):
    """
    Decorator to require admission staff role
    Usage: @admission_staff_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_admission_staff():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Admission staff only')
        return redirect('dashboard')
    return wrapper


def admin_required(view_func):
    """
    Decorator to require admin role
    Usage: @admin_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin_user():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied: Admin only')
        return redirect('dashboard')
    return wrapper


def ajax_required(view_func):
    """
    Decorator to require AJAX requests
    Usage: @ajax_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('AJAX request required')
    return wrapper


def audit_log(action: str, entity: str):
    """
    Decorator to automatically log actions in audit trail
    Usage: @audit_log('create_program', 'Program')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from .models import AuditTrail

            # Execute the view
            response = view_func(request, *args, **kwargs)

            # Log the action (simplified - you may want to capture more details)
            if request.user.is_authenticated:
                entity_id = kwargs.get('id') or kwargs.get('pk')
                AuditTrail.objects.create(
                    actor=request.user,
                    action=action,
                    entity=entity,
                    entity_id=entity_id,
                    new_value_json={}
                )

            return response
        return wrapper
    return decorator


def enrollment_period_required(view_func):
    """
    Decorator to require enrollment period to be open
    Usage: @enrollment_period_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from .models import Term

        active_term = Term.objects.filter(is_active=True).first()

        if not active_term:
            messages.error(request, 'No active enrollment term')
            return redirect('dashboard')

        if not active_term.is_enrollment_open():
            messages.warning(request, 'Enrollment period has closed')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper


def grade_encoding_period_required(view_func):
    """
    Decorator to require grade encoding period to be open
    Usage: @grade_encoding_period_required
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from .models import Term
        from django.utils import timezone

        active_term = Term.objects.filter(is_active=True).first()

        if not active_term:
            messages.error(request, 'No active term')
            return redirect('dashboard')

        if active_term.grade_encoding_deadline and timezone.now().date() > active_term.grade_encoding_deadline:
            messages.warning(request, 'Grade encoding period has ended')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper
