from django.urls import path
from . import views

urlpatterns = [
    path("", views.Assessment, name="assess"),
    
    path('record/topic/', views.RecordTopic, name='topic'),
    path("all/topics/", views.TopicLists,name="all_topics"),
    
    path('record/question/', views.RecordQuestion,name="question"),
    
    path('exam/result',views.record_result, name='exam_result'),
    path('get-students/', views.get_students_by_grade, name='get-students'),
    path('get-topics/', views.get_topics_by_grade, name='get-topics'),
    path('get-questions/', views.get_questions_by_topic, name='get-questions'),
    path('results', views.Exam_Results, name='results')
    
]