from .models import *
from django import forms

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'user','year_of_entry','first_name','last_name','gender','profile_picture','school'
        ]
        widgets={
            'user': forms.Select(attrs={'class':'form-select border-input'}),
            'year_of_entry': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'gender': forms.Select(attrs={'class': 'form-select border-input'}),
            'school': forms.Select(attrs={'class':'form-select border-input'}),
            'profile_picture': forms.URLInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter profile picture URL'}),
            
    }


class PayrollInformationForm(forms.ModelForm):
    class Meta:
        model = PayrollInformation
        fields = ['salary', 'bank_name', 'account_number', 'tax_identification_number', 'nssf_number', 'payment_frequency']
        
        widgets = {
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Salary'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Bank Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Account Number'}),
            'tax_identification_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TIN'}),
            'nssf_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter NSSF Number'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-select'}),
        }

class EducationBackgroundForm(forms.ModelForm):
    class Meta:
        model = EducationBackground
        fields = ['education_award', 'institution', 'graduation_year', 'result_obtained', 'additional_certifications']
        widgets = {
            'education_award': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Award'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Institution'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Graduation Year'}),
            'result_obtained': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Result'}),
            'additional_certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Additional Certifications'}),
        }

class EmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = EmploymentHistory
        fields = ['organization', 'department', 'role', 'start_date', 'end_date', 'responsibilities']
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Organization'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Role'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter Responsibilities'}),
        }

class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        fields = ['name', 'relationship', 'contact_number', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Relationship'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Address'}),
        }

class CurrentEmploymentForm(forms.ModelForm):
    class Meta:
        model = CurrentEmployment
        fields = ['position', 'department']
        widgets = {
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Position'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department'}),
        }



    
