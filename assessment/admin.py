from django.contrib import admin
from .models import  Topics, Question, ExamResult



@admin.register(Topics)
class TopicsAdmin(admin.ModelAdmin):
    list_display=("name","subject","grade")
    search_fields = ("name","subject", "grade")
    list_filter =("subject", "grade")
    



@admin.register(Question)
class Question(admin.ModelAdmin):
    list_display = ('grade',"subject","question_number", "topic", "exam_type","term_exam", "max_score")
    search_fields=("topic","term_exam","grade","subject")
    list_filter=('grade',"exam_type","question_number","topic","subject")

@admin.register(ExamResult)
class ExamResult(admin.ModelAdmin):
    list_display = ("student", "grade","exam_session" ,"subject","topic", "question", "score")
    search_fields = ("student", "subject", "question")
    list_filter = ("student","question", "grade","exam_session")
    