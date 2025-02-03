from django.urls import path

from .views import *

urlpatterns = [
    path("", finance, name="finance"),
#   grade school fees 
    path('schoolfees/', Schoolfees, name='schoolfees'),
    path("register/schoolfees/", RegisterSchoolfees.as_view(), name='register_schoolfees'),
    path('grades/summary/', grade_fee_summary, name='grade_fee_summary'),
#other school payments
    path('otherpayment/', OtherSchoolPayment, name='otherpayments'),
    path("register/otherschool/payments/", RegisterOtherSchoolPayments.as_view(), name='register_otherpayments'),
#transport
   
    path("register/transport/", RegisterTransport.as_view(), name='register_transport'),

#student_tuition_description
    path('tuition/description/', Student_TuitionDescription, name='tuition_description'),
    path("register/tuition/description/", RegisterStudentTuitionDescription.as_view(), name='register_tuition_description'),

#feetransaction
    path('fee/transaction/', Fee_Transaction, name='feetransaction'),
    path('fees/student/<int:student_id>/transactions/', Student_transactions, name='student_transactions'),
    path("register/fee/transaction", RegisterFeeTransaction.as_view(), name='register_schoolfees'),


]
