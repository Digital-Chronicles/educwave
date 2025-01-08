from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    GeneralInformation,
    ApplicationSetting,
    Lesson,
    SchedulingSetting,
    CertificateAward,
    Grade,
    TransactionSetting,
)


# Forms

class GeneralInformationForm(forms.ModelForm):
    class Meta:
        model = GeneralInformation
        fields = '__all__'
        exclude = ['registered_by']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'email': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'website': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control border-input'}),
        }


class ApplicationSettingForm(forms.ModelForm):
    class Meta:
        model = ApplicationSetting
        fields = '__all__'
        widgets = {
            'setting_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'value': forms.Textarea(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {
            'class_assigned': forms.Select(attrs={'class': 'form-control border-input'}),
            'subject': forms.Select(attrs={'class': 'form-control border-input'}),
            'teacher': forms.Select(attrs={'class': 'form-control border-input'}),
            'topic': forms.Select(attrs={'class': 'form-control border-input'}),
            'lesson_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control border-input'}),
        }


class SchedulingSettingForm(forms.ModelForm):
    class Meta:
        model = SchedulingSetting
        fields = '__all__'
        widgets = {
            'setting_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'value': forms.Textarea(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input'}),
        }


class CertificateAwardForm(forms.ModelForm):
    class Meta:
        model = CertificateAward
        fields = '__all__'
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'award_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input'}),
            'awarded_by': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'date_awarded': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = '__all__'
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'min_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class TransactionSettingForm(forms.ModelForm):
    class Meta:
        model = TransactionSetting
        fields = '__all__'
        widgets = {
            'setting_name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
