from django import forms
from django_select2 import forms as s2forms
from .models import StudentTuitionDescription, FeeTransaction, SchoolFees
from academic.models import Grade
from students.models import Student

# Custom Widgets
class StudentWidget(s2forms.ModelSelect2Widget):
    model = Student
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "registration_id__icontains",
        "admission_number__icontains"
    ]

class GradeWidget(s2forms.ModelSelect2Widget):
    model = Grade
    search_fields = ["name__icontains", "code__icontains"]

class SchoolFeesWidget(s2forms.ModelSelect2Widget):
    model = SchoolFees
    search_fields = [
        "grade__name__icontains",
        "description__icontains",
        "grade__code__icontains"
    ]

class StudentTuitionWidget(s2forms.ModelSelect2Widget):
    model = StudentTuitionDescription
    search_fields = [
        "student__first_name__icontains",
        "student__last_name__icontains",
        "student__registration_id__icontains"
    ]

# Payment Choices
PAYMENT_METHOD_CHOICES = (
    ('', '---------'),
    ('cash', 'Cash'),
    ('bank', 'Bank Transfer'),
    ('card', 'Credit/Debit Card'),
    ('mobile', 'Mobile Money'),
)

STATUS_CHOICES = (
    ('', '---------'),
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('partial', 'Partial Payment'),
    ('overdue', 'Overdue'),
)

# Base Form Styling
class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (s2forms.Select2Widget, s2forms.Select2MultipleWidget)):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    'autocomplete': 'off'
                })

# Forms
class TuitionDescriptionForm(BaseForm):
    class Meta:
        model = StudentTuitionDescription
        fields = ['student', 'tuition', 'hostel', 'lunch', 'breakfast']
        widgets = {
            'student': StudentWidget(attrs={
                'data-placeholder': 'Search student by name or ID'
            }),
            'tuition': SchoolFeesWidget(attrs={
                'data-placeholder': 'Select fee structure'
            }),
            'hostel': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-blue-600 rounded focus:ring-blue-500'
            }),
            'lunch': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-blue-600 rounded focus:ring-blue-500'
            }),
            'breakfast': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-blue-600 rounded focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tuition'].queryset = SchoolFees.objects.select_related('grade')
        self.fields['student'].label = "Student"
        self.fields['tuition'].label = "Fee Structure"

class TransactionForm(BaseForm):
    amount_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'placeholder': '0.00'
        })
    )

    class Meta:
        model = FeeTransaction
        fields = ['student', 'amount_paid', 'payment_method', 'due_date', 'status', 'payment_reference', 'remarks']
        widgets = {
            'student': StudentTuitionWidget(attrs={
                'data-placeholder': 'Search student fee record'
            }),
            'payment_method': s2forms.Select2Widget(choices=PAYMENT_METHOD_CHOICES),
            'status': s2forms.Select2Widget(choices=STATUS_CHOICES),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_reference': forms.TextInput(attrs={
                'placeholder': 'Transaction reference number'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'student' in self.initial:
            student = self.initial['student']
            self.fields['amount_due'] = forms.DecimalField(
                initial=student.total_fee,
                disabled=True,
                required=False,
                widget=forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-2 border rounded-lg bg-gray-100'
                })
            )
            self.fields['amount_due'].label = "Total Fee Due"

class SchoolFeesForm(BaseForm):
    class Meta:
        model = SchoolFees
        fields = ['grade', 'tuitionfee', 'hostelfee', 'breakfastfee', 'lunchfee', 'description']
        widgets = {
            'grade': GradeWidget(attrs={
                'data-placeholder': 'Select grade level'
            }),
            'tuitionfee': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'hostelfee': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'breakfastfee': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'lunchfee': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Fee description...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['tuitionfee', 'hostelfee', 'breakfastfee', 'lunchfee']:
            self.fields[field].label = f"{self.fields[field].label} (₦)"
            self.fields[field].widget.attrs['min'] = '0'