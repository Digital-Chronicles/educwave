# finance/forms.py

from django import forms
from .models import StudentTuitionDescription, FeeTransaction, SchoolFees


# ✅ Reusable Tailwind class sets
TAILWIND_INPUT = (
    "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm "
    "shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 "
    "focus:border-indigo-500 placeholder-gray-400"
)

TAILWIND_SELECT = (
    "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm "
    "shadow-sm bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 "
    "focus:border-indigo-500"
)

TAILWIND_TEXTAREA = (
    "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm "
    "shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 "
    "focus:border-indigo-500 placeholder-gray-400 min-h-[90px]"
)

TAILWIND_CHECKBOX = (
    "h-4 w-4 rounded border-gray-300 text-indigo-600 "
    "focus:ring-indigo-500 focus:ring-offset-0"
)


class StudentTuitionDescriptionForm(forms.ModelForm):
    """
    Finance user only selects options (hostel, lunch, breakfast).
    The actual tuition (SchoolFees) is auto-set from the student's current_grade.
    """
    class Meta:
        model = StudentTuitionDescription
        fields = ['hostel', 'lunch', 'breakfast']
        widgets = {
            'hostel': forms.CheckboxInput(attrs={"class": TAILWIND_CHECKBOX}),
            'lunch': forms.CheckboxInput(attrs={"class": TAILWIND_CHECKBOX}),
            'breakfast': forms.CheckboxInput(attrs={"class": TAILWIND_CHECKBOX}),
        }

    def __init__(self, *args, **kwargs):
        # Expect the view to send student instance
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()

        if not self.student:
            raise forms.ValidationError(
                "Student is required to set tuition description."
            )

        # Make sure the student has a current grade
        if not self.student.current_grade:
            raise forms.ValidationError(
                "This student has no current grade set. "
                "Please assign a grade to the student first."
            )

        # Make sure there is a SchoolFees record for this student's current grade
        try:
            school_fees = SchoolFees.objects.get(grade=self.student.current_grade)
        except SchoolFees.DoesNotExist:
            raise forms.ValidationError(
                f"No SchoolFees found for grade {self.student.current_grade}. "
                "Please create it in the finance module first."
            )

        # Store it so we can reuse in save()
        self.school_fees = school_fees
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.student
        instance.tuition = self.school_fees  # from clean()
        if commit:
            instance.save()
        return instance


class FeeTransactionForm(forms.ModelForm):
    """
    Form for recording a single fee payment (FeeTransaction).
    The tuition_description (StudentTuitionDescription instance) is passed in from the view.
    """
    class Meta:
        model = FeeTransaction
        fields = [
            'amount_paid',
            'payment_method',
            'term',
            'academic_year',
            'due_date',
            'remarks',
        ]
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "e.g. 150000",
                "step": "0.01",
                "min": "0"
            }),
            'payment_method': forms.Select(attrs={
                "class": TAILWIND_SELECT,
            }),
            'term': forms.Select(attrs={
                "class": TAILWIND_SELECT,
            }),
            'academic_year': forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "e.g. 2025/2026",
            }),
            'due_date': forms.DateInput(attrs={
                "class": TAILWIND_INPUT,
                "type": "date",
            }),
            'remarks': forms.Textarea(attrs={
                "class": TAILWIND_TEXTAREA,
                "placeholder": "Optional notes, reference, receipt number…",
            }),
        }

    def __init__(self, *args, **kwargs):
        # Expect the tuition description instance
        self.tuition_description = kwargs.pop('tuition_description', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if not self.tuition_description:
            raise forms.ValidationError(
                "Tuition description is required to record a payment."
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.tuition_description

        # grade is auto-set in FeeTransaction.save() if missing,
        # but we can set it here explicitly for safety
        if not instance.grade:
            instance.grade = self.tuition_description.tuition.grade

        if commit:
            instance.save()
        return instance
