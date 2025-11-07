# rci/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def login_view(request):
    """Login view for all user roles"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            # Redirect based on role
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Logout view for all users"""
    username = request.user.username
    auth_logout(request)
    messages.success(request, f'Goodbye, {username}! You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Role-based dashboard for all user types"""
    user = request.user
    context = {
        'user': user,
    }

    # Add role-specific context data
    if user.role == 'student':
        try:
            student = user.student_profile
            context['student'] = student
            context['enrolled_subjects'] = student.student_subjects.filter(
                status='enrolled'
            ).select_related('subject', 'section', 'term')
            context['completed_count'] = student.student_subjects.filter(status='completed').count()
            context['failed_count'] = student.student_subjects.filter(status='failed').count()
            context['inc_count'] = student.student_subjects.filter(status='inc').count()
        except Exception as e:
            context['error'] = 'Student profile not found'

    elif user.role == 'professor':
        from enrollment.models import Section
        context['sections'] = Section.objects.filter(
            professor=user
        ).select_related('subject', 'term')
        context['total_students'] = sum([section.enrolled_count for section in context['sections']])

    elif user.role in ['registrar', 'dean', 'admin']:
        from enrollment.models import Student, StudentSubject, Section
        from academics.models import Subject

        context['total_students'] = Student.objects.filter(status='active').count()
        context['total_enrollments'] = StudentSubject.objects.filter(status='enrolled').count()
        context['total_sections'] = Section.objects.count()
        context['total_subjects'] = Subject.objects.filter(active=True).count()

    elif user.role == 'admission':
        from enrollment.models import Student
        context['pending_applications'] = 0  # Placeholder for future admission module
        context['total_students'] = Student.objects.count()
        context['active_students'] = Student.objects.filter(status='active').count()

    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view for all users"""
    user = request.user
    context = {'user': user}

    # Add student-specific data if applicable
    if user.role == 'student':
        try:
            context['student'] = user.student_profile
        except:
            pass

    return render(request, 'users/profile.html', context)
