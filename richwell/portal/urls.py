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
]
