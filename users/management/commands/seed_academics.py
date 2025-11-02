from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from terms.models import Term
from courses.models import Course
from subjects.models import Subject, SubjectPrerequisite
from sections.models import Section, AssignedSubject

class Command(BaseCommand):
    help = "Seed sample academic data (terms, courses, subjects, sections)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting academic data seeding..."))

        # 1️⃣ Active term
        term, _ = Term.objects.get_or_create(
            school_year="2025-2026",
            semester="1st",
            defaults={"active": True},
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Term: {term.school_year} ({term.semester})"))

        # 2️⃣ Courses
        courses_data = [
            {"code": "BSIT", "title": "Bachelor of Science in Information Technology", "description": "IT program"},
            {"code": "BSCS", "title": "Bachelor of Science in Computer Science", "description": "CS program"},
        ]
        courses = []
        for data in courses_data:
            obj, _ = Course.objects.get_or_create(**data)
            courses.append(obj)
            self.stdout.write(self.style.SUCCESS(f"✅ Course: {obj.code}"))

        # 3️⃣ Subjects per course
        subjects_seed = [
            {"code": "IT101", "title": "Intro to IT", "units": 3, "subject_type": "MAJOR", "course": courses[0]},
            {"code": "IT102", "title": "Programming 1", "units": 3, "subject_type": "MAJOR", "course": courses[0]},
            {"code": "CS101", "title": "Computer Fundamentals", "units": 3, "subject_type": "MAJOR", "course": courses[1]},
            {"code": "CS102", "title": "Data Structures", "units": 3, "subject_type": "MAJOR", "course": courses[1]},
        ]
        subjects = []
        for data in subjects_seed:
            subj, _ = Subject.objects.get_or_create(**data)
            subjects.append(subj)
            self.stdout.write(self.style.SUCCESS(f"✅ Subject: {subj.code}"))

        # Add a prerequisite (CS102 requires CS101)
        try:
            cs101 = Subject.objects.get(code="CS101")
            cs102 = Subject.objects.get(code="CS102")
            SubjectPrerequisite.objects.get_or_create(subject=cs102, prerequisite=cs101)
            self.stdout.write(self.style.SUCCESS("🔗 Prerequisite added: CS101 → CS102"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Skipped prerequisite: {e}"))

        # 4️⃣ Create a professor if not exists
        professor, _ = User.objects.get_or_create(
            username="professor_demo",
            defaults={"role": "PROFESSOR", "first_name": "John", "last_name": "Doe"},
        )
        professor.set_password("password123")
        professor.save()
        self.stdout.write(self.style.SUCCESS("👨‍🏫 Professor account created (professor_demo / password123)"))

        # 5️⃣ Create sections for each course
        for course in courses:
            section, _ = Section.objects.get_or_create(
                code=f"{course.code}-1A",
                course=course,
                term=term,
                defaults={"professor": professor, "capacity": 30, "slots_remaining": 30},
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Section: {section.code}"))

            # 6️⃣ Assign subjects to the section
            for subj in subjects:
                if subj.course == course:
                    AssignedSubject.objects.get_or_create(section=section, subject=subj, professor=professor)
                    self.stdout.write(f"   └ assigned {subj.code}")

        self.stdout.write(self.style.SUCCESS("\n🎓 Academic seed complete!"))
        self.stdout.write(self.style.SUCCESS("Login as dean to view data on dashboard."))
