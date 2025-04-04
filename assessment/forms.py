from django import forms
from .models import *


class TopicsForm(forms.ModelForm):
    class Meta:
        model = Topics
        fields = ["name",  "grade", "subject",]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border-input", "placeholder": "Topic"}),
            "grade": forms.Select(attrs={"class": "form-control border-input"}),
            "subject": forms.Select(attrs={"class": "form-control border-input"}),

        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["term_exam", 'grade', 'subject', "topic",
                  'question_number',   'max_score']
        widgets = {
            'term_exam': forms.Select(attrs={'class': 'form-control border-input'}),
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'subject': forms.Select(attrs={'class': 'form-control border-input', 'id': 'subject-select'}),
            'topic': forms.Select(attrs={'class': 'form-control border-input'}),
            'question_number': forms.TextInput(attrs={'class': 'form-control border-input'}),

            'max_score': forms.NumberInput(attrs={'class': 'form-control border-input'})
        }


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ['grade', 'student', 'subject', 'topic', 'question', 'score']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-control border-input', 'id': 'grade-select'}),
            'student': forms.Select(attrs={'class': 'form-control border-input', 'id': 'student-select'}),
            'subject': forms.Select(attrs={'class': 'form-control border-input', 'id': 'subject-select'}),
            'topic': forms.Select(attrs={'class': 'form-control border-input', 'id': 'topic-select'}),
            'question': forms.Select(attrs={'class': 'form-control border-input', 'id': 'question-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control border-input'}),
        }
