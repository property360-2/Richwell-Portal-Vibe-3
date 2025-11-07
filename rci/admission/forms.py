# rci/admission/forms.py
from django import forms
from .models import AdmissionApplication
from academics.models import Program


class AdmissionApplicationForm(forms.ModelForm):
    """Form for admission applications"""

    class Meta:
        model = AdmissionApplication
        fields = [
            'first_name', 'last_name', 'middle_name',
            'email', 'phone', 'address', 'birth_date',
            'applicant_type', 'program',
            'previous_school', 'credits_earned'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Last Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Middle Name (Optional)'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Complete Address', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'applicant_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'program': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'previous_school': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Previous School (Transferees only)'}),
            'credits_earned': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Units Completed'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active programs
        self.fields['program'].queryset = Program.objects.all()
        self.fields['middle_name'].required = False
        self.fields['previous_school'].required = False
        self.fields['credits_earned'].required = False

    def clean(self):
        cleaned_data = super().clean()
        applicant_type = cleaned_data.get('applicant_type')
        previous_school = cleaned_data.get('previous_school')
        credits_earned = cleaned_data.get('credits_earned')

        # Validate transferee fields
        if applicant_type == 'transferee':
            if not previous_school:
                self.add_error('previous_school', 'Previous school is required for transferees.')
            if not credits_earned:
                self.add_error('credits_earned', 'Credits earned is required for transferees.')

        return cleaned_data
