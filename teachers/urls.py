from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.TeacherList.as_view(), name= 'teachers'),
    path("user/create/", views.create_user_account, name="create_user_account"),
    path('register/teacher/details/', RegisterTeacherDetails.as_view(), name="teacher_details"),
    path('register/teacher/payroll/<int:pk>/', Teacher_Payroll.as_view(), name="teacher_payroll"),
    path('register/teacher/education_background/<int:pk>/', Teacher_EducationBackground.as_view(), name="teacher_educationbackground"),
    path('register/teacher/employmenthistory/<int:pk>/', Teacher_EmploymentHistory.as_view(), name="teacher_employmenthistory"),
    path('register/teacher/nextofkin/<int:pk>/', Teacher_Next_of_Kin.as_view(), name="teacher_nextofkin"),
    path('register/teacher/currentemployment/<int:pk>/', Teacher_Current_Employment.as_view(), name="teacher_currentemployment"),

    # Teacher Detail
    path('details/<str:id>/', views.teacher_details, name = "teacher_details"),
  
]