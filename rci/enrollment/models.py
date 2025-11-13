# rci/enrollment/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import Program, Curriculum, Subject


class Student(models.Model):
    """Student info, linked to users, program, and curriculum"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='students')
    curriculum = models.ForeignKey(Curriculum, on_delete=models.PROTECT, related_name='students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    documents_json = models.JSONField(default=dict, blank=True, help_text='{"tor":"tor.pdf","id":"id.png"}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.program.name}"

    # ---------------------------------------------------------------
    # Custom method: Graduate student and archive academic record
    # ---------------------------------------------------------------
    def graduate_student(self, graduated_by):
        """
        Mark student as graduated and archive complete academic record
        Returns: (success: bool, message: str)
        """
        from django.db import transaction
        from django.utils import timezone
        from audit.models import Archive, AuditTrail
        from grades.models import Grade

        if self.status == 'graduated':
            return False, 'Student is already marked as graduated.'

        try:
            with transaction.atomic():
                # Get all student subjects
                all_subjects = self.student_subjects.select_related(
                    'subject', 'term', 'section', 'professor'
                ).order_by('term__start_date', 'subject__code')

                # Build complete academic record
                subjects_data = []
                for ss in all_subjects:
                    grade_data = None
                    try:
                        grade = ss.grade
                        grade_data = {
                            'grade': grade.grade,
                            'posted_at': grade.posted_at.isoformat() if grade.posted_at else None,
                            'remarks': grade.remarks,
                        }
                    except Grade.DoesNotExist:
                        pass

                    subjects_data.append({
                        'term': ss.term.name,
                        'subject_code': ss.subject.code,
                        'subject_title': ss.subject.title,
                        'units': str(ss.subject.units),
                        'type': ss.subject.type,
                        'section': ss.section.section_code,
                        'professor': ss.professor.get_full_name(),
                        'status': ss.status,
                        'grade': grade_data,
                        'enrolled_date': ss.created_at.isoformat(),
                    })

                # Calculate statistics
                completed_subjects = [s for s in subjects_data if s['status'] == 'completed']
                total_units = sum(float(s['units']) for s in completed_subjects)

                # Calculate GPA
                gpa_points = 0
                gpa_units = 0
                for s in completed_subjects:
                    if s['grade'] and s['grade']['grade']:
                        try:
                            grade_value = float(s['grade']['grade'])
                            gpa_points += grade_value * float(s['units'])
                            gpa_units += float(s['units'])
                        except ValueError:
                            pass

                final_gpa = round(gpa_points / gpa_units, 2) if gpa_units > 0 else None

                # Create comprehensive snapshot
                snapshot = {
                    'student_info': {
                        'username': self.user.username,
                        'full_name': self.user.get_full_name(),
                        'email': self.user.email,
                        'first_name': self.user.first_name,
                        'last_name': self.user.last_name,
                        'program': self.program.name,
                        'program_level': self.program.level,
                        'curriculum': self.curriculum.version,
                        'curriculum_effective_sy': self.curriculum.effective_sy,
                        'enrolled_date': self.created_at.isoformat(),
                        'graduation_date': timezone.now().isoformat(),
                    },
                    'academic_record': subjects_data,
                    'statistics': {
                        'total_subjects_taken': len(subjects_data),
                        'subjects_completed': len(completed_subjects),
                        'subjects_failed': sum(1 for s in subjects_data if s['status'] == 'failed'),
                        'subjects_with_inc': sum(1 for s in subjects_data if s['status'] == 'inc'),
                        'total_units_completed': str(total_units),
                        'final_gpa': str(final_gpa) if final_gpa else None,
                    },
                    'archived_date': timezone.now().isoformat(),
                    'archived_by': graduated_by.username,
                }

                # Create archive
                Archive.objects.create(
                    entity='Student',
                    entity_id=self.id,
                    data_snapshot=snapshot,
                    reason='Student Graduated',
                    archived_by=graduated_by
                )

                # Update student status
                old_status = self.status
                self.status = 'graduated'
                self.save()

                # Log in audit trail
                AuditTrail.objects.create(
                    actor=graduated_by,
                    action='graduate_student',
                    entity='Student',
                    entity_id=self.id,
                    old_value_json={'status': old_status},
                    new_value_json={
                        'status': 'graduated',
                        'total_units': str(total_units),
                        'gpa': str(final_gpa) if final_gpa else None
                    },
                )

                return True, f'Successfully graduated {self.user.get_full_name()} and archived academic record.'

        except Exception as e:
            return False, f'Error graduating student: {str(e)}'


class Term(models.Model):
    """Defines semesters/trimesters per academic year"""
    name = models.CharField(max_length=50, help_text="e.g. '1st Semester AY 2025-2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    add_drop_deadline = models.DateField(null=True, blank=True)
    grade_encoding_deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'terms'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    # ---------------------------------------------------------------
    # Custom method: Close this term and archive related enrollments
    # ---------------------------------------------------------------
    def close_term(self, closed_by):
        """
        Close this term and archive all associated data
        Returns: (success: bool, message: str, archived_count: int)
        """
        from django.db import transaction
        from audit.models import Archive, AuditTrail

        if self.is_active:
            self.is_active = False
            self.save()

        try:
            with transaction.atomic():
                archived_count = 0

                from enrollment.models import StudentSubject
                from grades.models import Grade

                student_subjects = StudentSubject.objects.filter(term=self).select_related(
                    'student__user', 'subject', 'section', 'professor'
                )

                for ss in student_subjects:
                    grade_data = None
                    try:
                        grade = ss.grade
                        grade_data = {
                            'grade': grade.grade,
                            'posted_at': grade.posted_at.isoformat() if grade.posted_at else None,
                            'inc_posted_date': grade.inc_posted_date.isoformat() if grade.inc_posted_date else None,
                            'remarks': grade.remarks,
                        }
                    except Grade.DoesNotExist:
                        pass

                    snapshot = {
                        'student_username': ss.student.user.username,
                        'student_name': ss.student.user.get_full_name(),
                        'subject_code': ss.subject.code,
                        'subject_title': ss.subject.title,
                        'subject_units': str(ss.subject.units),
                        'section_code': ss.section.section_code,
                        'professor_name': ss.professor.get_full_name(),
                        'status': ss.status,
                        'enrolled_date': ss.created_at.isoformat(),
                        'grade_data': grade_data,
                    }

                    Archive.objects.create(
                        entity='StudentSubject',
                        entity_id=ss.id,
                        data_snapshot=snapshot,
                        reason=f'Term Closed: {self.name}',
                        archived_by=closed_by
                    )
                    archived_count += 1

                term_snapshot = {
                    'name': self.name,
                    'start_date': self.start_date.isoformat(),
                    'end_date': self.end_date.isoformat(),
                    'add_drop_deadline': self.add_drop_deadline.isoformat() if self.add_drop_deadline else None,
                    'grade_encoding_deadline': self.grade_encoding_deadline.isoformat() if self.grade_encoding_deadline else None,
                    'total_sections': self.sections.count(),
                    'total_enrollments': student_subjects.count(),
                    'closed_date': timezone.now().isoformat(),
                }

                Archive.objects.create(
                    entity='Term',
                    entity_id=self.id,
                    data_snapshot=term_snapshot,
                    reason='Term Closed',
                    archived_by=closed_by
                )

                AuditTrail.objects.create(
                    actor=closed_by,
                    action='close_term',
                    entity='Term',
                    entity_id=self.id,
                    old_value_json={'is_active': True},
                    new_value_json={'is_active': False, 'archived_records': archived_count},
                )

                return True, f'Term closed successfully. Archived {archived_count} records.', archived_count

        except Exception as e:
            return False, f'Error closing term: {str(e)}', 0


class Section(models.Model):
    """Each subject offering per term (tied to a professor)"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('closed', 'Closed'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sections')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='sections')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sections',
        limit_choices_to={'role': 'professor'}
    )
    section_code = models.CharField(max_length=20, help_text="e.g. 'CS101-A'")
    capacity = models.IntegerField(default=40)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        unique_together = ['subject', 'term', 'section_code']
        ordering = ['section_code']

    def __str__(self):
        return f"{self.section_code} - {self.subject.code} ({self.term.name})"

    @property
    def enrolled_count(self):
        """Returns the number of students enrolled in this section"""
        return self.student_subjects.count()

    @property
    def is_full(self):
        """Check if section is at capacity"""
        return self.enrolled_count >= self.capacity


class StudentSubject(models.Model):
    """Student's enrolled subjects per term + section"""
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('inc', 'Incomplete'),
        ('repeat_required', 'Repeat Required'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_enrollments')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='student_subjects')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='student_subjects')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='student_subjects'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_subjects'
        ordering = ['-created_at']
        unique_together = ['student', 'subject', 'term']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.code} ({self.term.name})"
