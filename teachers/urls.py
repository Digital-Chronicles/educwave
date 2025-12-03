from django.urls import path
from .views import *
from . import views
app_name = 'teachers' 

urlpatterns = [
    path('teachers-lists', views.TeacherList.as_view(), name= 'teachers'),
    path("user/create/", views.create_user_account, name="create_user_account"),
    path('register/teacher/details/', RegisterTeacherDetails.as_view(), name="teacher_details"),
    path('register/teacher/payroll/<int:pk>/', Teacher_Payroll.as_view(), name="teacher_payroll"),
    path('register/teacher/education_background/<int:pk>/', Teacher_EducationBackground.as_view(), name="teacher_educationbackground"),
    path('register/teacher/employmenthistory/<int:pk>/', Teacher_EmploymentHistory.as_view(), name="teacher_employmenthistory"),
    path('register/teacher/nextofkin/<int:pk>/', Teacher_Next_of_Kin.as_view(), name="teacher_nextofkin"),
    path('register/teacher/currentemployment/<int:pk>/', Teacher_Current_Employment.as_view(), name="teacher_currentemployment"),

    # Teacher Detail
    path('details/<str:id>/', views.teacher_details, name = "teacher_details"),
    path('', views.teacher_dashboard, name='dashboard'),
    path('marks/quick-entry/', views.quick_mark_entry, name='quick_mark_entry'),
    path('marks/bulk-upload/', views.bulk_marks_upload, name='bulk_upload'),
    path('', views.teacher_dashboard, name='dashboard'),
    path('marks/quick-entry/', views.quick_mark_entry, name='quick_mark_entry'),
    path('marks/bulk-upload/', views.bulk_marks_upload, name='bulk_upload'),
    path('reports/', views.teacher_reports, name='reports'),
    path('reports/class/<int:class_id>/', views.class_reports, name='class_reports'),
    path('my-classes/', views.my_classes, name='my_classes'),
    path('profile/', views.teacher_profile, name='profile'),
    path('download-template/<int:class_id>/', views.download_class_template, name='download_class_template'),
]