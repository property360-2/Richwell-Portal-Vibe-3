# rci/enrollment/urls.py
from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    path('', views.enrollment_home_view, name='home'),
    path('auto-enroll/', views.auto_enroll_view, name='auto_enroll'),
    path('enroll/<int:section_id>/', views.enroll_subject_view, name='enroll'),
    path('drop/<int:enrollment_id>/', views.drop_subject_view, name='drop'),
    path('cor/', views.cor_view, name='cor'),
]
