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
    path('upload/exam/', views.UploadExamView.as_view(), name='upload_exam'),
    path('upload/notes/', views.UploadNotesView.as_view(), name='upload_notes'),
    path('reports/mark-summary/', views.mark_summary_report, name='mark_summary_report'),
    path('reports/mark-summary/<int:pk>/', views.StudentMarkSummaryDetailView.as_view(), name='mark_summary_detail'),
    path('reports/export-csv/', views.export_mark_summary_csv, name='export_mark_summary_csv'),
    path('reports/student-progress/<int:student_id>/', views.StudentProgressReportView.as_view(), name='student_progress_report'),
    path('term-exams/', views.TermExamListView.as_view(), name='term_exam_list'),
    path('term-exams/<int:pk>/', views.TermExamDetailView.as_view(), name='term_exam_detail'),

    # Report URL
    path('reports/student-term-report/<int:student_id>/', views.student_term_report, name='student_term_report'),
    #Bulk entry to save time

    
]