from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path("", views.StudentList.as_view(), name="students"),
    path("register/student-detail/", RegisterStudentDetails.as_view(), name="registerStudentDetail"),
    path("student-details/<int:id>/", views.studentDetail, name="StudentDetail"),
]