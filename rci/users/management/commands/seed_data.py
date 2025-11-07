# rci/users/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from users.models import User
from academics.models import Program, Curriculum, Subject, Prereq, CurriculumSubject
from enrollment.models import Term, Section, Student, StudentSubject
from grades.models import Grade
from settingsapp.models import Setting
from audit.models import AuditTrail


class Command(BaseCommand):
    help = 'Seed database with comprehensive test data for all plan.md scenarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('RICHWELL PORTAL - COMPREHENSIVE DATA SEEDING'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        # ==================== USERS ====================
        self.stdout.write('\n📋 Creating Users...')

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

        # Professors
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

        prof3, _ = User.objects.get_or_create(
            username='prof_santos',
            defaults={
                'email': 'rsantos@richwell.edu',
                'role': 'professor',
                'first_name': 'Ramon',
                'last_name': 'Santos'
            }
        )
        prof3.set_password('prof123')
        prof3.save()

        # Students - Different test scenarios
        # 1. Freshman student (just starting)
        freshman_user, _ = User.objects.get_or_create(
            username='freshman',
            defaults={
                'email': 'fresh@students.richwell.edu',
                'role': 'student',
                'first_name': 'Pedro',
                'last_name': 'Freshman'
            }
        )
        freshman_user.set_password('student123')
        freshman_user.save()

        # 2. Regular student WITH INC grades (needs to resolve before enrolling)
        student_inc, _ = User.objects.get_or_create(
            username='student_with_inc',
            defaults={
                'email': 'inc@students.richwell.edu',
                'role': 'student',
                'first_name': 'Maria',
                'last_name': 'Incomplete'
            }
        )
        student_inc.set_password('student123')
        student_inc.save()

        # 3. Regular student NO INC (ready to enroll)
        student_clean, _ = User.objects.get_or_create(
            username='student_clean',
            defaults={
                'email': 'clean@students.richwell.edu',
                'role': 'student',
                'first_name': 'Jose',
                'last_name': 'Completo'
            }
        )
        student_clean.set_password('student123')
        student_clean.save()

        # 4. Regular student (for general testing)
        student_regular, _ = User.objects.get_or_create(
            username='student_dela_cruz',
            defaults={
                'email': 'jdelacruz@students.richwell.edu',
                'role': 'student',
                'first_name': 'Juan',
                'last_name': 'Dela Cruz'
            }
        )
        student_regular.set_password('student123')
        student_regular.save()

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {User.objects.count()} users'))

        # ==================== PROGRAMS & CURRICULA ====================
        self.stdout.write('\n📚 Creating Programs & Curricula...')

        bscs, _ = Program.objects.get_or_create(
            name='Bachelor of Science in Computer Science',
            defaults={
                'level': 'Bachelor',
                'passing_grade': Decimal('3.00')
            }
        )

        bsit, _ = Program.objects.get_or_create(
            name='Bachelor of Science in Information Technology',
            defaults={
                'level': 'Bachelor',
                'passing_grade': Decimal('3.00')
            }
        )

        bscs_curr, _ = Curriculum.objects.get_or_create(
            program=bscs,
            version='CHED 2018',
            defaults={
                'effective_sy': 'AY 2018-2019',
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Program.objects.count()} programs'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Curriculum.objects.count()} curricula'))

        # ==================== SUBJECTS WITH PREREQUISITES ====================
        self.stdout.write('\n📖 Creating Subjects with Prerequisites Chain...')

        # Year 1, Sem 1 - Foundation subjects
        cs101, _ = Subject.objects.get_or_create(
            code='CS101',
            defaults={
                'program': bscs,
                'title': 'Introduction to Computing',
                'description': 'Fundamentals of computer science',
                'units': Decimal('3.0'),
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
                'units': Decimal('3.0'),
                'type': 'major',
                'recommended_year': 1,
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
                'units': Decimal('3.0'),
                'type': 'minor',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        eng101, _ = Subject.objects.get_or_create(
            code='ENG101',
            defaults={
                'program': bscs,
                'title': 'Communication Skills',
                'description': 'English communication fundamentals',
                'units': Decimal('3.0'),
                'type': 'minor',
                'recommended_year': 1,
                'recommended_sem': 1,
                'active': True
            }
        )

        # Year 1, Sem 2
        cs103, _ = Subject.objects.get_or_create(
            code='CS103',
            defaults={
                'program': bscs,
                'title': 'Computer Programming 2',
                'description': 'Object-oriented programming',
                'units': Decimal('3.0'),
                'type': 'major',
                'recommended_year': 1,
                'recommended_sem': 2,
                'active': True
            }
        )

        math102, _ = Subject.objects.get_or_create(
            code='MATH102',
            defaults={
                'program': bscs,
                'title': 'Calculus 1',
                'description': 'Differential calculus',
                'units': Decimal('3.0'),
                'type': 'minor',
                'recommended_year': 1,
                'recommended_sem': 2,
                'active': True
            }
        )

        # Year 2, Sem 1 - Requires prerequisites
        cs201, _ = Subject.objects.get_or_create(
            code='CS201',
            defaults={
                'program': bscs,
                'title': 'Data Structures and Algorithms',
                'description': 'Study of data structures and algorithm design',
                'units': Decimal('3.0'),
                'type': 'major',
                'recommended_year': 2,
                'recommended_sem': 1,
                'active': True
            }
        )

        cs202, _ = Subject.objects.get_or_create(
            code='CS202',
            defaults={
                'program': bscs,
                'title': 'Database Systems',
                'description': 'Relational database design and SQL',
                'units': Decimal('3.0'),
                'type': 'major',
                'recommended_year': 2,
                'recommended_sem': 1,
                'active': True
            }
        )

        # Year 2, Sem 2
        cs203, _ = Subject.objects.get_or_create(
            code='CS203',
            defaults={
                'program': bscs,
                'title': 'Web Development',
                'description': 'Modern web technologies and frameworks',
                'units': Decimal('3.0'),
                'type': 'major',
                'recommended_year': 2,
                'recommended_sem': 2,
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Subject.objects.count()} subjects'))

        # Prerequisites Setup
        self.stdout.write('\n🔗 Creating Prerequisite Relationships...')
        prereqs = [
            (cs103, cs102),  # CS103 requires CS102
            (cs201, cs102),  # CS201 requires CS102
            (cs201, cs101),  # CS201 requires CS101
            (cs202, cs103),  # CS202 requires CS103
            (cs203, cs202),  # CS203 requires CS202
            (math102, math101),  # Calculus requires Algebra
        ]

        for subject, prereq_subject in prereqs:
            Prereq.objects.get_or_create(
                subject=subject,
                prereq_subject=prereq_subject
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Prereq.objects.count()} prerequisite relationships'))

        # Link to Curriculum
        self.stdout.write('\n🔗 Linking Subjects to Curriculum...')
        curriculum_subjects = [
            (cs101, 1, 1), (cs102, 1, 1), (math101, 1, 1), (eng101, 1, 1),
            (cs103, 1, 2), (math102, 1, 2),
            (cs201, 2, 1), (cs202, 2, 1),
            (cs203, 2, 2),
        ]

        for subject, year, sem in curriculum_subjects:
            CurriculumSubject.objects.get_or_create(
                curriculum=bscs_curr,
                subject=subject,
                defaults={'year_level': year, 'term_no': sem, 'is_recommended': True}
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {CurriculumSubject.objects.count()} curriculum mappings'))

        # ==================== TERMS ====================
        self.stdout.write('\n📅 Creating Academic Terms...')

        current_year = datetime.now().year

        # Past term (for INC expiration testing)
        past_term, _ = Term.objects.get_or_create(
            name=f'1st Semester AY {current_year-1}-{current_year}',
            defaults={
                'start_date': datetime(current_year-1, 8, 1).date(),
                'end_date': datetime(current_year-1, 12, 15).date(),
                'add_drop_deadline': datetime(current_year-1, 8, 15).date(),
                'grade_encoding_deadline': datetime(current_year-1, 12, 20).date(),
                'is_active': False
            }
        )

        # Previous term (closed, has grades)
        prev_term, _ = Term.objects.get_or_create(
            name=f'2nd Semester AY {current_year-1}-{current_year}',
            defaults={
                'start_date': datetime(current_year, 1, 5).date(),
                'end_date': datetime(current_year, 5, 31).date(),
                'add_drop_deadline': datetime(current_year, 1, 20).date(),
                'grade_encoding_deadline': datetime(current_year, 6, 10).date(),
                'is_active': False
            }
        )

        # Current term (active - for enrollment)
        current_term, _ = Term.objects.get_or_create(
            name=f'1st Semester AY {current_year}-{current_year+1}',
            defaults={
                'start_date': datetime(current_year, 8, 1).date(),
                'end_date': datetime(current_year, 12, 15).date(),
                'add_drop_deadline': datetime(current_year, 8, 15).date(),
                'grade_encoding_deadline': datetime(current_year, 12, 20).date(),
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Term.objects.count()} terms'))

        # ==================== STUDENT PROFILES ====================
        self.stdout.write('\n👨‍🎓 Creating Student Profiles...')

        # Freshman - just starting
        freshman_profile, _ = Student.objects.get_or_create(
            user=freshman_user,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        # Student with INC
        student_inc_profile, _ = Student.objects.get_or_create(
            user=student_inc,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        # Student clean (no INC)
        student_clean_profile, _ = Student.objects.get_or_create(
            user=student_clean,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        # Regular student
        student_regular_profile, _ = Student.objects.get_or_create(
            user=student_regular,
            defaults={
                'program': bscs,
                'curriculum': bscs_curr,
                'status': 'active',
                'documents_json': {}
            }
        )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Student.objects.count()} student profiles'))

        # ==================== SECTIONS ====================
        self.stdout.write('\n🏫 Creating Sections for Current Term...')

        sections_data = [
            # Year 1, Sem 1 subjects (for freshmen)
            (cs101, current_term, 'CS101-A', prof1, 40),
            (cs102, current_term, 'CS102-A', prof1, 40),
            (math101, current_term, 'MATH101-A', prof2, 45),
            (eng101, current_term, 'ENG101-A', prof2, 50),
            # Year 1, Sem 2 subjects
            (cs103, current_term, 'CS103-A', prof1, 40),
            (math102, current_term, 'MATH102-A', prof2, 45),
            # Year 2 subjects (for students who completed Year 1)
            (cs201, current_term, 'CS201-A', prof3, 35),
            (cs202, current_term, 'CS202-A', prof3, 35),
            (cs203, current_term, 'CS203-A', prof3, 35),
        ]

        for subject, term, code, professor, capacity in sections_data:
            Section.objects.get_or_create(
                subject=subject,
                term=term,
                section_code=code,
                defaults={
                    'professor': professor,
                    'capacity': capacity,
                    'status': 'open'
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Section.objects.count()} sections'))

        # ==================== STUDENT SUBJECT RECORDS & GRADES ====================
        self.stdout.write('\n📝 Creating Student Records and Grades...')

        # Get sections for previous terms
        past_sections = {}
        prev_sections = {}
        curr_sections = {}

        for subject in [cs101, cs102, math101, eng101, cs103, math102]:
            # Create sections in past term
            past_sec, _ = Section.objects.get_or_create(
                subject=subject,
                term=past_term,
                section_code=f'{subject.code}-P',
                defaults={'professor': prof1, 'capacity': 40, 'status': 'closed'}
            )
            past_sections[subject.code] = past_sec

            # Create sections in previous term
            prev_sec, _ = Section.objects.get_or_create(
                subject=subject,
                term=prev_term,
                section_code=f'{subject.code}-B',
                defaults={'professor': prof1, 'capacity': 40, 'status': 'closed'}
            )
            prev_sections[subject.code] = prev_sec

        # Current term sections
        for subject in [cs101, cs102, math101, eng101, cs103, math102, cs201, cs202, cs203]:
            curr_sec = Section.objects.filter(subject=subject, term=current_term).first()
            if curr_sec:
                curr_sections[subject.code] = curr_sec

        # STUDENT WITH INC - Scenario testing INC expiration
        self.stdout.write('\n  📌 Setting up: Student WITH INC grades...')

        # Completed subjects (Year 1, Sem 1)
        for subject_code, grade_value in [('CS101', '1.75'), ('MATH101', '2.00'), ('ENG101', '2.50')]:
            ss, _ = StudentSubject.objects.get_or_create(
                student=student_inc_profile,
                subject=Subject.objects.get(code=subject_code),
                term=past_term,
                defaults={
                    'section': past_sections[subject_code],
                    'professor': prof1,
                    'status': 'completed'
                }
            )
            Grade.objects.get_or_create(
                student_subject=ss,
                subject=ss.subject,
                defaults={
                    'grade': grade_value,
                    'professor': prof1,
                    'remarks': 'Completed'
                }
            )

        # INC in major subject (CS102) - Posted 8 months ago (EXPIRED - major = 6 months)
        inc_major_date = (timezone.now() - timedelta(days=240)).date()
        ss_inc_major, _ = StudentSubject.objects.get_or_create(
            student=student_inc_profile,
            subject=cs102,
            term=past_term,
            defaults={
                'section': past_sections['CS102'],
                'professor': prof1,
                'status': 'inc'
            }
        )
        Grade.objects.get_or_create(
            student_subject=ss_inc_major,
            subject=cs102,
            defaults={
                'grade': 'INC',
                'inc_posted_date': inc_major_date,
                'professor': prof1,
                'remarks': 'Missing final project - EXPIRED'
            }
        )

        # INC in minor subject (MATH102) - Posted 8 months ago (ACTIVE - minor = 1 year)
        inc_minor_date = (timezone.now() - timedelta(days=240)).date()
        ss_inc_minor, _ = StudentSubject.objects.get_or_create(
            student=student_inc_profile,
            subject=math102,
            term=prev_term,
            defaults={
                'section': prev_sections['MATH102'],
                'professor': prof2,
                'status': 'inc'
            }
        )
        Grade.objects.get_or_create(
            student_subject=ss_inc_minor,
            subject=math102,
            defaults={
                'grade': 'INC',
                'inc_posted_date': inc_minor_date,
                'professor': prof2,
                'remarks': 'Incomplete requirements - still active'
            }
        )

        # Completed CS103 in previous term (after resolving one INC)
        ss_cs103, _ = StudentSubject.objects.get_or_create(
            student=student_inc_profile,
            subject=cs103,
            term=prev_term,
            defaults={
                'section': prev_sections['CS103'],
                'professor': prof1,
                'status': 'completed'
            }
        )
        Grade.objects.get_or_create(
            student_subject=ss_cs103,
            subject=cs103,
            defaults={
                'grade': '2.25',
                'professor': prof1,
                'remarks': 'Completed'
            }
        )

        # STUDENT CLEAN - No INC, ready to enroll in Year 2
        self.stdout.write('\n  📌 Setting up: Student CLEAN (No INC)...')

        # All Year 1 subjects completed with good grades
        clean_subjects = [
            ('CS101', '1.50', past_term, 'CS101'),
            ('CS102', '1.75', past_term, 'CS102'),
            ('MATH101', '2.00', past_term, 'MATH101'),
            ('ENG101', '2.25', past_term, 'ENG101'),
            ('CS103', '2.00', prev_term, 'CS103'),
            ('MATH102', '2.50', prev_term, 'MATH102'),
        ]

        for subject_code, grade_value, term, section_key in clean_subjects:
            subject_obj = Subject.objects.get(code=subject_code)
            section = past_sections[section_key] if term == past_term else prev_sections[section_key]

            ss, _ = StudentSubject.objects.get_or_create(
                student=student_clean_profile,
                subject=subject_obj,
                term=term,
                defaults={
                    'section': section,
                    'professor': prof1,
                    'status': 'completed'
                }
            )
            Grade.objects.get_or_create(
                student_subject=ss,
                subject=subject_obj,
                defaults={
                    'grade': grade_value,
                    'professor': prof1,
                    'remarks': 'Completed successfully'
                }
            )

        # REGULAR STUDENT - Mix of completed and one failed subject
        self.stdout.write('\n  📌 Setting up: Regular Student...')

        regular_subjects = [
            ('CS101', '2.00', past_term),
            ('CS102', '2.50', past_term),
            ('MATH101', '1.75', past_term),
            ('ENG101', '2.75', past_term),
            ('CS103', '5.00', prev_term),  # FAILED - needs to repeat
            ('MATH102', '2.00', prev_term),
        ]

        for subject_code, grade_value, term in regular_subjects:
            subject_obj = Subject.objects.get(code=subject_code)
            section = past_sections[subject_code] if term == past_term else prev_sections[subject_code]
            status = 'failed' if grade_value == '5.00' else 'completed'

            ss, _ = StudentSubject.objects.get_or_create(
                student=student_regular_profile,
                subject=subject_obj,
                term=term,
                defaults={
                    'section': section,
                    'professor': prof1,
                    'status': status
                }
            )
            Grade.objects.get_or_create(
                student_subject=ss,
                subject=subject_obj,
                defaults={
                    'grade': grade_value,
                    'professor': prof1,
                    'remarks': 'Failed - needs to repeat' if status == 'failed' else 'Completed'
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created student subject records and grades'))

        # ==================== SYSTEM SETTINGS ====================
        self.stdout.write('\n⚙️  Creating System Settings...')

        settings_data = [
            ('admission_link_enabled', 'true', 'Enable/disable admission form'),
            ('enrollment_open', 'true', 'Allow or block student enrollment'),
            ('freshman_unit_cap', '30', 'Unit limit for freshmen (per plan.md)'),
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

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {Setting.objects.count()} system settings'))

        # ==================== AUDIT TRAIL ====================
        self.stdout.write('\n📋 Creating Sample Audit Trail Entries...')

        audit_entries = [
            ('create_grade', 'Grade', 'Professor submitted grade for CS101'),
            ('update_grade', 'Grade', 'Grade updated from INC to 2.00'),
            ('create_enrollment', 'StudentSubject', 'Student enrolled in CS201'),
            ('update_setting', 'Setting', 'Changed freshman_unit_cap to 30'),
        ]

        for action, entity, notes in audit_entries:
            AuditTrail.objects.create(
                actor=admin_user,
                action=action,
                entity=entity,
                notes=notes
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {AuditTrail.objects.count()} audit entries'))

        # ==================== SUMMARY ====================
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('DATA SEEDING COMPLETED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  • Users: {User.objects.count()}')
        self.stdout.write(f'  • Programs: {Program.objects.count()}')
        self.stdout.write(f'  • Subjects: {Subject.objects.count()}')
        self.stdout.write(f'  • Prerequisites: {Prereq.objects.count()}')
        self.stdout.write(f'  • Terms: {Term.objects.count()}')
        self.stdout.write(f'  • Sections: {Section.objects.count()}')
        self.stdout.write(f'  • Students: {Student.objects.count()}')
        self.stdout.write(f'  • Grades: {Grade.objects.count()}')
        self.stdout.write(f'  • Settings: {Setting.objects.count()}')

        self.stdout.write('\n🔑 Test Credentials:')
        self.stdout.write('  ┌─────────────┬──────────────────────┬────────────────┐')
        self.stdout.write('  │ Role        │ Username             │ Password       │')
        self.stdout.write('  ├─────────────┼──────────────────────┼────────────────┤')
        self.stdout.write('  │ Admin       │ admin                │ admin123       │')
        self.stdout.write('  │ Registrar   │ registrar            │ registrar123   │')
        self.stdout.write('  │ Admission   │ admission            │ admission123   │')
        self.stdout.write('  │ Dean        │ dean                 │ dean123        │')
        self.stdout.write('  │ Professor   │ prof_cruz            │ prof123        │')
        self.stdout.write('  │ Professor   │ prof_reyes           │ prof123        │')
        self.stdout.write('  │ Professor   │ prof_santos          │ prof123        │')
        self.stdout.write('  │ Student     │ freshman             │ student123     │')
        self.stdout.write('  │ Student     │ student_with_inc     │ student123     │')
        self.stdout.write('  │ Student     │ student_clean        │ student123     │')
        self.stdout.write('  │ Student     │ student_dela_cruz    │ student123     │')
        self.stdout.write('  └─────────────┴──────────────────────┴────────────────┘')

        self.stdout.write('\n📚 Test Scenarios (All passwords: student123):')
        self.stdout.write('')
        self.stdout.write('  1. FRESHMAN → username: freshman')
        self.stdout.write('     • No prior subjects')
        self.stdout.write('     • Can enroll up to 30 units (freshman cap)')
        self.stdout.write('     • Available subjects: CS101, CS102, MATH101, ENG101')
        self.stdout.write('     • Tests: Freshman unit cap enforcement')
        self.stdout.write('')
        self.stdout.write('  2. STUDENT WITH INC → username: student_with_inc')
        self.stdout.write('     • Has EXPIRED INC in CS102 (major, 8 months old > 6 months)')
        self.stdout.write('     • Has ACTIVE INC in MATH102 (minor, 8 months old < 1 year)')
        self.stdout.write('     • Completed: CS101 (1.75), MATH101 (2.00), ENG101 (2.50), CS103 (2.25)')
        self.stdout.write('     • Cannot enroll in CS201 (blocked by CS102 INC prerequisite)')
        self.stdout.write('     • Tests: INC expiration rules, prerequisite blocking')
        self.stdout.write('')
        self.stdout.write('  3. STUDENT CLEAN → username: student_clean')
        self.stdout.write('     • All Year 1 subjects completed with passing grades')
        self.stdout.write('     • No INC grades')
        self.stdout.write('     • Ready to enroll in Year 2 subjects: CS201, CS202')
        self.stdout.write('     • Tests: Normal enrollment, all prerequisites met')
        self.stdout.write('')
        self.stdout.write('  4. REGULAR STUDENT → username: student_dela_cruz')
        self.stdout.write('     • Completed most Year 1 subjects')
        self.stdout.write('     • Failed CS103 (grade: 5.00) - needs to repeat')
        self.stdout.write('     • Tests: Failed subject re-enrollment')

        self.stdout.write('\n✅ Ready to test all plan.md scenarios!')
        self.stdout.write(self.style.SUCCESS('=' * 80))
