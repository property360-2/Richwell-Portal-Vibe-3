"""
Custom validators for the Richwell Portal.

This module contains custom validation logic for business rules
and data integrity checks.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class PasswordValidator:
    """Custom password validation rules."""

    @staticmethod
    def validate_password_strength(password):
        """
        Validate password meets strength requirements.

        Requirements:
        - At least 8 characters
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit

        Args:
            password: The password string to validate

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValidationError(
                _('Password must be at least 8 characters long.'),
                code='password_too_short'
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'),
                code='password_no_upper'
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.'),
                code='password_no_lower'
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _('Password must contain at least one digit.'),
                code='password_no_digit'
            )

        return True


class FileValidator:
    """Validators for file uploads."""

    ALLOWED_DOCUMENT_TYPES = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    def validate_file_extension(file):
        """
        Validate that uploaded file has an allowed extension.

        Args:
            file: UploadedFile object

        Raises:
            ValidationError: If file extension is not allowed
        """
        ext = file.name.split('.')[-1].lower()
        if ext not in FileValidator.ALLOWED_DOCUMENT_TYPES:
            raise ValidationError(
                _(f'File type .{ext} is not allowed. Allowed types: {", ".join(FileValidator.ALLOWED_DOCUMENT_TYPES)}'),
                code='invalid_file_type'
            )
        return True

    @staticmethod
    def validate_file_size(file):
        """
        Validate that uploaded file doesn't exceed maximum size.

        Args:
            file: UploadedFile object

        Raises:
            ValidationError: If file is too large
        """
        if file.size > FileValidator.MAX_FILE_SIZE:
            max_size_mb = FileValidator.MAX_FILE_SIZE / (1024 * 1024)
            raise ValidationError(
                _(f'File size exceeds maximum allowed size of {max_size_mb}MB.'),
                code='file_too_large'
            )
        return True


class AcademicValidator:
    """Validators for academic business rules."""

    @staticmethod
    def validate_grade(grade):
        """
        Validate grade value.

        Numeric grades: 1.00 - 5.00
        Letter grades: P, F, INC, W

        Args:
            grade: Grade value (string or Decimal)

        Raises:
            ValidationError: If grade is invalid
        """
        grade_str = str(grade)

        # Check if it's a letter grade
        if grade_str in ['P', 'F', 'INC', 'W']:
            return True

        # Check if it's a valid numeric grade
        try:
            grade_decimal = float(grade_str)
            if not (1.00 <= grade_decimal <= 5.00):
                raise ValidationError(
                    _('Numeric grade must be between 1.00 and 5.00'),
                    code='invalid_grade_range'
                )
            # Check if it follows the valid grade increments
            valid_grades = [1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 4.00, 5.00]
            if grade_decimal not in valid_grades:
                raise ValidationError(
                    _('Grade must be one of: 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 4.00, 5.00, P, F, INC, W'),
                    code='invalid_grade_value'
                )
            return True
        except (ValueError, TypeError):
            raise ValidationError(
                _('Invalid grade format'),
                code='invalid_grade_format'
            )

    @staticmethod
    def validate_units(units):
        """
        Validate academic units.

        Args:
            units: Number of units (integer)

        Raises:
            ValidationError: If units are invalid
        """
        if units < 0:
            raise ValidationError(
                _('Units cannot be negative'),
                code='negative_units'
            )
        if units > 12:
            raise ValidationError(
                _('Subject units cannot exceed 12'),
                code='excessive_units'
            )
        return True

    @staticmethod
    def validate_year_level(year_level):
        """
        Validate student year level.

        Args:
            year_level: Year level (1-6 typically)

        Raises:
            ValidationError: If year level is invalid
        """
        if year_level < 1 or year_level > 6:
            raise ValidationError(
                _('Year level must be between 1 and 6'),
                code='invalid_year_level'
            )
        return True


class EnrollmentValidator:
    """Validators for enrollment business logic."""

    @staticmethod
    def validate_unit_cap(current_units, additional_units, max_units=30):
        """
        Validate that adding units doesn't exceed cap.

        Args:
            current_units: Currently enrolled units
            additional_units: Units to add
            max_units: Maximum allowed units (default 30 for freshmen)

        Raises:
            ValidationError: If units exceed cap
        """
        total = current_units + additional_units
        if total > max_units:
            raise ValidationError(
                _(f'Total units ({total}) would exceed maximum of {max_units} units'),
                code='unit_cap_exceeded'
            )
        return True

    @staticmethod
    def validate_section_capacity(current_enrolled, capacity, additional=1):
        """
        Validate that section has capacity.

        Args:
            current_enrolled: Currently enrolled students
            capacity: Section capacity
            additional: Number of students to add (default 1)

        Raises:
            ValidationError: If section is full
        """
        if current_enrolled + additional > capacity:
            raise ValidationError(
                _('Section is full. No more students can be enrolled.'),
                code='section_full'
            )
        return True
