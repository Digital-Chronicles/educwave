from django.urls import path

from .views import *

urlpatterns = [
    path("", finance, name="finance"),
    path('schoolfees/', Schoolfees, name='schoolfees'),
    path("register/schoolfees/", RegisterSchoolfees.as_view(), name='register_schoolfees'),
    path('grades/summary/', grade_fee_summary, name='grade_fee_summary'),
    path('otherpayment/', OtherSchoolPayment, name='otherpayments'),
    path("register/otherschool/payments/", RegisterOtherSchoolPayments.as_view(), name='register_otherpayments'),
    path("register/transport/", RegisterTransport.as_view(), name='register_transport'),
    path('tuition/description/', Student_TuitionDescription, name='tuition_description'),
    path("register/tuition/description/<int:student_id>/", RegisterStudentTuitionDescription, name='register_tuition_description'),
    path('fee/transaction/', Fee_Transaction_list, name='feetransaction'),
    path('student/<int:id>/transactions/', student_transactions, name='student_transactions'),
    path('get-students/', get_students_by_grade, name='get_students_by_grade'),
    path("register/fee/transaction", RegisterFeeTransaction.as_view(), name='register_schoolfees'),


]
