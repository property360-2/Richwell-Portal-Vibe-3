# rci/audit/urls.py
from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Archive management
    path('archives/', views.view_archives_view, name='archives_list'),
    path('archives/<int:archive_id>/', views.archive_detail_view, name='archive_detail'),
    path('archives/<int:archive_id>/restore/', views.restore_archive_view, name='restore_archive'),
    
    # Archive actions
    path('archive-term/<int:term_id>/', views.archive_term_view, name='archive_term'),
    path('archive-student/<int:student_id>/', views.archive_student_view, name='archive_student'),
]