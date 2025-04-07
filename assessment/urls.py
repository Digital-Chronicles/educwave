from django.urls import path
from . import views

urlpatterns = [
    path("", views.Assessment, name="assess"),
    # RECORD TOPICS
    path('tget-subjects/', views.get_Tsubjects_by_grade,
         name='get_subjects_by_grade'),

    path('record/topic/', views.RecordTopic, name='topic'),
    path("all/topics/", views.topic_lists, name="all_topics"),


    # RECORD QUESTION
    path('record/question/', views.RecordQuestion, name="question"),
    path('qget-subjects/', views.get_Qsubjects_by_grade,
         name='get_subjects_by_grade'),
    path('qget-topics-by-subject/', views.get_Qtopics_by_subject,
         name='get_topics_by_subject'),


    # RECORD RESULTS
    path('results', views.Exam_Results, name='results'),
    path('bulk', views.bulk_exam_entry, name="bulk-items"),
    path('bget-subjects/', views.bget_subjects_by_grade,
         name='get_subjects_by_grade'),

]
