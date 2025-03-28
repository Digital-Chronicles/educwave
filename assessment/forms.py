from django import forms
from .models import *


class TopicsForm(forms.ModelForm):
    class Meta:
        model = Topics
        fields = ["name", "subject", "grade"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border-input", "placeholder": "Topic"}),
            "subject": forms.Select(attrs={"class": "form-control border-input"}),
            "grade": forms.Select(attrs={"class": "form-control border-input"}),
        }
        
    
class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields = ["term_exam", 'question_number', "topic", 'grade', 'max_score']
        widgets ={
            'term_exam':forms.Select(attrs={'class':'form-control border-input'}),
            'topic':forms.Select(attrs={'class':'form-control border-input'}),
            'question_number':forms.TextInput(attrs={'class':'form-control border-input'}),
            'grade':forms.Select(attrs={'class':'form-control border-input'}),
            'max_score':forms.NumberInput(attrs={'class':'form-control border-input'})
        }    


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ['grade', 'student', 'topic', 'question', 'score',]
        widgets={
            'grade': forms.Select(attrs={'class': 'form-control border-input'}),
            'topic': forms.Select(attrs={'class': 'form-control border-input'}),
            'student':forms.Select(attrs={'class':'form-control border-input'}),
            'question':forms.Select(attrs={'class':'form-control border-input'}),
            'score':forms.NumberInput(attrs={'class':'form-control border-input'})
            
        }    