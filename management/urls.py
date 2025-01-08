from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('general-information/create/', create_general_information, name='create_general_information'),
    path('application-setting/create/', create_application_setting, name='create_application_setting'),
    path('lesson/create/', create_lesson, name='create_lesson'),
    path('scheduling-setting/create/', create_scheduling_setting, name='create_scheduling_setting'),
    path('certificate-award/create/', create_certificate_award, name='create_certificate_award'),
    path('grade/create/', create_grade, name='create_grade'),
    path('transaction-setting/create/', create_transaction_setting, name='create_transaction_setting'),
]
