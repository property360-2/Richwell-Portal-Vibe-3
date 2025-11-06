from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Generic dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Role-specific dashboards
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('professor/', views.professor_dashboard, name='professor_dashboard'),
    path('registrar/', views.registrar_dashboard, name='registrar_dashboard'),
    path('dean/', views.dean_dashboard, name='dean_dashboard'),
    path('admission/', views.admission_dashboard, name='admission_dashboard'),

    # Enrollment system
    path('enrollment/', views.enrollment_view, name='enrollment'),
    path('enrollment/drop/<int:enrollment_id>/', views.drop_enrollment, name='drop_enrollment'),

    # Grade management
    path('section/<int:section_id>/students/', views.section_students, name='section_students'),
    path('grade/<int:enrollment_id>/', views.grade_student, name='grade_student'),
    path('section/<int:section_id>/bulk-upload/', views.bulk_grade_upload, name='bulk_grade_upload'),

    # Term management (Registrar)
    path('registrar/terms/', views.term_management, name='term_management'),
    path('registrar/terms/create/', views.term_create, name='term_create'),
    path('registrar/terms/<int:term_id>/edit/', views.term_edit, name='term_edit'),
    path('registrar/terms/<int:term_id>/delete/', views.term_delete, name='term_delete'),

    # Section management (Registrar)
    path('registrar/sections/', views.section_management, name='section_management'),
    path('registrar/sections/create/', views.section_create, name='section_create'),
    path('registrar/sections/<int:section_id>/edit/', views.section_edit, name='section_edit'),
    path('registrar/sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),

    # Program management (Registrar)
    path('registrar/programs/', views.program_management, name='program_management'),
    path('registrar/programs/create/', views.program_create, name='program_create'),
    path('registrar/programs/<int:program_id>/edit/', views.program_edit, name='program_edit'),

    # Settings management (Admin/Registrar)
    path('settings/', views.settings_management, name='settings_management'),
    path('settings/<int:setting_id>/edit/', views.setting_edit, name='setting_edit'),
]
