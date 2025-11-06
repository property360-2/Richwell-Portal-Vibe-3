from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Program, Curriculum, Subject, Prerequisite,
    CurriculumSubject, Student, Term, Section,
    StudentSubject, Grade, AuditTrail, Archive, Setting
)


# ===========================
# USER ADMIN
# ===========================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role field"""
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


# ===========================
# PROGRAM ADMIN
# ===========================

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'passing_grade', 'created_at']
    list_filter = ['level']
    search_fields = ['name']
    ordering = ['name']


# ===========================
# CURRICULUM ADMIN
# ===========================

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['program', 'version', 'effective_sy', 'active', 'created_at']
    list_filter = ['active', 'program']
    search_fields = ['version', 'effective_sy', 'program__name']
    ordering = ['-effective_sy']


# ===========================
# SUBJECT ADMIN
# ===========================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'program', 'units', 'type', 'recommended_year', 'recommended_sem', 'active']
    list_filter = ['type', 'active', 'program', 'recommended_year', 'recommended_sem']
    search_fields = ['code', 'title', 'description']
    ordering = ['code']
    readonly_fields = ['created_at']


# ===========================
# PREREQUISITE ADMIN
# ===========================

@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['subject', 'prereq_subject']
    search_fields = ['subject__code', 'subject__title', 'prereq_subject__code', 'prereq_subject__title']
    autocomplete_fields = ['subject', 'prereq_subject']


# ===========================
# CURRICULUM SUBJECT ADMIN
# ===========================

@admin.register(CurriculumSubject)
class CurriculumSubjectAdmin(admin.ModelAdmin):
    list_display = ['curriculum', 'subject', 'year_level', 'term_no', 'is_recommended', 'created_at']
    list_filter = ['year_level', 'term_no', 'is_recommended', 'curriculum__program']
    search_fields = ['curriculum__version', 'subject__code', 'subject__title']
    ordering = ['curriculum', 'year_level', 'term_no']


# ===========================
# STUDENT ADMIN
# ===========================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'curriculum', 'status', 'created_at']
    list_filter = ['status', 'program', 'curriculum']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user']


# ===========================
# TERM ADMIN
# ===========================

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'add_drop_deadline', 'grade_encoding_deadline', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['-start_date']
    readonly_fields = ['created_at']


# ===========================
# SECTION ADMIN
# ===========================

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['section_code', 'subject', 'term', 'professor', 'capacity', 'status', 'enrolled_count']
    list_filter = ['status', 'term', 'subject__program']
    search_fields = ['section_code', 'subject__code', 'subject__title', 'professor__username']
    ordering = ['term', 'section_code']
    readonly_fields = ['created_at']

    def enrolled_count(self, obj):
        return obj.enrolled_count()
    enrolled_count.short_description = 'Enrolled'


# ===========================
# STUDENT SUBJECT ADMIN
# ===========================

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'term', 'section', 'professor', 'status', 'created_at']
    list_filter = ['status', 'term', 'subject__program']
    search_fields = ['student__user__username', 'subject__code', 'subject__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


# ===========================
# GRADE ADMIN
# ===========================

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['get_student', 'subject', 'professor', 'grade', 'posted_at']
    list_filter = ['subject__program', 'posted_at']
    search_fields = ['student_subject__student__user__username', 'subject__code', 'subject__title']
    ordering = ['-posted_at']
    readonly_fields = ['posted_at']

    def get_student(self, obj):
        return obj.student_subject.student.user.username
    get_student.short_description = 'Student'
    get_student.admin_order_field = 'student_subject__student__user__username'


# ===========================
# AUDIT TRAIL ADMIN
# ===========================

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'entity', 'entity_id', 'created_at']
    list_filter = ['action', 'entity', 'created_at']
    search_fields = ['actor__username', 'action', 'entity']
    ordering = ['-created_at']
    readonly_fields = ['actor', 'action', 'entity', 'entity_id', 'old_value_json', 'new_value_json', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ===========================
# ARCHIVE ADMIN
# ===========================

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ['entity', 'entity_id', 'reason', 'archived_by', 'archived_at']
    list_filter = ['entity', 'archived_at']
    search_fields = ['entity', 'reason']
    ordering = ['-archived_at']
    readonly_fields = ['entity', 'entity_id', 'data_snapshot', 'reason', 'archived_by', 'archived_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ===========================
# SETTING ADMIN
# ===========================

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key_name', 'value_text', 'description', 'updated_by', 'updated_at']
    search_fields = ['key_name', 'description']
    ordering = ['key_name']
    readonly_fields = ['updated_at']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
