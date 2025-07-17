from .models import FeeTransaction, StudentTuitionDescription
from django import forms
from .models import *

class SchoolfeesForm(forms.ModelForm):
    class Meta:
        model = SchoolFees
        fields = ['grade', 'tuitionfee', 'hostelfee', 'breakfastfee', 'lunchfee', 'description']
        widgets = {
            'grade': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
            'tuitionfee': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
            'hostelfee': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
            'breakfastfee': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
            'lunchfee': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
        }


class OtherSchoolPaymentForm(forms.ModelForm):
    class Meta:
        model = OtherSchoolPayments
        fields = ['grade', 'fees_type', 'amount', 'unique_code', 'description']
        widgets = {
            'grade': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'fees_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'unique_code': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
        }
     
    
class TransportForm(forms.ModelForm):
    class Meta:
        model = TransportFee
        fields = ['location', 'amount']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
        }      

 
class StudentTuitionDescriptionForm(forms.ModelForm):
    class Meta:
        model = StudentTuitionDescription
        fields = ['hostel', 'lunch', 'breakfast']
        widgets = {
            'hostel': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'lunch': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'breakfast': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }


# # class FeeTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FeeTransaction
#         fields = [
#             'student','amount_paid', 'payment_method', 'due_date',
#             'status', 'last_payment_date', 'payment_reference', 'receipt_url', 'remarks'
#         ]
#         widgets = {
#             'student': forms.Select(attrs={'class': 'form-control border-input'}),
           
#             'amount_paid': forms.NumberInput(attrs={'class': 'form-control border-input', 'step': '0.01'}),
#             'payment_method': forms.Select(attrs={'class': 'form-control border-input'}),
#             'due_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
#             'status': forms.Select(attrs={'class': 'form-control border-input'}),
#             'last_payment_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
#             'payment_reference': forms.TextInput(attrs={'class': 'form-control border-input'}),
#             'receipt_url': forms.URLInput(attrs={'class': 'form-control border-input'}),
#             'remarks': forms.Textarea(attrs={'class': 'form-control border-input', 'rows': 3}),
#         }

class FeeTransactionForm(forms.ModelForm):
    class Meta:
        model = FeeTransaction
        fields = [
            'grade', 'student', 'amount_paid', 'payment_method', 'due_date',
            'status', 'last_payment_date', 'payment_reference', 'receipt_url', 'remarks'
        ]
        widgets = {
            'grade': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'student': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'due_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'last_payment_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md', 'type': 'date'}),
            'payment_reference': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'receipt_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student'].queryset = StudentTuitionDescription.objects.none()

        if 'grade' in self.data:
            try:
                grade_id = int(self.data.get('grade'))
                self.fields['student'].queryset = StudentTuitionDescription.objects.filter(
                    student__current_grade=grade_id
                ).select_related('student')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['student'].queryset = StudentTuitionDescription.objects.filter(
                student=self.instance.student.student
            )
