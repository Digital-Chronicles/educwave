from django import forms
from .models import Grade, Subject, Curriculum, Topic, Exam

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
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide a brief description'}),
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
            'objectives': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'List curriculum objectives'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Outline learning outcomes'}),
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
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide topic details'}),
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
            'file': 'Upload File',
            'description': 'Description',
            'grade': 'Grade',
            'created_by': 'Created By'
        }
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control border-input'}),
            'date': forms.DateInput(attrs={'class': 'form-control border-input', 'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control border-input', 'placeholder': 'Enter duration in minutes'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control border-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-input', 'placeholder': 'Provide additional details'}),
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'created_by': forms.Select(attrs={'class': 'form-control border-input'}),
        }
