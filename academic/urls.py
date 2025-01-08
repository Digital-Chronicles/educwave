from django.urls import path
from . import views

urlpatterns = [
    path("", views.academics, name="academics"),

    # Grades
    path('grades/', views.grades, name="grades"),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/edit/', views.exam_update, name='exam_update'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('subjects/', views.subjects, name="subjects"),
    path('register/grade/', views.RegisterGrade.as_view(), name='register_grade'),
    path('register/subject/', views.RegisterSubject.as_view(), name='register_subject'),
    path('register/curriculum/', views.RegisterCurriculum.as_view(), name='register_curriculum'),
    path('register/topic/', views.RegisterTopic.as_view(), name='register_topic'),
    path('register/exam/', views.RegisterExam.as_view(), name='register_exam'),
]