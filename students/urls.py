from django.urls import path
from . import views
from .views import CareTakerCreateView, CareTakerUpdateView, CareTakerListView, StudentGradeCreateView, StudentGradeUpdateView, StudentGradeListView

urlpatterns = [
    path("", views.StudentList.as_view(), name="students"),
    path("register/student-detail/", views.RegisterStudentDetails.as_view(), name="registerStudentDetail"),
    path("/students/register/student-address/", views.RegisterStudentAddress.as_view(), name="registerStudentAdress"),

    # Student Caretakers
    path('caretaker/add/', CareTakerCreateView.as_view(), name='caretaker_create'),
    path('caretaker/edit/<int:pk>/', CareTakerUpdateView.as_view(), name='caretaker_edit'),
    path('caretakers/', CareTakerListView.as_view(), name='caretaker_list'),

    # Student Grade URLs
    path('student-grade/add/', StudentGradeCreateView.as_view(), name='student_grade_create'),
    path('student-grade/edit/<int:pk>/', StudentGradeUpdateView.as_view(), name='student_grade_edit'),
    path('student-grades/', StudentGradeListView.as_view(), name='student_grade_list'),

    # Student Detail
    path("student-details/<int:id>/", views.studentDetail, name="StudentDetail"),
]