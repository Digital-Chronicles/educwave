# finance/views.py
from decimal import Decimal
from django.contrib import messages
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from .models import StudentTuitionDescription, FeeTransaction, SchoolFees
from academic.models import Grade
from students.models import Student
from .forms import StudentTuitionDescriptionForm, FeeTransactionForm
from django.db.models import Q
from django.shortcuts import render
from students.models import Student


def finance_dashboard(request):
    """
    Simple dashboard:
    - Total expected fees (all StudentTuitionDescription.total_fee)
    - Total collected (all FeeTransaction.amount_paid)
    - Total outstanding (expected - collected)
    - Optional per-grade summary
    """
    # Total collected
    total_collected = (
        FeeTransaction.objects.aggregate(
            total=Coalesce(Sum('amount_paid'), Decimal('0.00'))
        )['total']
    )

    # Total expected from all students with tuition description
    total_expected = (
        StudentTuitionDescription.objects.aggregate(
            total=Coalesce(Sum('total_fee'), Decimal('0.00'))
        )['total']
    )

    total_outstanding = total_expected - total_collected

    # Per-grade summary (optional)
    grade_summaries = (
        Grade.objects
        .annotate(
            expected=Coalesce(
                Sum('school_fees__student_tuition_descriptions__total_fee'),
                Decimal('0.00')
            ),
            collected=Coalesce(
                Sum(
                    'school_fees__student_tuition_descriptions__fee_transactions__amount_paid'
                ),
                Decimal('0.00')
            ),
        )
        .annotate(
            outstanding=F('expected') - F('collected')
        )
        .order_by('grade_name')
    )

    context = {
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'grade_summaries': grade_summaries,
    }
    return render(request, 'finance_dashboard.html', context)


def finance_student_list(request):
    """
    List of students for the finance department.
    With optional search by first or last name.
    """
    # use current_grade instead of grade
    qs = (
        Student.objects
        .select_related('current_grade')
        .order_by('current_grade__grade_name', 'first_name', 'last_name')
    )

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    context = {
        'students': qs,
        'search': search,
    }
    return render(request, 'finance_student_list.html', context)


def student_finance_detail(request, student_id):
    """
    Shows:
    - Student info
    - Tuition description (if any)
    - Total fee, total paid, balance
    - List of payments
    - Buttons to edit tuition / record payment
    """
    student = get_object_or_404(Student, pk=student_id)

    tuition_desc = (
        StudentTuitionDescription.objects
        .select_related('tuition__grade')
        .filter(student=student)
        .first()
    )

    total_fee = Decimal('0.00')
    total_paid = Decimal('0.00')
    balance = Decimal('0.00')
    transactions = []

    if tuition_desc:
        total_fee = tuition_desc.total_fee
        total_paid = (
            tuition_desc.fee_transactions.aggregate(
                total=Coalesce(Sum('amount_paid'), Decimal('0.00'))
            )['total']
        )
        balance = total_fee - total_paid
        transactions = tuition_desc.fee_transactions.order_by('-created')

    context = {
        'student': student,
        'tuition_desc': tuition_desc,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'balance': balance,
        'transactions': transactions,
    }
    return render(request, 'finance_student_detail.html', context)


# finance/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from students.models import Student
from .models import SchoolFees, StudentTuitionDescription
from .forms import StudentTuitionDescriptionForm


def register_student_tuition_description(request, student_id):
    """
    Create or update StudentTuitionDescription for this student.
    Tuition is auto-linked from SchoolFees based on student's current_grade.
    """
    student = get_object_or_404(Student, pk=student_id)

    # ✅ make sure student has a current_grade
    if not student.current_grade:
        messages.error(
            request,
            "This student has no current grade set. "
            "Please update the student's current grade first."
        )
        return redirect('finance_student_detail', student_id=student.id)

    # ✅ get SchoolFees for this grade (use current_grade, not grade)
    try:
        school_fees = SchoolFees.objects.get(grade=student.current_grade)
    except SchoolFees.DoesNotExist:
        messages.error(
            request,
            f"No SchoolFees configured for grade {student.current_grade}. "
            "Please create SchoolFees for this grade first."
        )
        return redirect('finance_student_detail', student_id=student.id)

    # existing tuition description (if any)
    tuition_desc = StudentTuitionDescription.objects.filter(student=student).first()

    if request.method == "POST":
        form = StudentTuitionDescriptionForm(
            request.POST,
            instance=tuition_desc,
            student=student,   # passed into form.__init__
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Tuition description saved successfully.")
            return redirect('finance_student_detail', student_id=student.id)
    else:
        form = StudentTuitionDescriptionForm(
            instance=tuition_desc,
            student=student,
        )

    context = {
        "student": student,
        "form": form,
        "school_fees": school_fees,
        "tuition_desc": tuition_desc,
    }
    return render(request, "register_tuition_description.html", context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from students.models import Student
from .models import StudentTuitionDescription, FeeTransaction
from .forms import FeeTransactionForm


def record_fee_payment(request, student_id):
    # Get the actual Student
    student = get_object_or_404(Student, pk=student_id)

    # Get the student's tuition description (StudentTuitionDescription)
    tuition_description = get_object_or_404(StudentTuitionDescription, student=student)

    # ✅ Use the correct FK name: student=tuition_description
    # or simply: tuition_description.fee_transactions.all()
    transactions = (
        FeeTransaction.objects
        .filter(student=tuition_description)
        .order_by('-created')
    )

    if request.method == "POST":
        # We pass tuition_description into the form so it can use it if needed
        form = FeeTransactionForm(request.POST, tuition_description=tuition_description)
        if form.is_valid():
            # ✅ Make sure the FK is set to this tuition_description
            fee_tx = form.save(commit=False)
            fee_tx.student = tuition_description   # FK -> StudentTuitionDescription
            fee_tx.save()

            messages.success(request, "Payment recorded successfully.")
            return redirect('finance_student_detail', student_id=student.id)
    else:
        form = FeeTransactionForm(tuition_description=tuition_description)

    context = {
        "student": student,
        "student_id": student.id,
        "tuition_description": tuition_description,
        "form": form,
        "transactions": transactions,
    }
    return render(request, "finance_record_payment.html", context)
