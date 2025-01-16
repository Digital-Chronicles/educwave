from django import forms
from .models import Student, StudentAddress, CareTaker, StudentGrade

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 
            'last_name', 
            'date_of_birth',
            'gender', 
            'current_status', 
            'year_of_entry',
            'guardian_name', 
            'guardian_phone', 
            'father_name', 
            'father_phone', 
            'mother_name', 
            'mother_phone', 
            'profile_picture',
            'school',
        ]

        # Applying Bootstrap classes to form fields using widgets
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control border-input'}),
            'current_status': forms.Select(attrs={'class': 'form-control border-input'}),
            'year_of_entry': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'school': forms.Select(attrs={'class': 'form-control border-input'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'father_phone': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'mother_phone': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control border-input'}),
        }



class StudentAddressForm(forms.ModelForm):
    class Meta:
        model = StudentAddress
        fields = ['address', 'city', 'state', 'zip_code']
        
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Enter your address', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter your state'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter your zip code'}),
        }

class CareTakerForm(forms.ModelForm):
    class Meta:
        model = CareTaker
        fields = ['name', 'relationship', 'contact_number', 'email']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter caretaker name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter relationship'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter contact number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter email'}),
        }


class StudentGradeForm(forms.ModelForm):
    class Meta:
        model = StudentGrade
        fields = ['class_assigned', 'assigned_date']

        widgets = {
            'class_assigned': forms.Select(attrs={'class': 'form-control border-input'}),
            'assigned_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
        }
