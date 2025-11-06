"""
Utility functions for the Richwell Portal.

This module contains helper functions used across the application.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def calculate_gpa(grades):
    """
    Calculate GPA from a list of grades.

    Args:
        grades: QuerySet or list of Grade objects

    Returns:
        Decimal: Calculated GPA (0.00 if no valid grades)
    """
    grade_values = {
        '1.00': Decimal('4.00'),
        '1.25': Decimal('3.75'),
        '1.50': Decimal('3.50'),
        '1.75': Decimal('3.25'),
        '2.00': Decimal('3.00'),
        '2.25': Decimal('2.75'),
        '2.50': Decimal('2.50'),
        '2.75': Decimal('2.25'),
        '3.00': Decimal('2.00'),
        '4.00': Decimal('1.00'),
        '5.00': Decimal('0.00'),
    }

    total_points = Decimal('0.00')
    total_units = 0

    for grade in grades:
        if hasattr(grade, 'numeric_grade') and grade.numeric_grade:
            grade_str = str(grade.numeric_grade)
            if grade_str in grade_values:
                units = grade.student_subject.subject.units if hasattr(grade, 'student_subject') else 3
                total_points += grade_values[grade_str] * units
                total_units += units

    if total_units == 0:
        return Decimal('0.00')

    gpa = total_points / total_units
    return round(gpa, 2)


def format_name(first_name, last_name, middle_name=None, format_type='full'):
    """
    Format name in different styles.

    Args:
        first_name: First name
        last_name: Last name
        middle_name: Middle name (optional)
        format_type: 'full', 'lastname_first', 'formal'

    Returns:
        str: Formatted name
    """
    if format_type == 'full':
        if middle_name:
            return f"{first_name} {middle_name} {last_name}"
        return f"{first_name} {last_name}"

    elif format_type == 'lastname_first':
        if middle_name:
            return f"{last_name}, {first_name} {middle_name}"
        return f"{last_name}, {first_name}"

    elif format_type == 'formal':
        if middle_name:
            middle_initial = middle_name[0] + '.'
            return f"{last_name}, {first_name} {middle_initial}"
        return f"{last_name}, {first_name}"

    return f"{first_name} {last_name}"


def generate_student_id(year, sequence):
    """
    Generate student ID in format: YYYY-NNNN

    Args:
        year: Academic year (e.g., 2024)
        sequence: Sequence number (e.g., 1, 2, 3...)

    Returns:
        str: Student ID (e.g., "2024-0001")
    """
    return f"{year}-{sequence:04d}"


def generate_section_code(subject_code, section_number):
    """
    Generate section code.

    Args:
        subject_code: Subject code (e.g., "CS101")
        section_number: Section number (e.g., 1, 2, 3)

    Returns:
        str: Section code (e.g., "CS101-1")
    """
    return f"{subject_code}-{section_number}"


def academic_year_display(start_year):
    """
    Format academic year for display.

    Args:
        start_year: Starting year (e.g., 2024)

    Returns:
        str: Academic year string (e.g., "AY 2024-2025")
    """
    end_year = start_year + 1
    return f"AY {start_year}-{end_year}"


def get_semester_name(semester_number):
    """
    Get semester name from number.

    Args:
        semester_number: Semester number (1, 2, 3)

    Returns:
        str: Semester name
    """
    semester_names = {
        1: "First Semester",
        2: "Second Semester",
        3: "Summer Term"
    }
    return semester_names.get(semester_number, f"Semester {semester_number}")


def calculate_age(birthdate):
    """
    Calculate age from birthdate.

    Args:
        birthdate: Date of birth

    Returns:
        int: Age in years
    """
    today = datetime.now().date()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def is_within_deadline(deadline_date, buffer_days=0):
    """
    Check if current date is within deadline.

    Args:
        deadline_date: Deadline date
        buffer_days: Buffer days after deadline (default 0)

    Returns:
        bool: True if within deadline
    """
    if not deadline_date:
        return True

    today = timezone.now().date()
    extended_deadline = deadline_date + timedelta(days=buffer_days)
    return today <= extended_deadline


def paginate_queryset(queryset, page_number, per_page=25):
    """
    Paginate a queryset.

    Args:
        queryset: Django queryset to paginate
        page_number: Current page number
        per_page: Items per page (default 25)

    Returns:
        Page object
    """
    paginator = Paginator(queryset, per_page)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def grade_to_numeric(letter_grade):
    """
    Convert letter grade to numeric equivalent.

    Args:
        letter_grade: Letter grade (P, F, INC, etc.)

    Returns:
        Decimal or None: Numeric grade or None if not convertible
    """
    conversions = {
        'P': Decimal('3.00'),  # Passing
        'F': Decimal('5.00'),  # Failing
    }
    return conversions.get(letter_grade)


def is_passing_grade(grade):
    """
    Check if a grade is passing.

    Args:
        grade: Grade value (numeric or letter)

    Returns:
        bool: True if passing
    """
    if isinstance(grade, str):
        if grade == 'P':
            return True
        if grade in ['F', 'INC', 'W']:
            return False
        try:
            grade = Decimal(grade)
        except:
            return False

    # Numeric grades: 1.00 - 3.00 are passing
    return Decimal('1.00') <= grade <= Decimal('3.00')


def format_grade_display(numeric_grade, letter_grade=None):
    """
    Format grade for display.

    Args:
        numeric_grade: Numeric grade (Decimal or None)
        letter_grade: Letter grade (str or None)

    Returns:
        str: Formatted grade
    """
    if letter_grade:
        return letter_grade
    if numeric_grade:
        return f"{numeric_grade:.2f}"
    return "No Grade"


def get_academic_status(gpa):
    """
    Determine academic status from GPA.

    Args:
        gpa: Current GPA

    Returns:
        str: Academic status
    """
    gpa = Decimal(str(gpa))

    if gpa >= Decimal('3.50'):
        return "Dean's List"
    elif gpa >= Decimal('3.00'):
        return "Good Standing"
    elif gpa >= Decimal('2.00'):
        return "Satisfactory"
    elif gpa >= Decimal('1.75'):
        return "Warning"
    else:
        return "Probation"


def sanitize_filename(filename):
    """
    Sanitize filename to remove special characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    import re
    # Remove special characters, keep alphanumeric, dots, hyphens, underscores
    clean_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return clean_name


def generate_temporary_password(length=8):
    """
    Generate a temporary password.

    Args:
        length: Password length (default 8)

    Returns:
        str: Generated password
    """
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_enrollment_statistics(term):
    """
    Get enrollment statistics for a term.

    Args:
        term: Term instance

    Returns:
        dict: Statistics dictionary
    """
    from .models import Section, StudentSubject

    sections = Section.objects.filter(term=term)
    total_sections = sections.count()
    total_capacity = sum(s.capacity for s in sections)

    enrollments = StudentSubject.objects.filter(term=term, status='enrolled')
    total_enrolled = enrollments.count()

    unique_students = enrollments.values('student').distinct().count()

    return {
        'total_sections': total_sections,
        'total_capacity': total_capacity,
        'total_enrolled': total_enrolled,
        'unique_students': unique_students,
        'utilization_rate': (total_enrolled / total_capacity * 100) if total_capacity > 0 else 0,
    }
