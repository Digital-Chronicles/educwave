from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import timedelta
from students.models import Student
from finance.models import SchoolFees, StudentTuitionDescription, FeeTransaction
from academic.models import Grade
from .forms import TuitionDescriptionForm, TransactionForm, SchoolFeesForm


@login_required
def finance_dashboard(request):
    # Student statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(current_status='active').count()
    graduated_students = Student.objects.filter(current_status='graduated').count()
    
    # Fee statistics
    total_fees_due = StudentTuitionDescription.objects.aggregate(
        total=Sum('total_fee')
    )['total'] or 0
    
    total_paid = FeeTransaction.objects.filter(status='paid').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    outstanding_balance = total_fees_due - total_paid
    
    # Recent transactions (last 30 days)
    recent_transactions = FeeTransaction.objects.filter(
        created__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created')[:10]
    
    # Payment status breakdown
    payment_status = {
        'paid': FeeTransaction.objects.filter(status='paid').count(),
        'pending': FeeTransaction.objects.filter(status='pending').count(),
        'overdue': FeeTransaction.objects.filter(status='overdue').count(),
    }
    
    # Grade-wise fee summary
    grade_summary = []
    grades = Grade.objects.all()
    for grade in grades:
        try:
            fee_structure = SchoolFees.objects.get(grade=grade)
            students_in_grade = StudentTuitionDescription.objects.filter(
                tuition__grade=grade
            ).count()
            
            grade_summary.append({
                'grade': grade.grade_name,
                'tuition_fee': fee_structure.tuitionfee,
                'students_count': students_in_grade,
                'total_expected': fee_structure.tuitionfee * students_in_grade,
            })
        except SchoolFees.DoesNotExist:
            continue
    
    # Upcoming due payments (next 7 days)
    upcoming_due = FeeTransaction.objects.filter(
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timedelta(days=7),
        status__in=['pending', 'overdue']
    ).order_by('due_date')
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'graduated_students': graduated_students,
        'total_fees_due': total_fees_due,
        'total_paid': total_paid,
        'outstanding_balance': outstanding_balance,
        'recent_transactions': recent_transactions,
        'payment_status': payment_status,
        'grade_summary': grade_summary,
        'upcoming_due': upcoming_due,
    }
    
    return render(request, "finance_dashboard.html", context)


# Tuition Description Views
class TuitionDescriptionListView(ListView):
    model = StudentTuitionDescription
    template_name = 'tuition_description_list.html'
    context_object_name = 'tuition_descriptions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('student', 'tuition__grade')
        if 'student_id' in self.request.GET:
            queryset = queryset.filter(student__id=self.request.GET['student_id'])
        return queryset

class TuitionDescriptionCreateView(CreateView):
    model = StudentTuitionDescription
    form_class = TuitionDescriptionForm
    template_name = 'tuition_description_form.html'
    success_url = reverse_lazy('tuition_description_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tuition description added successfully!')
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if 'student_id' in self.request.GET:
            student = get_object_or_404(Student, id=self.request.GET['student_id'])
            initial['student'] = student
        return initial

class TuitionDescriptionUpdateView(UpdateView):
    model = StudentTuitionDescription
    form_class = TuitionDescriptionForm
    template_name = 'tuition_description_form.html'
    success_url = reverse_lazy('tuition_description_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tuition description updated successfully!')
        return super().form_valid(form)

class TuitionDescriptionDeleteView(DeleteView):
    model = StudentTuitionDescription
    template_name = 'tuition_description_confirm_delete.html'
    success_url = reverse_lazy('tuition_description_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tuition description deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Transaction Views
class TransactionListView(ListView):
    model = FeeTransaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('student__student', 'student__tuition__grade')
        if 'student_id' in self.request.GET:
            queryset = queryset.filter(student__student__id=self.request.GET['student_id'])
        return queryset.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_paid'] = self.get_queryset().filter(status='paid').aggregate(total=Sum('amount_paid'))['total'] or 0
        return context

class TransactionCreateView(CreateView):
    model = FeeTransaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction recorded successfully!')
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if 'student_id' in self.request.GET:
            student = get_object_or_404(StudentTuitionDescription, student__id=self.request.GET['student_id'])
            initial['student'] = student
            initial['amount_due'] = student.total_fee
        return initial

class TransactionUpdateView(UpdateView):
    model = FeeTransaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction updated successfully!')
        return super().form_valid(form)

class TransactionDeleteView(DeleteView):
    model = FeeTransaction
    template_name = 'transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)

# School Fees Management Views
class SchoolFeesListView(ListView):
    model = SchoolFees
    template_name = 'school_fees_list.html'
    context_object_name = 'school_fees_list'

    def get_queryset(self):
        return SchoolFees.objects.select_related('grade').order_by('grade__grade_name')

class SchoolFeesUpdateView(UpdateView):
    model = SchoolFees
    form_class = SchoolFeesForm
    template_name = 'school_fees_form.html'
    success_url = reverse_lazy('manage_school_fees')

    def form_valid(self, form):
        messages.success(self.request, 'School fees updated successfully!')
        return super().form_valid(form)

class SchoolFeesDetailView(DetailView):
    model = SchoolFees
    template_name = 'school_fees_detail.html'
    context_object_name = 'school_fees'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade = self.object.grade
        context['students'] = Student.objects.filter(current_grade=grade)
        context['tuition_descriptions'] = StudentTuitionDescription.objects.filter(
            tuition__grade=grade
        ).select_related('student')
        return context