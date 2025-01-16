from django import forms
from .models import Grade, Subject, Curriculum, Topic, Exam, Notes
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError

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
            'grade_name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter grade name'}),
            'class_teacher': forms.Select(attrs={'class': 'form-control border-input'}),
        }
        help_texts = {
            'class_teacher': 'Assign a teacher to this grade (optional).'
        }

# Form for Subject model
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'curriculum']
        labels = {
            'name': 'Subject Name',
            'description': 'Description',
            'curriculum': 'Curriculum'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter subject name'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide a brief description', 'rows': 4}),
            'curriculum': forms.Select(attrs={'class': 'form-control border-input'}),
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
            'name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter curriculum name'}),
            'objectives': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'List curriculum objectives', 'rows': 4}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Outline learning outcomes', 'rows': 4}),
        }

# Form for Topic model
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['subject', 'name', 'description', 'order']
        labels = {
            'subject': 'Related Subject',
            'name': 'Topic Name',
            'description': 'Description',
            'order': 'Order'
        }
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control border-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter topic name'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide topic details', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'form-control border-input'}),
        }

# Form for Exam model
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['subject', 'date', 'duration_minutes', 'file', 'description', 'grade', 'created_by']
        labels = {
            'subject': 'Subject',
            'date': 'Exam Date',
            'duration_minutes': 'Duration (Minutes)',
            'file': 'Upload Exam File',
            'description': 'Description',
            'grade': 'Grade',
            'created_by': 'Created By'
        }
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control border-input'}),
            'date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter duration in minutes'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide additional details', 'rows': 4}),
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'created_by': forms.Select(attrs={'class': 'form-control border-input'}),
        }
        help_texts = {
            'file': 'You can upload PDF, DOCX, or PPTX files.'
        }
        error_messages = {
            'duration_minutes': {'required': 'Please specify the duration of the exam in minutes.'}
        }

# Form for Notes model
class NotesForm(forms.ModelForm):
    # Use CKEditorWidget for notes_content
    notes_content = forms.CharField(
        widget=CKEditorWidget(attrs={'class': 'form-control border-input'}),
        label='Notes Content',
    )

    # Use ModelMultipleChoiceField for the 'topics' field
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
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
            'subject': forms.Select(attrs={'class': 'form-control border-input'}),
            'topics': forms.SelectMultiple(attrs={'class': 'form-control border-input'}),
            'notes_file': forms.ClearableFileInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide notes details', 'rows': 4}),
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'created_by': forms.Select(attrs={'class': 'form-control border-input'}),
        }

        help_texts = {
            'notes_file': 'You can upload PDF, DOCX, or PPTX files for the notes.',
            'description': 'Provide any additional details or context for the notes.',
        }

    # Custom validation for notes file extension
    def clean_notes_file(self):
        notes_file = self.cleaned_data.get('notes_file')
        if notes_file:
            file_extension = notes_file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'docx', 'pptx']
            if file_extension not in allowed_extensions:
                raise ValidationError('Only PDF, DOCX, or PPTX files are allowed.')
        return notes_file