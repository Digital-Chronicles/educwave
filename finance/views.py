from .models import StudentTuitionDescription, Student
from django.shortcuts import get_object_or_404
from .models import Student
from .models import Student  # Ensure this matches your actual models
from django.http import JsonResponse
from django.db.models import Sum, Prefetch

from accounts.decorators import role_required
from .models import StudentTuitionDescription
from django.shortcuts import redirect, render
from students.models import Student
from .models import StudentTuitionDescription, FeeTransaction
from django.db.models import Sum
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Prefetch

from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F, DecimalField
from django.db.models import Max
from django.http import HttpResponseBadRequest

# Create your views here.


def finance(request):
    # Get all StudentTuitionDescription records and calculate the total fees

    # total_fees = StudentTuitionDescription.objects.aggregate(total=Sum('total_fee'))['total'] or 0

    return render(request, "finance.html")
# School fees


def Schoolfees(request):
    grade_fees = SchoolFees.objects.all()

    return render(request, 'schoolfees.html', {'grade_fees': grade_fees})


class RegisterSchoolfees(LoginRequiredMixin, generic.CreateView):
    model = SchoolFees
    template_name = 'registerschoolfees.html'
    form_class = SchoolfeesForm
    success_url = reverse_lazy('schoolfees')
    # Override the form_valid method to set created_by to the current user

    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)

# Grade fee summary


def grade_fee_summary(request):
    grades = SchoolFees.objects.all()
    data = []

    for grade in grades:
        students = StudentTuitionDescription.objects.filter(tuition=grade)
        total_students = students.count()

        # Calculate total fees, amount paid, and balance for the grade
        total_fees = students.aggregate(total_fees=Sum('total_fee'))[
            'total_fees'] or 0
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


# OtherSchoolPayments
def OtherSchoolPayment(request):
    payments = OtherSchoolPayments.objects.all()

    return render(request, 'otherschoolpayments.html', {'payments': payments})


class RegisterOtherSchoolPayments(LoginRequiredMixin, generic.CreateView):
    model = OtherSchoolPayments
    template_name = 'registerotherpayments.html'
    form_class = OtherSchoolPaymentForm
    success_url = reverse_lazy('otherpayments')
    # Override the form_valid method to set created_by to the current user

    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)

# Transport


class RegisterTransport(LoginRequiredMixin, generic.CreateView):
    model = TransportFee
    template_name = 'registertransport.html'
    form_class = TransportForm
    success_url = reverse_lazy('finance')
    # Override the form_valid method to set created_by to the current user

    def form_valid(self, form):
        # Set 'created_by' to the currently logged-in user before saving the object
        form.instance.created_by = self.request.user
        # Call the parent class's form_valid method to save the object
        return super().form_valid(form)

# ALL TUITION ACCORDING TO CLASSES
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



#REGISTER STUDENT TUITION DESCRIPTION
@role_required(allowed_roles=['ADMIN', 'TEACHER'])
def RegisterStudentTuitionDescription(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Fetch the student's grade and the corresponding tuition fee
    try:
        tuition_fee = SchoolFees.objects.get(grade=student.current_grade)
    except SchoolFees.DoesNotExist:
        tuition_fee = None  # Handle cases where the grade has no tuition fee

    # Check if the student already has a tuition record
    tuition_instance = StudentTuitionDescription.objects.filter(
        student=student).first()

    if request.method == "POST":
        form = StudentTuitionDescriptionForm(
            request.POST, instance=tuition_instance)
        if form.is_valid():
            tuition_desc = form.save(commit=False)  # Don't save yet
            tuition_desc.student = student  # Assign the student
            tuition_desc.tuition = tuition_fee  # Assign the tuition based on grade
            tuition_desc.save()
            # Redirect back to student details
            return redirect('students')

    else:
        form = StudentTuitionDescriptionForm(
            instance=tuition_instance or StudentTuitionDescription())

    return render(request, "registerstudent_tution_description.html", {
        "student": student,
        "form": form,
        "tuition_fee": tuition_fee,  # Pass the fee to the template for display if needed
    })


def get_students_by_grade(request):
    grade_id = request.GET.get('grade_id')

    if grade_id:
        students = StudentTuitionDescription.objects.filter(
            student__current_grade=grade_id
        ).select_related('student').values(
            'id',  # This should be StudentTuitionDescription.id
            'student__first_name',
            'student__last_name'
        )

        student_list = [
            {
                # This should be StudentTuitionDescription.id
                'id': student['id'],
                'first_name': student['student__first_name'],
                'last_name': student['student__last_name']
            }
            for student in students
        ]

        return JsonResponse({'students': student_list})
    return JsonResponse({'students': []})





#  FEES STUDENTS TRANSACTIONS

# #Register Fee_transaction
class RegisterFeeTransaction(LoginRequiredMixin, generic.CreateView):
    model = FeeTransaction
    template_name = 'registerfeetransaction.html'
    form_class = FeeTransactionForm
    success_url = reverse_lazy('feetransaction')


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


#Each students fee  transactions

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
