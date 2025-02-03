from django.shortcuts import render
from students.models import Student
from .models import StudentTuitionDescription, FeeTransaction
from django.db.models import Sum
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
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
#StudentTuitionDescription
def Student_TuitionDescription(request):
    tuition = StudentTuitionDescription.objects.all()
    return render (request, 'student_tution_description.html', {'tuition':tuition})
# class RegisterStudentTuitionDescription(LoginRequiredMixin,generic.CreateView):
#     model= StudentTuitionDescription
#     template_name = 'registerstudent_tution_description.html'
#     form_class = StudentTuitionDescriptionForm
#     success_url = reverse_lazy('tuition_description')
#        # Override the form_valid method to set created_by to the current user
#     def form_valid(self, form):
#         # Set 'created_by' to the currently logged-in user before saving the object
#         form.instance.created_by = self.request.user
#         # Call the parent class's form_valid method to save the object
#         return super().form_valid(form)
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




 #FeesTransaction
def Fee_Transaction(request):
        # Group transactions by grade and fetch the latest transaction for each student
    grades = {}
    students = StudentTuitionDescription.objects.all()

    for student in students:
        # Get the latest transaction for this student
        latest_transaction = student.fee_transactions.order_by('-created').first()

        if latest_transaction:
            grade_name = student.tuition.grade.grade_name
            if grade_name not in grades:
                grades[grade_name] = []

            grades[grade_name].append({
                'student_name': f"{student.student.first_name} {student.student.last_name}",
                'amount_due': latest_transaction.amount_due,
                'amount_paid': latest_transaction.amount_paid,
                'payment_method': latest_transaction.payment_method,
                'status': latest_transaction.status,
                'due_date': latest_transaction.due_date,
                'last_payment_date': latest_transaction.last_payment_date,
                'all_transactions': student.fee_transactions.all()  # For detailed view
            })

    context = {'grades': grades}
    
    return render(request, 'feetransaction.html', context)


# #Register Fee_transaction
# class RegiseterFeeTransaction(LoginRequiredMixin, generic.CreateView):
#     model =FeeTransaction
#     template_name = 'registerfeetransaction.html'
#     form_class = FeeTransactionForm
#     success_url = reverse_lazy('feetransaction')



class RegisterFeeTransaction(LoginRequiredMixin, generic.CreateView):
    model = FeeTransaction
    template_name = 'registerfeetransaction.html'
    form_class = FeeTransactionForm
    success_url = reverse_lazy('feetransaction')

    def form_valid(self, form):
        # Extract relevant fields from the form to identify duplicates
        student = form.cleaned_data.get('student')
        transaction_date = form.cleaned_data.get('transaction_date')
        amount = form.cleaned_data.get('amount')
        # Add other fields as necessary

        # Check if a FeeTransaction with the same details already exists
        if FeeTransaction.objects.filter(
            student=student,
            transaction_date=transaction_date,
            amount=amount,
            # Add other fields as necessary
        ).exists():
            # Handle the case where a duplicate transaction exists
            return HttpResponseBadRequest("A similar fee transaction already exists.")
        else:
            # Set 'created_by' to the currently logged-in user before saving the object
            form.instance.created_by = self.request.user
            return super().form_valid(form)


#Each students transactions
def Student_transactions(request, student_id):
    # Fetch the student's details and their transactions
    student = get_object_or_404(StudentTuitionDescription, id=student_id)
    transactions = student.fee_transactions.order_by('-created')  # Order by the most recent

    context = {
        'student': student,
        'transactions': transactions,
    }
    return render(request, 'all_transactions.html', context)












    recent_fees_transactions = FeeTransaction.objects.all().order_by('-created')[:10]
    estimated_collections = StudentTuitionDescription.objects.aggregate(total=Sum('total_fee'))['total'] or 0


    return render(request, "finance.html", {"estimated_collections": estimated_collections, "recent_fees_transactions":recent_fees_transactions})

