# rci/grades/urls.py
from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    # Professor views
    path('professor/sections/', views.professor_sections_view, name='professor_sections'),
    path('professor/section/<int:section_id>/', views.section_grades_view, name='section_grades'),
    path('professor/submit/<int:enrollment_id>/', views.submit_grade_view, name='submit_grade'),

    # Student views
    path('my-grades/', views.student_grades_view, name='student_grades'),
]
