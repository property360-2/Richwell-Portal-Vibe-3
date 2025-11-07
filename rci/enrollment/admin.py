# rci/enrollment/admin.py
from django.contrib import admin
from .models import Student, Term, Section, StudentSubject


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'curriculum', 'status', 'created_at']
    list_filter = ['program', 'status', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('program', 'curriculum', 'status')
        }),
        ('Documents', {
            'fields': ('documents_json',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'add_drop_deadline', 'grade_encoding_deadline']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['-start_date']
    fieldsets = (
        ('Term Information', {
            'fields': ('name', 'is_active')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'add_drop_deadline', 'grade_encoding_deadline')
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['section_code', 'subject', 'term', 'professor', 'capacity', 'enrolled_count', 'status']
    list_filter = ['term', 'status', 'subject__program']
    search_fields = ['section_code', 'subject__code', 'subject__title', 'professor__username']
    ordering = ['section_code']

    def enrolled_count(self, obj):
        return obj.enrolled_count
    enrolled_count.short_description = 'Enrolled'


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'term', 'section', 'professor', 'status', 'created_at']
    list_filter = ['term', 'status', 'subject__program']
    search_fields = ['student__user__username', 'subject__code', 'subject__title']
    ordering = ['-created_at']
