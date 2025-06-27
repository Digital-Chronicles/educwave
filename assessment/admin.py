from django.contrib import admin
from .models import  Topics, Question, ExamResult



@admin.register(Topics)
class TopicsAdmin(admin.ModelAdmin):
    list_display=("name","subject","grade")
    search_fields = ("name","subject", "grade")
    list_filter =("subject", "grade")
    



@admin.register(Question)
class Question(admin.ModelAdmin):
    list_display = ("question_number", "topic", "term_exam", "max_score")
    search_fields=("topic","term_exam","grade")
    list_filter=("question_number","topic")

@admin.register(ExamResult)
class ExamResult(admin.ModelAdmin):
    list_display = ("student", "grade", "subject","topic", "question", "score")
    search_fields = ("student", "subject", "question")
    list_filter = ("question",)
    