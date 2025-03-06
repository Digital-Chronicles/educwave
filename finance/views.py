from django.db.models import Sum, Prefetch
from .models import StudentTuitionDescription
from django.shortcuts import render
from students.models import Student
from .models import StudentTuitionDescription, FeeTransaction
from django.db.models import Sum
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Prefetch

from .models import *
from  .forms import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F, DecimalField
from django.db.models import Max
from django.http import HttpResponseBadRequest

# Create your views here.
def finance(request):
    # Get all StudentTuitionDescription records and calculate the total fees

    # total_fees = StudentTuitionDescription.objects.aggregate(total=Sum('total_fee'))['total'] or 0

    return render(request, "finance.html")
#School fees
def Schoolfees(request):
    grade_fees = SchoolFees.objects.all()

    return render (request, 'schoolfees.html',{'grade_fees':grade_fees} )
    

class RegisterSchoolfees(LoginRequiredMixin,generic.CreateView):
    model= SchoolFees
    template_name = 'registerschoolfees.html'
    form_class = SchoolfeesForm
    success_url = reverse_lazy('schoolfees')
       # Override the form_valid method to set created_by to the current user
    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)
    
#Grade fee summary
def grade_fee_summary(request):
    grades = SchoolFees.objects.all()
    data = []

    for grade in grades:
        students = StudentTuitionDescription.objects.filter(tuition=grade)
        total_students = students.count()

        # Calculate total fees, amount paid, and balance for the grade
        total_fees = students.aggregate(total_fees=Sum('total_fee'))['total_fees'] or 0
        total_paid = FeeTransaction.objects.filter(student__in=students).aggregate(
            total_paid=Sum('amount_paid')
        )['total_paid'] or 0
        balance = total_fees - total_paid

        data.append({
            'grade': grade.grade.grade_name,
            'total_students': total_students,
            'total_fees': total_fees,
            'total_paid': total_paid,
            'balance': balance,
        })

    context = {'data': data}
    return render(request, 'grade_fee_summary.html', context)




#OtherSchoolPayments
def OtherSchoolPayment(request):
    payments = OtherSchoolPayments.objects.all()

    return render (request, 'otherschoolpayments.html',{'payments':payments} )

class RegisterOtherSchoolPayments(LoginRequiredMixin,generic.CreateView):
    model= OtherSchoolPayments
    template_name = 'registerotherpayments.html'
    form_class = OtherSchoolPaymentForm
    success_url = reverse_lazy('otherpayments')
       # Override the form_valid method to set created_by to the current user
    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)
    
#Transport
class RegisterTransport(LoginRequiredMixin,generic.CreateView):
    model= TransportFee
    template_name = 'registertransport.html'
    form_class = TransportForm
    success_url = reverse_lazy('finance')
       # Override the form_valid method to set created_by to the current user
    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)
 #   
# #StudentTuitionDescription
# def Student_TuitionDescription(request):
#     tuition = StudentTuitionDescription.objects.all()
    
    
#     return render (request, 'student_tution_description.html', {'tuition':tuition})


def Student_TuitionDescription(request):
    # Fetch all student tuition descriptions with related student and grade
    tuition_records = StudentTuitionDescription.objects.select_related(
        'student', 'tuition__grade')

    # Organize records by grade
    grades = {}
    for record in tuition_records:
        grade_name = record.tuition.grade.grade_name

        if grade_name not in grades:
            grades[grade_name] = []

        grades[grade_name].append({
            'id': record.id,
            'student_name': f"{record.student.first_name} {record.student.last_name}",
            'tuition_fee': record.tuition.tuitionfee,
            'hostel_fee': record.tuition.hostelfee if record.hostel else Decimal('0.00'),
            'breakfast_fee': record.tuition.breakfastfee if record.breakfast else Decimal('0.00'),
            'lunch_fee': record.tuition.lunchfee if record.lunch else Decimal('0.00'),
            'total_fee': record.total_fee,
        })

    return render(request, 'student_tution_description.html', {'grades': grades})



class RegisterStudentTuitionDescription(LoginRequiredMixin, generic.CreateView):
    model = StudentTuitionDescription
    template_name = 'registerstudent_tution_description.html'
    form_class = StudentTuitionDescriptionForm
    success_url = reverse_lazy('tuition_description')

    def form_valid(self, form):
        student_instance = form.instance.student

        # Check if a StudentTuitionDescription already exists for this student
        if StudentTuitionDescription.objects.filter(student=student_instance).exists():
            # Handle the case where the description already exists
            return HttpResponseBadRequest("A tuition description for this student already exists.")
        else:
            # Set 'created_by' to the currently logged-in user before saving the object
            form.instance.created_by = self.request.user
            return super().form_valid(form)
        
        
# #Register Fee_transaction
class RegisterFeeTransaction(LoginRequiredMixin, generic.CreateView):
    model = FeeTransaction
    template_name = 'registerfeetransaction.html'
    form_class = FeeTransactionForm
    success_url = reverse_lazy('feetransaction')


#  FEES STUDENTS TRANSACTIONS


def Fee_Transaction_list(request):
    # Fetch students with related tuition and prefetch transactions
    students = StudentTuitionDescription.objects.select_related(
        'student', 'tuition__grade'
    ).prefetch_related(
        Prefetch('fee_transactions',
                 queryset=FeeTransaction.objects.order_by('-created'))
    )

    grades = {}

    for student in students:
        # Get all fee transactions for the student
        transactions = list(student.fee_transactions.all())

        # Calculate total amount paid by summing transactions
        total_paid = sum(
            transaction.amount_paid for transaction in transactions)

        # Calculate remaining amount due
        original_due = student.tuition.tuitionfee + student.tuition.hostelfee + \
            student.tuition.breakfastfee + student.tuition.lunchfee
        # Ensure no negative balance
        amount_due = max(original_due - total_paid, 0)

        grade_name = student.tuition.grade.grade_name

        if grade_name not in grades:
            grades[grade_name] = []

        # Store student data with updated amounts
        grades[grade_name].append({
            'student_id': student.student.id,
            'student_name': f"{student.student.first_name} {student.student.last_name}",
            'amount_due': amount_due,  # Updated amount due
            'amount_paid': total_paid,
            'payment_method': transactions[0].payment_method if transactions else 'N/A',
            'status': 'Paid' if amount_due == 0 else 'Pending',
            'due_date': transactions[0].due_date if transactions else 'N/A',
            'last_payment_date': transactions[0].last_payment_date if transactions else 'N/A',
            'all_transactions': transactions
        })

    return render(request, 'feetransaction.html', {'grades': grades})


#


def student_transactions(request, id):
    # Fetch the student's tuition details
    student_tuition_description = get_object_or_404(
        StudentTuitionDescription, student__id=id)

    # Get all transactions for the student (ordered by creation date)
    transactions = student_tuition_description.fee_transactions.order_by(
        'created')

    # Initial amount due (from tuition details)
    original_due = (
        student_tuition_description.tuition.tuitionfee +
        student_tuition_description.tuition.hostelfee +
        student_tuition_description.tuition.breakfastfee +
        student_tuition_description.tuition.lunchfee
    )

    # Calculate the updated amount_due for each transaction
    total_paid = 0
    for transaction in transactions:
        total_paid += transaction.amount_paid  # Add each payment to total
        transaction.remaining_due = max(
            original_due - total_paid, 0)  # Ensure no negative value

    context = {
        'student_tuition_description': student_tuition_description,
        'transactions': transactions
    }

    return render(request, 'each_student_transactions.html', context)












  

