# rci/grades/admin.py
from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'subject', 'grade', 'professor', 'posted_at']
    list_filter = ['subject__program', 'posted_at']
    search_fields = [
        'student_subject__student__user__username',
        'student_subject__student__user__first_name',
        'student_subject__student__user__last_name',
        'subject__code',
        'subject__title'
    ]
    ordering = ['-posted_at']
    readonly_fields = ['posted_at']

    def student_name(self, obj):
        return obj.student_subject.student.user.username
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student_subject__student__user__username'
