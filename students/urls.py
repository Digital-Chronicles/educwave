from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path("", views.StudentList.as_view(), name="students"),
    path("register/student-detail/", RegisterStudentDetails.as_view(), name="registerStudentDetail"),
    path("register/student-address/<int:pk>/", RegisterStudentAddress.as_view(), name="register_student_address"),
    path("register/student-caretaker/<int:student_pk>/", CareTakerCreateView.as_view(), name="register_student_caretaker"),
    path("register/student-grade/<int:student_pk>/", StudentGradeCreateView.as_view(), name="register_student_grade"),

    # Student Caretakers
    path('caretaker/add/', CareTakerCreateView.as_view(), name='caretaker_create'),

    # Student Grade URLs
    path('student-grade/add/', StudentGradeCreateView.as_view(), name='student_grade_create'),

    # Student Detail
    path("student-details/<int:id>/", views.studentDetail, name="StudentDetail"),
]