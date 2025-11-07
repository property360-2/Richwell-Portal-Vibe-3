# rci/admission/urls.py
from django.urls import path
from . import views

app_name = 'admission'

urlpatterns = [
    path('apply/', views.admission_form_view, name='apply'),
    path('confirmation/<int:pk>/', views.admission_confirmation_view, name='confirmation'),
    path('process/<int:pk>/', views.process_application_view, name='process'),
]
