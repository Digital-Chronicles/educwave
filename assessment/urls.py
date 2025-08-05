from django.urls import path
from . import views
from .upload_views import ExamResultsView, ExamResultsEntryView, download_marks_template, upload_marks

app_name = 'assessment'

urlpatterns = [
    # Assessment Home
    path("", views.assessment_home, name="home"),
    
    # Topic Management URLs
    path("topics/", views.topic_lists, name="topic_list"),
    path("topics/create/", views.record_topic, name="topic_create"),
    path('get_topics/', views.get_topics, name='get_topics'),

    # Question Management URLs
    path("questions/", views.record_question, name="question_list"),
    path("questions/create/", views.record_question, name="question_create"),
    path("questions/get-topics/", views.get_topics_by_subject, name="question_topic_ajax"),
    
    # Results Management URLs
    path("results/", views.exam_results, name="result_list"),

    # Exam Results URLs
    path('exam-results/', ExamResultsView.as_view(), name='exam_results'),
    path('exam-results/entry/', ExamResultsEntryView.as_view(), name='exam_results_entry'),
    path('exam-results/download-template/', download_marks_template, name='download_marks_template'),
    path('exam-results/upload-marks/', upload_marks, name='upload_marks'),
]