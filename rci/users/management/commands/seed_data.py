# rci/users/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import User
from academics.models import Program, Curriculum, Subject, Prereq, CurriculumSubject
from enrollment.models import Term, Section, Student, StudentSubject
from settingsapp.models import Setting


class Command(BaseCommand):
    help = 'Seed database with sample data for development and testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create Users
        self.stdout.write('Creating users...')
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@richwell.edu',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'System',
                'last_name': 'Administrator'
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        registrar_user, _ = User.objects.get_or_create(
            username='registrar',
            defaults={
                'email': 'registrar@richwell.edu',
                'role': 'registrar',
                'is_staff': True,
                'first_name': 'Anna',
                'last_name': 'Santos'
            }
        )
        registrar_user.set_password('registrar123')
        registrar_user.save()

        admission_user, _ = User.objects.get_or_create(
            username='admission',
            defaults={
                'email': 'admission@richwell.edu',
                'role': 'admission',
                'is_staff': True,
                'first_name': 'Maria',
                'last_name': 'Gonzales'
            }
        )
        admission_user.set_password('admission123')
        admission_user.save()

        dean_user, _ = User.objects.get_or_create(
            username='dean',
            defaults={
                'email': 'dean@richwell.edu',
                'role': 'dean',
                'is_staff': True,
                'first_name': 'Roberto',
                'last_name': 'Fernandez'
            }
        )
        dean_user.set_password('dean123')
        dean_user.save()

        prof1, _ = User.objects.get_or_create(
            username='prof_cruz',
            defaults={
                'email': 'jcruz@richwell.edu',
                'role': 'professor',
                'first_name': 'Juan',
                'last_name': 'Cruz'
            }
        )
        prof1.set_password('prof123')
        prof1.save()

        prof2, _ = User.objects.get_or_create(
            username='prof_reyes',
            defaults={
                'email': 'mreyes@richwell.edu',
                'role': 'professor',
                'first_name': 'Maria',
                'last_name': 'Reyes'
            }
        )
        prof2.set_password('prof123')
        prof2.save()

        student1, _ = User.objects.get_or_create(
            username='student_dela_cruz',
            defaults={
                'email': 'jdelacruz@students.richwell.edu',
                'role': 'student',
                'first_name': 'Jose',
                'last_name': 'Dela Cruz'
            }
        )
        student1.set_password('student123')
        student1.save()

        student2, _ = User.objects.get_or_create(
            username='student_garcia',
            defaults={
                'email': 'mgarcia@students.richwell.edu',
                'role': 'student',
                'first_name': 'Maria',
                'last_name': 'Garcia'
            }
        )
        student2.set_password('student123')
        student2.save()

        self.stdout.write(self.style.SUCCESS(f'✓ Created {User.objects.count()} users'))

        # Create Programs
        self.stdout.write('Creating programs...')
        bscs, _ = Program.objects.get_or_create(
            name='Bachelor of Science in Computer Science',
            defaults={
                'level': 'Bachelor',
                'passing_grade': 3.00
            }
        )

        bsit, _ = Program.objects.get_or_create(
            name='Bachelor of Science in Information Technology',
            defaults={
                'level': 'Bachelor',
                'passing_grade': 3.00
            }
        )

        stem, _ = Program.objects.get_or_create(
            name='Science, Technology, Engineering and Mathematics',
            defaults={
                'level': 'SHS',
                'passing_grade': 3.00
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Program.objects.count()} programs'))

        # Create Curricula
        self.stdout.write('Creating curricula...')
        bscs_curr, _ = Curriculum.objects.get_or_create(
            program=bscs,
            version='CHED 2018',
            defaults={
                'effective_sy': 'AY 2018-2019',
                'active': True
            }
        )

        bsit_curr, _ = Curriculum.objects.get_or_create(
            program=bsit,
            version='CHED 2018',
            defaults={
                'effective_sy': 'AY 2018-2019',
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Curriculum.objects.count()} curricula'))

        # Create Subjects
        self.stdout.write('Creating subjects...')
        cs101, _ = Subject.objects.get_or_create(
            code='CS101',
            defaults={
                'program': bscs,
                'title': 'Introduction to Computing',
                'description': 'Fundamentals of computer science and programming',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        cs102, _ = Subject.objects.get_or_create(
            code='CS102',
            defaults={
                'program': bscs,
                'title': 'Computer Programming 1',
                'description': 'Introduction to programming using Python',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        cs201, _ = Subject.objects.get_or_create(
            code='CS201',
            defaults={
                'program': bscs,
                'title': 'Data Structures and Algorithms',
                'description': 'Study of data structures and algorithm design',
                'units': 3.0,
                'type': 'major',
                'recommended_year': 2,
                'recommended_sem': 1,
                'active': True
            }
        )

        math101, _ = Subject.objects.get_or_create(
            code='MATH101',
            defaults={
                'program': bscs,
                'title': 'College Algebra',
                'description': 'Fundamental algebraic concepts',
                'units': 3.0,
                'type': 'minor',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Subject.objects.count()} subjects'))

        # Create Prerequisites
        self.stdout.write('Creating prerequisites...')
        Prereq.objects.get_or_create(
            subject=cs201,
            prereq_subject=cs102
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Prereq.objects.count()} prerequisites'))

        # Link Subjects to Curriculum
        self.stdout.write('Linking subjects to curriculum...')
        CurriculumSubject.objects.get_or_create(
            curriculum=bscs_curr,
            subject=cs101,
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )
        CurriculumSubject.objects.get_or_create(
            curriculum=bscs_curr,
            subject=cs102,
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )
        CurriculumSubject.objects.get_or_create(
            curriculum=bscs_curr,
            subject=math101,
            defaults={'year_level': 1, 'term_no': 1, 'is_recommended': True}
        )
        CurriculumSubject.objects.get_or_create(
            curriculum=bscs_curr,
            subject=cs201,
            defaults={'year_level': 2, 'term_no': 1, 'is_recommended': True}
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {CurriculumSubject.objects.count()} curriculum mappings'))

        # Create Terms
        self.stdout.write('Creating terms...')
        current_year = datetime.now().year
        term1, _ = Term.objects.get_or_create(
            name=f'1st Semester AY {current_year}-{current_year+1}',
            defaults={
                'start_date': datetime(current_year, 8, 1).date(),
                'end_date': datetime(current_year, 12, 15).date(),
                'add_drop_deadline': datetime(current_year, 8, 15).date(),
                'grade_encoding_deadline': datetime(current_year, 12, 20).date(),
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Term.objects.count()} terms'))

        # Create Students
        self.stdout.write('Creating student profiles...')
        student_profile1, _ = Student.objects.get_or_create(
            user=student1,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        student_profile2, _ = Student.objects.get_or_create(
            user=student2,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Student.objects.count()} student profiles'))

        # Create Sections
        self.stdout.write('Creating sections...')
        section1, _ = Section.objects.get_or_create(
            subject=cs101,
            term=term1,
            section_code='CS101-A',
            defaults={
                'professor': prof1,
                'capacity': 40,
                'status': 'open'
            }
        )

        section2, _ = Section.objects.get_or_create(
            subject=cs102,
            term=term1,
            section_code='CS102-A',
            defaults={
                'professor': prof1,
                'capacity': 40,
                'status': 'open'
            }
        )

        section3, _ = Section.objects.get_or_create(
            subject=math101,
            term=term1,
            section_code='MATH101-A',
            defaults={
                'professor': prof2,
                'capacity': 40,
                'status': 'open'
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Section.objects.count()} sections'))

        # Create System Settings
        self.stdout.write('Creating system settings...')
        settings_data = [
            ('admission_link_enabled', 'true', 'Enable/disable admission form'),
            ('enrollment_open', 'true', 'Allow or block student enrollment'),
            ('freshman_unit_cap', '30', 'Unit limit for freshmen'),
            ('passing_grade', '3.00', 'Default passing grade'),
            ('timezone', 'Asia/Manila', 'System timezone'),
        ]

        for key_name, value_text, description in settings_data:
            Setting.objects.get_or_create(
                key_name=key_name,
                defaults={
                    'value_text': value_text,
                    'description': description,
                    'updated_by': admin_user
                }
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {Setting.objects.count()} system settings'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('  Admin:      username: admin              password: admin123')
        self.stdout.write('  Registrar:  username: registrar          password: registrar123')
        self.stdout.write('  Admission:  username: admission          password: admission123')
        self.stdout.write('  Dean:       username: dean               password: dean123')
        self.stdout.write('  Professor:  username: prof_cruz          password: prof123')
        self.stdout.write('  Student:    username: student_dela_cruz password: student123')
