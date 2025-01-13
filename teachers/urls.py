from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', teachers, name= 'teachers'),
    path('register/teacher/details', RegisterTeacherDetails.as_view(), name="teacher_details"),
    path('register/teacher/payroll', Teacher_Payroll.as_view(), name="teacher_payroll"),
    path('register/teacher/education_background', Teacher_EducationBackground.as_view(), name="teacher_educationbackground"),
    path('register/teacher/employmenthistory', Teacher_EmploymentHistory.as_view(), name="teacher_employmenthistory"),
    path('register/teacher/nextofkin', Teacher_Next_of_Kin.as_view(), name="teacher_nextofkin"),
    path('register/teacher/currentemployment', Teacher_Current_Employment.as_view(), name="teacher_currentemployment"),

    # Teacher Detail
    path('details/<str:id>/', views.teacher_details, name = "teacher_details"),
  
]