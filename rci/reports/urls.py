# rci/reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard_view, name='dashboard'),
    path('enrollment/', views.enrollment_report_view, name='enrollment'),
    path('grades/', views.grade_distribution_report_view, name='grades'),
    path('inc-tracking/', views.inc_tracking_report_view, name='inc_tracking'),
    path('student-load/', views.student_load_report_view, name='student_load'),
    path('section-utilization/', views.section_utilization_report_view, name='section_utilization'),
    path('audit-trail/', views.audit_trail_report_view, name='audit_trail'),
]
