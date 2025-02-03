from .models import *
from django import forms

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'user','year_of_entry','first_name','last_name','nin_number', 'gender','profile_picture','school'
        ]
        widgets={
            'user': forms.Select(attrs={'class': 'form-control border-input'}),
            'year_of_entry': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'nin_number': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'gender': forms.Select(attrs={'class': 'form-control border-input'}),
            'school': forms.Select(attrs={'class': 'form-control border-input'}),
            'profile_picture': forms.URLInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter profile picture URL'}),
            
    }


class PayrollInformationForm(forms.ModelForm):
    class Meta:
        model = PayrollInformation
        fields = ['salary', 'bank_name', 'account_number', 'tax_identification_number', 'nssf_number', 'payment_frequency']
        
        widgets = {
            'salary': forms.NumberInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Salary'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Bank Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Account Number'}),
            'tax_identification_number': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter TIN'}),
            'nssf_number': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter NSSF Number'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-control border-input'}),
        }

class EducationBackgroundForm(forms.ModelForm):
    class Meta:
        model = EducationBackground
        fields = ['education_award', 'institution', 'graduation_year', 'result_obtained', 'additional_certifications']
        widgets = {
            'education_award': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Award'}),
            'institution': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Institution'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Graduation Year'}),
            'result_obtained': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Result'}),
            'additional_certifications': forms.Textarea(attrs={'class': 'form-control border-input', 'rows': 3, 'placeholder': 'Enter Additional Certifications'}),
        }

class EmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = EmploymentHistory
        fields = ['organization', 'department', 'role', 'start_date', 'end_date', 'responsibilities']
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Organization'}),
            'department': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Department'}),
            'role': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Role'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control border-input', 'rows': 4, 'placeholder': 'Enter Responsibilities'}),
        }

class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        fields = ['name', 'relationship', 'contact_number', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Relationship'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Contact Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Address'}),
        }

class CurrentEmploymentForm(forms.ModelForm):
    class Meta:
        model = CurrentEmployment
        fields = ['position', 'department']
        widgets = {
            'position': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Position'}),
            'department': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter Department'}),
        }



    
