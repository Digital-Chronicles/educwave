from django import forms
from django.urls import reverse_lazy
from .models import *
from academic.models import Grade, Subject
from students.models import Student

class TopicsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty label for better UX
        self.fields['grade'].empty_label = "Select Grade"
        self.fields['subject'].empty_label = "Select Subject"

    class Meta:
        model = Topics
        fields = ["name", "grade", "subject"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "placeholder": "Topic"
            }),
            "grade": forms.Select(attrs={
                "class": "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                "hx-get": "/get_subjects/",  # For dynamic subject loading
                "hx-target": "#id_subject",
            }),
            "subject": forms.Select(attrs={
                "class": "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            }),
        }


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set empty labels
        self.fields['term_exam'].empty_label = "Select Exam Session"
        self.fields['grade'].empty_label = "Select Grade"
        self.fields['subject'].empty_label = "Select Subject"
        self.fields['topic'].empty_label = "Select Topic"
        
        # Make fields required
        for field in ['term_exam', 'grade', 'subject', 'topic']:
            self.fields[field].required = True
        
        # Always show all subjects
        self.fields['subject'].queryset = Subject.objects.all()
        
        # Limit topic choices based on selected subject and grade
        if 'subject' in self.data and 'grade' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                grade_id = int(self.data.get('grade'))
                self.fields['topic'].queryset = Topics.objects.filter(
                    subject_id=subject_id,
                    grade_id=grade_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['topic'].queryset = Topics.objects.filter(
                subject=self.instance.subject,
                grade=self.instance.grade
            )
        else:
            self.fields['topic'].queryset = Topics.objects.none()

    class Meta:
        model = Question
        fields = ["term_exam", "exam_type", 'grade', 'subject', "topic", 'question_number', 'max_score']
        widgets = {
            'term_exam': forms.Select(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            'exam_type': forms.Select(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            }),
            'grade': forms.Select(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'subject': forms.Select(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'topic': forms.Select(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'question_number': forms.TextInput(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                'placeholder': "e.g. 1, 2a, 3b, etc."
            }),
            'max_score': forms.NumberInput(attrs={
                'class': "w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                'min': 1,
                'max': 100,
            }),
        }


class ExamResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set empty labels
        self.fields['grade'].empty_label = "Select Grade"
        self.fields['student'].empty_label = "Select Student"
        self.fields['subject'].empty_label = "Select Subject"
        self.fields['topic'].empty_label = "Select Topic"
        self.fields['question'].empty_label = "Select Question"
        
        # Limit querysets dynamically
        if 'grade' in self.data:
            try:
                grade_id = int(self.data.get('grade'))
                self.fields['student'].queryset = Student.objects.filter(grade_id=grade_id).order_by('first_name')
                self.fields['subject'].queryset = Subject.objects.filter(grade__id=grade_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['student'].queryset = self.instance.grade.student_set.order_by('first_name')
            self.fields['subject'].queryset = self.instance.grade.subject_set.order_by('name')

        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['topic'].queryset = Topics.objects.filter(subject_id=subject_id).order_by('name')
                self.fields['question'].queryset = Question.objects.filter(subject_id=subject_id).order_by('question_number')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['topic'].queryset = self.instance.subject.assessment_topics.order_by('name')
            self.fields['question'].queryset = self.instance.subject.subject_question.order_by('question_number')

    class Meta:
        model = ExamResult
        fields = ['grade', 'student', 'subject', 'topic', 'question', 'score']
        widgets = {
            'grade': forms.Select(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'id': 'id_grade',
                'hx-get': "/load_students_subjects/",
                'hx-target': "#id_student, #id_subject",
            }),
            'student': forms.Select(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'id': 'id_student',
            }),
            'subject': forms.Select(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'id': 'id_subject',
                'hx-get': "/load_topics_questions/",
                'hx-target': "#id_topic, #id_question",
            }),
            'topic': forms.Select(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'id': 'id_topic',
            }),
            'question': forms.Select(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'id': 'id_question',
            }),
            'score': forms.NumberInput(attrs={
                'class': "w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500",
                'min': 0,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        score = cleaned_data.get('score')
        
        if question and score is not None:
            if score > question.max_score:
                raise forms.ValidationError({
                    'score': f"Score cannot exceed the maximum score of {question.max_score} for this question"
                })
        return cleaned_data
    
