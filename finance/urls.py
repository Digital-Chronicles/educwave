from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("", finance_dashboard, name="finance-dashboard"),
    
    # Tuition Description URLs
    path('tuition-descriptions/', views.TuitionDescriptionListView.as_view(), name='tuition_description_list'),
    path('tuition-descriptions/add/', views.TuitionDescriptionCreateView.as_view(), name='add_tuition_description'),
    path('tuition-descriptions/<int:pk>/edit/', views.TuitionDescriptionUpdateView.as_view(), name='edit_tuition_description'),
    path('tuition-descriptions/<int:pk>/delete/', views.TuitionDescriptionDeleteView.as_view(), name='delete_tuition_description'),
    
    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='add_transaction'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete_transaction'),
    
    # School Fees Management
    path('manage-fees/', views.SchoolFeesListView.as_view(), name='manage_school_fees'),
    path('manage-fees/<int:pk>/edit/', views.SchoolFeesUpdateView.as_view(), name='edit_grade_fee'),
    path('manage-fees/<int:pk>/', views.SchoolFeesDetailView.as_view(), name='grade_fee_details'),
]


