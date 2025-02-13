from django.urls import path
from . import views

urlpatterns = [
    path("", views.academics, name="academics"),
    path('grades/', views.grades, name="grades"),
    path('exams/', views.ExamList.as_view(), name = "exams"),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:pk>/edit/', views.exam_update, name='exam_update'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('subjects/', views.subjects, name="subjects"),
    path('register/grade/', views.RegisterGrade.as_view(), name='register_grade'),
    path('register/subject/', views.RegisterSubject.as_view(), name='register_subject'),
    path('register/curriculum/', views.RegisterCurriculum.as_view(), name='register_curriculum'),
    path('register/topic/', views.RegisterTopic.as_view(), name='register_topic'),
    path('upload/exam/', views.UploadExamView.as_view(), name='upload_exam'),
    path('upload/notes/', views.UploadNotesView.as_view(), name='upload_notes'),
    path('upload/marks/', views.RegisterStudentMarksView.as_view(), name='register-student-marks'),
]