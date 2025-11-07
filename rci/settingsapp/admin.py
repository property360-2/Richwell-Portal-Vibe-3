# rci/settingsapp/admin.py
from django.contrib import admin
from .models import Setting


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key_name', 'value_text', 'description', 'updated_by', 'updated_at']
    search_fields = ['key_name', 'description']
    ordering = ['key_name']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('Setting Information', {
            'fields': ('key_name', 'value_text', 'description')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.updated_by:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
