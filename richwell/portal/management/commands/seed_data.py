"""
Management command to seed initial data for Richwell Portal
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from portal.models import (
    User, Program, Curriculum, Subject, Term, Setting,
    Student, Section, Prerequisite, CurriculumSubject
)
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed initial data for Richwell Portal (settings, programs, sample users)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        with transaction.atomic():
            # 1. Create Settings
            self.create_settings()

            # 2. Create Users
            admin, registrar, dean, admission, professor1, professor2, student1, student2 = self.create_users()

            # 3. Create Programs
            cs_program, it_program = self.create_programs()

            # 4. Create Curricula
            cs_curriculum, it_curriculum = self.create_curricula(cs_program, it_program)

            # 5. Create Subjects
            subjects = self.create_subjects(cs_program, it_program)

            # 6. Map Curriculum Subjects
            self.map_curriculum_subjects(cs_curriculum, it_curriculum, subjects)

            # 7. Create Prerequisites
            self.create_prerequisites(subjects)

            # 8. Create Term
            active_term = self.create_term()

            # 9. Create Sections
            sections = self.create_sections(active_term, subjects, professor1, professor2)

            # 10. Create Sample Students
            self.create_students(student1, student2, cs_program, it_program, cs_curriculum, it_curriculum)

        self.stdout.write(self.style.SUCCESS('\n✅ Data seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\n📋 Default Login Credentials:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Registrar: registrar / registrar123')
        self.stdout.write('  Dean: dean / dean123')
        self.stdout.write('  Admission: admission / admission123')
        self.stdout.write('  Professor: prof1 / prof123 | prof2 / prof123')
        self.stdout.write('  Student: student1 / student123 | student2 / student123')

    def create_settings(self):
        self.stdout.write('Creating system settings...')
        settings = [
            ('system_name', 'Richwell School Portal'),
            ('timezone', 'Asia/Manila'),
            ('admission_link_enabled', 'true'),
            ('enrollment_open', 'true'),
            ('freshman_max_units', '15'),
            ('passing_grade', '3.00'),
        ]

        for key, value in settings:
            Setting.objects.get_or_create(
                key_name=key,
                defaults={
                    'value_text': value,
                    'description': f'System setting: {key}'
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(settings)} settings'))

    def create_users(self):
        self.stdout.write('Creating users...')

        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@richwell.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Registrar
        registrar, created = User.objects.get_or_create(
            username='registrar',
            defaults={
                'email': 'registrar@richwell.edu',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'role': 'registrar'
            }
        )
        if created:
            registrar.set_password('registrar123')
            registrar.save()

        # Dean
        dean, created = User.objects.get_or_create(
            username='dean',
            defaults={
                'email': 'dean@richwell.edu',
                'first_name': 'Juan',
                'last_name': 'Dela Cruz',
                'role': 'dean'
            }
        )
        if created:
            dean.set_password('dean123')
            dean.save()

        # Admission Staff
        admission, created = User.objects.get_or_create(
            username='admission',
            defaults={
                'email': 'admission@richwell.edu',
                'first_name': 'Ana',
                'last_name': 'Garcia',
                'role': 'admission'
            }
        )
        if created:
            admission.set_password('admission123')
            admission.save()

        # Professors
        professor1, created = User.objects.get_or_create(
            username='prof1',
            defaults={
                'email': 'prof1@richwell.edu',
                'first_name': 'Pedro',
                'last_name': 'Reyes',
                'role': 'professor'
            }
        )
        if created:
            professor1.set_password('prof123')
            professor1.save()

        professor2, created = User.objects.get_or_create(
            username='prof2',
            defaults={
                'email': 'prof2@richwell.edu',
                'first_name': 'Rosa',
                'last_name': 'Martinez',
                'role': 'professor'
            }
        )
        if created:
            professor2.set_password('prof123')
            professor2.save()

        # Students
        student1, created = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'student1@richwell.edu',
                'first_name': 'Carlos',
                'last_name': 'Ramos',
                'role': 'student'
            }
        )
        if created:
            student1.set_password('student123')
            student1.save()

        student2, created = User.objects.get_or_create(
            username='student2',
            defaults={
                'email': 'student2@richwell.edu',
                'first_name': 'Lisa',
                'last_name': 'Torres',
                'role': 'student'
            }
        )
        if created:
            student2.set_password('student123')
            student2.save()

        self.stdout.write(self.style.SUCCESS('  ✓ Created 8 users'))

        return admin, registrar, dean, admission, professor1, professor2, student1, student2

    def create_programs(self):
        self.stdout.write('Creating programs...')

        cs_program, created = Program.objects.get_or_create(
            name='Bachelor of Science in Computer Science',
            defaults={
                'level': 'undergraduate',
                'passing_grade': 3.00
            }
        )

        it_program, created = Program.objects.get_or_create(
            name='Bachelor of Science in Information Technology',
            defaults={
                'level': 'undergraduate',
                'passing_grade': 3.00
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 2 programs'))

        return cs_program, it_program

    def create_curricula(self, cs_program, it_program):
        self.stdout.write('Creating curricula...')

        cs_curriculum, created = Curriculum.objects.get_or_create(
            program=cs_program,
            version='CHED 2023 Rev',
            defaults={
                'effective_sy': 'AY 2023-2024',
                'active': True
            }
        )

        it_curriculum, created = Curriculum.objects.get_or_create(
            program=it_program,
            version='CHED 2023 Rev',
            defaults={
                'effective_sy': 'AY 2023-2024',
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 2 curricula'))

        return cs_curriculum, it_curriculum

    def create_subjects(self, cs_program, it_program):
        self.stdout.write('Creating subjects...')

        subjects = {}

        # CS Subjects
        subjects['cs101'], _ = Subject.objects.get_or_create(
            code='CS101',
            defaults={
                'program': cs_program,
                'title': 'Introduction to Computing',
                'description': 'Fundamentals of computing and programming',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        subjects['cs102'], _ = Subject.objects.get_or_create(
            code='CS102',
            defaults={
                'program': cs_program,
                'title': 'Computer Programming 1',
                'description': 'Introduction to programming using Python',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        subjects['cs201'], _ = Subject.objects.get_or_create(
            code='CS201',
            defaults={
                'program': cs_program,
                'title': 'Data Structures',
                'description': 'Arrays, linked lists, stacks, queues, trees',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 2,
                'recommended_sem': 1,
                'active': True
            }
        )

        # IT Subjects
        subjects['it101'], _ = Subject.objects.get_or_create(
            code='IT101',
            defaults={
                'program': it_program,
                'title': 'Introduction to Information Technology',
                'description': 'Overview of IT field and careers',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        subjects['it102'], _ = Subject.objects.get_or_create(
            code='IT102',
            defaults={
                'program': it_program,
                'title': 'Web Development Fundamentals',
                'description': 'HTML, CSS, JavaScript basics',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        # General Education
        subjects['ge101'], _ = Subject.objects.get_or_create(
            code='GE101',
            defaults={
                'program': cs_program,
                'title': 'Purposive Communication',
                'description': 'Communication skills development',
                'units': 3.0,
                'type': 'general_education',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(subjects)} subjects'))

        return subjects

    def map_curriculum_subjects(self, cs_curriculum, it_curriculum, subjects):
        self.stdout.write('Mapping curriculum subjects...')

        # CS Curriculum
        CurriculumSubject.objects.get_or_create(
            curriculum=cs_curriculum,
            subject=subjects['cs101'],
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )

        CurriculumSubject.objects.get_or_create(
            curriculum=cs_curriculum,
            subject=subjects['cs102'],
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )

        CurriculumSubject.objects.get_or_create(
            curriculum=cs_curriculum,
            subject=subjects['cs201'],
            defaults={'year_level': 2, 'term_no': 1, 'is_recommended': True}
        )

        CurriculumSubject.objects.get_or_create(
            curriculum=cs_curriculum,
            subject=subjects['ge101'],
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )

        # IT Curriculum
        CurriculumSubject.objects.get_or_create(
            curriculum=it_curriculum,
            subject=subjects['it101'],
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )

        CurriculumSubject.objects.get_or_create(
            curriculum=it_curriculum,
            subject=subjects['it102'],
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Mapped curriculum subjects'))

    def create_prerequisites(self, subjects):
        self.stdout.write('Creating prerequisites...')

        # CS201 requires CS102
        Prerequisite.objects.get_or_create(
            subject=subjects['cs201'],
            prereq_subject=subjects['cs102']
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created prerequisites'))

    def create_term(self):
        self.stdout.write('Creating academic term...')

        today = date.today()
        start_date = today
        end_date = today + timedelta(days=120)  # ~4 months
        add_drop = today + timedelta(days=14)    # 2 weeks
        grade_deadline = end_date + timedelta(days=7)  # 1 week after term ends

        active_term, created = Term.objects.get_or_create(
            name='First Semester AY 2024-2025',
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'add_drop_deadline': add_drop,
                'grade_encoding_deadline': grade_deadline,
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created active term'))

        return active_term

    def create_sections(self, active_term, subjects, professor1, professor2):
        self.stdout.write('Creating sections...')

        sections = []

        # Create sections for each subject
        for key, subject in subjects.items():
            section, created = Section.objects.get_or_create(
                subject=subject,
                term=active_term,
                section_code=f'{subject.code}-A',
                defaults={
                    'professor': professor1 if 'cs' in key else professor2,
                    'capacity': 30,
                    'status': 'open'
                }
            )
            sections.append(section)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(sections)} sections'))

        return sections

    def create_students(self, student1, student2, cs_program, it_program, cs_curriculum, it_curriculum):
        self.stdout.write('Creating student profiles...')

        Student.objects.get_or_create(
            user=student1,
            defaults={
                'program': cs_program,
                'curriculum': cs_curriculum,
                'status': 'active'
            }
        )

        Student.objects.get_or_create(
            user=student2,
            defaults={
                'program': it_program,
                'curriculum': it_curriculum,
                'status': 'active'
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 2 student profiles'))
