from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from .models import StudentSubject, Section, Grade, Student, Prerequisite


class EnrollmentForm(forms.Form):
    """
    Form for student enrollment with prerequisite validation
    """
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Section'
    )

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        self.term = kwargs.pop('term', None)
        super().__init__(*args, **kwargs)

        if self.term:
            # Only show open sections for the current term
            self.fields['section'].queryset = Section.objects.filter(
                term=self.term,
                status='open'
            ).select_related('subject', 'professor')

    def clean_section(self):
        section = self.cleaned_data.get('section')

        if not section:
            raise ValidationError('Please select a section.')

        if not self.student:
            raise ValidationError('Student not found.')

        # Check if already enrolled
        existing = StudentSubject.objects.filter(
            student=self.student,
            subject=section.subject,
            term=section.term
        ).exists()

        if existing:
            raise ValidationError(f'You are already enrolled in {section.subject.code}.')

        # Check if section is full
        if section.is_full():
            raise ValidationError(f'Section {section.section_code} is full.')

        # Check prerequisites
        prerequisites = Prerequisite.objects.filter(
            subject=section.subject
        ).select_related('prereq_subject')

        for prereq in prerequisites:
            # Check if student has passed the prerequisite
            has_passed = Grade.objects.filter(
                student_subject__student=self.student,
                subject=prereq.prereq_subject,
                grade__in=['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']
            ).exists()

            if not has_passed:
                raise ValidationError(
                    f'Prerequisite not met: {prereq.prereq_subject.code} - {prereq.prereq_subject.title}'
                )

        # Check if student is freshman and enforce unit cap (if configured)
        if self.student.is_freshman():
            from .models import Setting
            max_units = Setting.get_int('freshman_max_units', 15)

            # Calculate current enrolled units
            current_units = StudentSubject.objects.filter(
                student=self.student,
                term=section.term,
                status='enrolled'
            ).aggregate(
                total=models.Sum('subject__units')
            )['total'] or 0

            if current_units + section.subject.units > max_units:
                raise ValidationError(
                    f'Unit limit exceeded. Freshmen can enroll in maximum {max_units} units. '
                    f'You currently have {current_units} units enrolled.'
                )

        return section


class GradeEntryForm(forms.Form):
    """
    Form for professor to enter/update grades
    """
    GRADE_CHOICES = [
        ('1.00', '1.00'),
        ('1.25', '1.25'),
        ('1.50', '1.50'),
        ('1.75', '1.75'),
        ('2.00', '2.00'),
        ('2.25', '2.25'),
        ('2.50', '2.50'),
        ('2.75', '2.75'),
        ('3.00', '3.00'),
        ('4.00', '4.00 (Conditional)'),
        ('5.00', '5.00 (Failed)'),
        ('INC', 'INC (Incomplete)'),
        ('DRP', 'DRP (Dropped)'),
        ('P', 'P (Passed)'),
    ]

    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Grade'
    )

    def __init__(self, *args, **kwargs):
        self.student_subject = kwargs.pop('student_subject', None)
        self.professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')

        if not self.professor:
            raise ValidationError('Professor not found.')

        if not self.student_subject:
            raise ValidationError('Student enrollment not found.')

        # Verify professor is assigned to this section
        if self.student_subject.professor != self.professor:
            raise ValidationError('You are not authorized to grade this student.')

        return grade

    def save(self):
        """
        Save or update the grade
        """
        from .models import AuditTrail
        import json

        grade_value = self.cleaned_data['grade']

        # Get or create the grade record
        grade_obj, created = Grade.objects.get_or_create(
            student_subject=self.student_subject,
            defaults={
                'subject': self.student_subject.subject,
                'professor': self.professor,
                'grade': grade_value
            }
        )

        # If updating existing grade, log the change
        if not created:
            old_grade = grade_obj.grade
            grade_obj.grade = grade_value
            grade_obj.professor = self.professor
            grade_obj.save()

            # Create audit trail
            AuditTrail.objects.create(
                actor=self.professor,
                action='update_grade',
                entity='Grade',
                entity_id=grade_obj.id,
                old_value_json=json.dumps({'grade': old_grade}),
                new_value_json=json.dumps({'grade': grade_value})
            )

        # Update student subject status based on grade
        if grade_value in ['1.00', '1.25', '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00', 'P']:
            self.student_subject.status = 'completed'
        elif grade_value in ['5.00', 'DRP']:
            self.student_subject.status = 'failed'
        elif grade_value == 'INC':
            self.student_subject.status = 'inc'
        elif grade_value == '4.00':
            self.student_subject.status = 'repeat_required'

        self.student_subject.save()

        return grade_obj


class BulkGradeUploadForm(forms.Form):
    """
    Form for uploading grades in bulk via CSV
    """
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: student_id, grade',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )

    def __init__(self, *args, **kwargs):
        self.section = kwargs.pop('section', None)
        self.professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')

        if not csv_file:
            raise ValidationError('Please upload a CSV file.')

        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV file.')

        # Validate file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise ValidationError('File size must not exceed 5MB.')

        return csv_file
