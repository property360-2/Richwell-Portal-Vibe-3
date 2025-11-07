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
    path('student/profile/', views.student_profile, name='student_profile'),
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

    # Curriculum management (Registrar)
    path('registrar/curricula/', views.curriculum_management, name='curriculum_management'),
    path('registrar/curricula/create/', views.curriculum_create, name='curriculum_create'),
    path('registrar/curricula/<int:curriculum_id>/edit/', views.curriculum_edit, name='curriculum_edit'),
    path('registrar/curricula/<int:curriculum_id>/delete/', views.curriculum_delete, name='curriculum_delete'),

    # Subject management (Registrar)
    path('registrar/subjects/', views.subject_management, name='subject_management'),
    path('registrar/subjects/create/', views.subject_create, name='subject_create'),
    path('registrar/subjects/<int:subject_id>/edit/', views.subject_edit, name='subject_edit'),
    path('registrar/subjects/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),

    # Curriculum-Subject mapping (Registrar)
    path('registrar/curricula/<int:curriculum_id>/subjects/', views.curriculum_subjects, name='curriculum_subjects'),
    path('registrar/curricula/<int:curriculum_id>/subjects/add/', views.curriculum_subject_add, name='curriculum_subject_add'),
    path('registrar/curriculum-subjects/<int:curriculum_subject_id>/remove/', views.curriculum_subject_remove, name='curriculum_subject_remove'),

    # Prerequisite management (Registrar)
    path('registrar/subjects/<int:subject_id>/prerequisites/', views.prerequisite_management, name='prerequisite_management'),
    path('registrar/subjects/<int:subject_id>/prerequisites/add/', views.prerequisite_add, name='prerequisite_add'),
    path('registrar/prerequisites/<int:prerequisite_id>/remove/', views.prerequisite_remove, name='prerequisite_remove'),

    # Student admission (Admission staff)
    path('admission/processing/', views.admission_processing, name='admission_processing'),
    path('admission/student/admit/', views.student_admit, name='student_admit'),
    path('admission/student/<int:student_id>/status/', views.student_status_update, name='student_status_update'),

    # Advanced reporting (Dean/Registrar)
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/grade-distribution/', views.report_grade_distribution, name='report_grade_distribution'),
    path('reports/student-performance/', views.report_student_performance, name='report_student_performance'),

    # INC grade tracking (Dean/Registrar)
    path('reports/inc-tracking/', views.inc_grade_tracking, name='inc_grade_tracking'),

    # Export functionality
    path('export/cor/pdf/', views.export_cor_pdf, name='export_cor_pdf'),
    path('export/section/<int:section_id>/roster/pdf/', views.export_section_roster_pdf, name='export_section_roster_pdf'),
    path('export/section/<int:section_id>/grades/csv/', views.export_section_grades_csv, name='export_section_grades_csv'),
    path('export/section/<int:section_id>/grades/excel/', views.export_section_grades_excel, name='export_section_grades_excel'),
    path('export/enrollment/report/csv/', views.export_enrollment_report_csv, name='export_enrollment_report_csv'),

    # Password management
    path('change-password/', views.change_password, name='change_password'),
    path('admin/reset-password/<int:user_id>/', views.reset_user_password, name='reset_user_password'),
]
