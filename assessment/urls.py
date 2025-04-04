from django.urls import path
from . import views

urlpatterns = [
    path("", views.Assessment, name="assess"),
    #RECORD TOPICS
    path('tget-subjects/', views.get_Tsubjects_by_grade,
         name='get_subjects_by_grade'),

    path('record/topic/', views.RecordTopic, name='topic'),
    path("all/topics/", views.topic_lists, name="all_topics"),
    
    
    #RECORD QUESTION
    path('record/question/', views.RecordQuestion,name="question"),
    path('qget-subjects/', views.get_Qsubjects_by_grade,
         name='get_subjects_by_grade'),
    path('qget-topics-by-subject/', views.get_Qtopics_by_subject,
         name='get_topics_by_subject'),

    
    #RECORD RESULTS
    path('get-students/', views.get_students_by_grade,
         name='get_students_by_grade'),
    path('get-subjects/', views.get_subjects_by_grade,
         name='get_subjects_by_grade'),
    path('get-topics-by-subject/', views.get_topics_by_subject,
         name='get_topics_by_subject'),
    path('get-questions/', views.get_questions_by_topic,
         name='get_questions_by_topic'),

    
    
    path('exam/result', views.record_result, name='exam_result'),
    path('results', views.Exam_Results, name='results')
    
]