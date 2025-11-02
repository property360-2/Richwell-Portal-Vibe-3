from django.contrib import admin
from .models import Section, AssignedSubject

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("code", "course", "term", "capacity", "slots_remaining")
    list_filter = ("term", "course")
    search_fields = ("code",)

@admin.register(AssignedSubject)
class AssignedSubjectAdmin(admin.ModelAdmin):
    list_display = ("section", "subject", "get_professors")
    search_fields = ("section__code", "subject__code")

    def get_professors(self, obj):
        return ", ".join(p.username for p in obj.professors.all())
    get_professors.short_description = "Professors"
