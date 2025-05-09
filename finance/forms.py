from .models import FeeTransaction, StudentTuitionDescription
from django import forms
from .models import *

class SchoolfeesForm(forms.ModelForm):
    class Meta:
        model= SchoolFees
        fields =[ 'grade','tuitionfee','hostelfee','breakfastfee','lunchfee','description'

        ]
        widgets={
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'tuitionfee': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'hostelfee': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'breakfastfee': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'lunchfee': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input'}),

        }

class OtherSchoolPaymentForm(forms.ModelForm):
    class Meta:
        model= OtherSchoolPayments
        fields =[ 'grade','fees_type','amount','unique_code','description'

        ]
        widgets={
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'fees_type': forms.Select(attrs={'class': 'form-control border-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'unique_code': forms.NumberInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input'}),

        }        
    
class TransportForm(forms.ModelForm):
    class Meta:
        model= TransportFee
        fields =[ 'location','amount'

        ]
        widgets={
            'location': forms.TextInput(attrs={'class': 'form-control border-input'}),
          
            'amount': forms.NumberInput(attrs={'class': 'form-control border-input'})
           

        }       

 
class StudentTuitionDescriptionForm(forms.ModelForm):
    class Meta:
        model = StudentTuitionDescription
        fields = [ 'hostel', 'lunch', 'breakfast']  
        widgets = {
            
            # 'tuition': forms.Select(attrs={'class': 'form-control border-input'}),
            'hostel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  
            'lunch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  
            'breakfast': forms.CheckboxInput(attrs={'class': 'form-check-input'})   }                 



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
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'student': forms.Select(attrs={'class': 'form-control border-input'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control border-input', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control border-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control border-input'}),
            'last_payment_date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'payment_reference': forms.TextInput(attrs={'class': 'form-control border-input'}),
            'receipt_url': forms.URLInput(attrs={'class': 'form-control border-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control border-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure the student field is linked to StudentTuitionDescription, not Student
        self.fields['student'].queryset = StudentTuitionDescription.objects.none()

        if 'grade' in self.data:
            try:
                grade_id = int(self.data.get('grade'))
                self.fields['student'].queryset = StudentTuitionDescription.objects.filter(
                    student__current_grade=grade_id
                ).select_related('student')
            except (ValueError, TypeError):
                pass  # Ignore invalid values
        elif self.instance.pk:
            self.fields['student'].queryset = StudentTuitionDescription.objects.filter(
                student=self.instance.student.student
            )
