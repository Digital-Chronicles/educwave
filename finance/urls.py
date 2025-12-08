# finance/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_dashboard, name='finance-dashboard'),

    path('students/', views.finance_student_list, name='finance_student_list'),
    path('students/<int:student_id>/', views.student_finance_detail,
         name='finance_student_detail'),

    path(
        'students/<int:student_id>/tuition-description/',
        views.register_student_tuition_description,
        name='register_student_tuition_description',
    ),

    path(
        'students/<int:student_id>/payments/add/',
        views.record_fee_payment,
        name='record_fee_payment',
    ),
]
