from django import forms
from .models import Grade, Subject, Curriculum, Exam, Notes
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget
from assessment.models import Topics

# Form for Grade model
class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['grade_name', 'class_teacher']
        labels = {
            'grade_name': 'Grade Name',
            'class_teacher': 'Class Teacher'
        }
        widgets = {
            'grade_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter grade name'
            }),
            'class_teacher': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
        help_texts = {
            'class_teacher': 'Assign a teacher to this grade (optional).'
        }

# Form for Subject model
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code','grade', 'description', 'curriculum']
        labels = {
            'name': 'Subject Name',
            'code': 'Code',
            'grade' : 'Grade',
            'description': 'Description',
            'curriculum': 'Curriculum'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter subject name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter subject code'
            }),
            'grade': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Provide a brief description',
                'rows': 4
            }),
            'curriculum': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

# Form for Curriculum model
class CurriculumForm(forms.ModelForm):
    class Meta:
        model = Curriculum
        fields = ['name', 'objectives', 'learning_outcomes']
        labels = {
            'name': 'Curriculum Name',
            'objectives': 'Objectives',
            'learning_outcomes': 'Learning Outcomes'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter curriculum name'
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'List curriculum objectives',
                'rows': 4
            }),
            'learning_outcomes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Outline learning outcomes',
                'rows': 4
            }),
        }


# Form for Exam model
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['subject', 'date', 'duration_minutes', 'file', 'description', 'grade']
        labels = {
            'subject': 'Subject',
            'date': 'Exam Date',
            'duration_minutes': 'Duration (Minutes)',
            'file': 'Upload Exam File',
            'description': 'Description',
            'grade': 'Grade',
        }
        widgets = {
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter duration in minutes'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Provide additional details',
                'rows': 4
            }),
            'grade': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
        help_texts = {
            'file': 'You can upload PDF, DOCX, or PPTX files.'
        }
        error_messages = {
            'duration_minutes': {'required': 'Please specify the duration of the exam in minutes.'}
        }

# Form for Notes model
class NotesForm(forms.ModelForm):
    notes_content = forms.CharField(
        widget=CKEditor5Widget(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        }),
        label='Notes Content',
    )

    topics = forms.ModelMultipleChoiceField(
        queryset=Topics.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        }),
        required=True,
        label='Topics'
    )

    class Meta:
        model = Notes
        fields = ['subject', 'topics', 'notes_file', 'notes_content', 'description', 'grade']

        labels = {
            'subject': 'Subject',
            'topics': 'Topics',
            'notes_file': 'Upload Notes File',
            'description': 'Description',
            'grade': 'Grade',
        }

        widgets = {
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'notes_file': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Provide notes details',
                'rows': 4
            }),
            'grade': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

        help_texts = {
            'notes_file': 'You can upload PDF, DOCX, or PPTX files for the notes.',
            'description': 'Provide any additional details or context for the notes.',
        }

    def clean_notes_file(self):
        notes_file = self.cleaned_data.get('notes_file')
        if notes_file:
            file_extension = notes_file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'docx', 'pptx']
            if file_extension not in allowed_extensions:
                raise ValidationError('Only PDF, DOCX, or PPTX files are allowed.')
        return notes_file