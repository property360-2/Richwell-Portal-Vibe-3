# rci/staff/urls.py
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Students Management
    path('students/', views.students_list_view, name='students_list'),
    path('students/<int:student_id>/', views.student_detail_view, name='student_detail'),

    # Sections Management
    path('sections/', views.sections_list_view, name='sections_list'),
    path('sections/<int:section_id>/', views.section_detail_view, name='section_detail'),

    # Term Management
    path('terms/', views.terms_list_view, name='terms_list'),
    path('terms/<int:term_id>/', views.term_detail_view, name='term_detail'),

    # Enrollment Overview
    path('enrollments/', views.enrollments_overview_view, name='enrollments_overview'),

    # Applications Management
    path('applications/', views.applications_list_view, name='applications_list'),
    path('applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
]
