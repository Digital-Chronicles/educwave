from django.urls import path
from . import views
from . import csv_views


urlpatterns = [
    path("", views.studentList, name="students"),
    path("register/student-detail/", views.RegisterStudentDetails.as_view(), name="registerStudentDetail"),
    path("student-details/<int:id>/", views.studentDetail, name="StudentDetail"),

    # CSV UPLOAD
    path("register/csv_upload/", csv_views.student_csv_view, name="student_csv_upload"),
    path('student-download-csv-template/', csv_views.download_student_csv_template, name='download_student_csv_template'),
]