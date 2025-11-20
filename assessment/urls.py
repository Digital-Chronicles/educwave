from django.urls import path
from . import views

from .upload_views import ExamResultsView, ExamResultsEntryView,SubjectTotalsEntryView,get_exams_by_term, SubjectTotalsSelectView, download_marks_template, upload_marks

app_name = 'assessment'

urlpatterns = [
    # Assessment Home
    path("", views.assessment_home, name="home"),   
    
    # Topic Management URLs
    path("topics/", views.topic_lists, name="topic_list"),
    path("topics/create/", views.record_topic, name="topic_create"),
    path('get_topics/', views.get_topics, name='get_topics'),
    path('get_subjects/', views.get_subjects, name='get_subjects'),

    # Question Management URLs
    path("questions/", views.record_question, name="question_list"),
    path("questions/create/", views.record_question, name="question_create"),
    path("get-subjects-by-grade/", views.get_subjects_by_grade, name="get_subjects_by_grade"),
    path("questions/get-topics/", views.get_topics_by_subject, name="get_topics"),
    
    # Results Management URLs
    path("results/", views.exam_results, name="result_list"),

    # Exam Results URLs
    path('exam-results/', ExamResultsView.as_view(), name='exam_results'),
    path('exam-results/entry/', ExamResultsEntryView.as_view(), name='exam_results_entry'),
    path('exam-results/download-template/', download_marks_template, name='download_marks_template'),
    path('exam-results/upload-marks/', upload_marks, name='upload_marks'),

    # Subject Totals Entry Flow
    path("exam-results/get-exams-by-term/", get_exams_by_term, name="get_exams_by_term"),

    path('exam-results/subject-totals/select/', SubjectTotalsSelectView.as_view(), name='subject_totals_select'),
    path('exam-results/subject-totals/', SubjectTotalsEntryView.as_view(), name='subject_totals_entry'),

    
    # Mark Sheet
    path("marksheet/", views.marksheet_list, name="marksheet_list"),  # list of grades
    path("marksheet_details/<int:grade_id>/", views.marksheet_detail, name="marksheet_detail"),  
    








   
   

]