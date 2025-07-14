from django.db import models
from accounts.models import CustomUser
from .districts import Districts
from django.conf import settings
from django.core.validators import RegexValidator
from django import forms
from .models import *

class TeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields automatically
        for field in self.fields:
            if field != 'profile_picture':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                })
            if field in ['gender', 'school', 'user']:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                })

    class Meta:
        model = Teacher
        fields = [
            'user', 'year_of_entry', 'first_name', 'last_name', 
            'gender', 'profile_picture', 'school'
        ]
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }

    def clean_year_of_entry(self):
        year = self.cleaned_data.get('year_of_entry')
        if year and len(year) != 4:
            raise forms.ValidationError("Year must be in YYYY format.")
        return year


class PayrollInformationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })

    class Meta:
        model = PayrollInformation
        fields = ['salary', 'bank_name', 'account_number', 
                 'tax_identification_number', 'nssf_number', 'payment_frequency']
        widgets = {
            'payment_frequency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'salary': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
        }


class EducationBackgroundForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'additional_certifications':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                    'rows': '3'
                })

    class Meta:
        model = EducationBackground
        fields = ['education_award', 'institution', 'graduation_year', 
                 'result_obtained', 'additional_certifications']
        widgets = {
            'graduation_year': forms.NumberInput(attrs={
                'min': '1900',
                'max': '2100'
            }),
        }


class EmploymentHistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['start_date', 'end_date', 'responsibilities']:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                })
            elif field in ['start_date', 'end_date']:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                    'type': 'date'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                    'rows': '4'
                })

    class Meta:
        model = EmploymentHistory
        fields = ['organization', 'department', 'role', 
                 'start_date', 'end_date', 'responsibilities']


class NextOfKinForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'address':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                    'rows': '3'
                })

    class Meta:
        model = NextOfKin
        fields = ['name', 'relationship', 'contact_number', 'address']


class CurrentEmploymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })

    class Meta:
        model = CurrentEmployment
        fields = ['position', 'department']