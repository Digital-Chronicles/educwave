# finance/models.py

from decimal import Decimal
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from django.db.models import Sum

from academic.models import Grade
from accounts.models import CustomUser
from students.models import Student


class SchoolFees(models.Model):
    """
    Fee structure per Grade (base amounts).
    One SchoolFees per Grade.
    """
    grade = models.OneToOneField(
        Grade,
        on_delete=models.CASCADE,
        related_name="school_fees",
    )
    tuitionfee = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
    )
    hostelfee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    breakfastfee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    lunchfee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    description = models.TextField(default="No Description ...")
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "SchoolFees"

    def __str__(self):
        return self.grade.grade_name


class OtherSchoolPayments(models.Model):
    """
    Extra / other fees per Grade (development, sports, etc.).
    """
    FEES_TYPE = (
        ("development", "development"),
        ("sports", "sports"),
        ("library", "library"),
        ("laboratory", "laboratory"),
        ("uniform", "uniform"),
        ("examination", "examination"),
        ("medical", "medical"),
        ("maintenance", "maintenance"),
        ("technology", "technology"),
        ("admission", "admission"),
        ("field_trip", "field_trip"),
        ("extra_classes", "extra_classes"),
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="other_payments",
    )
    fees_type = models.CharField(choices=FEES_TYPE, max_length=150)
    amount = models.IntegerField()
    description = models.TextField(default="No Description ...")
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    unique_code = models.CharField(
        blank=True,
        null=True,
        unique=True,
        max_length=150,
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "other_school_payments"
        db_table_comment = "This includes other school payments data"
        unique_together = ("grade", "fees_type")

    def __str__(self):
        return f"{self.grade.grade_name} - {self.fees_type}"

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = f"{slugify(self.grade.grade_name)}-{slugify(self.fees_type)}"
        super().save(*args, **kwargs)


class TransportFee(models.Model):
    """
    Transport fee per location.
    """
    location = models.CharField(max_length=150)
    amount = models.IntegerField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "transport_fee"

    def __str__(self):
        return self.location


class StudentTuitionDescription(models.Model):
    """
    Stores the fee structure attached to a student for a given Grade.
    total_fee is auto-calculated from SchoolFees + options (hostel, lunch, breakfast).

    Reverse relations:
      - student.tuition_description  (QuerySet of StudentTuitionDescription)
      - fee_transactions (from FeeTransaction.student)
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="tuition_description",
    )
    tuition = models.ForeignKey(
        SchoolFees,
        on_delete=models.CASCADE,
        related_name="student_tuition_descriptions",
    )
    hostel = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)

    total_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        db_table = "student_tuition_description"

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.tuition.grade.grade_name}"

    # === Fee / balance logic ===

    def calculate_total_fee(self) -> Decimal:
        """
        Calculate the total fee based on tuition and selected options.
        """
        base_fee = Decimal(str(self.tuition.tuitionfee))
        if self.hostel:
            base_fee += Decimal(str(self.tuition.hostelfee))
        if self.lunch:
            base_fee += Decimal(str(self.tuition.lunchfee))
        if self.breakfast:
            base_fee += Decimal(str(self.tuition.breakfastfee))
        return base_fee

    def save(self, *args, **kwargs):
        # Always recalculate total_fee before saving
        self.total_fee = self.calculate_total_fee()
        super().save(*args, **kwargs)

    def get_total_paid(self) -> Decimal:
        """
        Total amount paid across all transactions for this student's tuition.
        """
        return (
            self.fee_transactions.aggregate(total=Sum("amount_paid"))["total"]
            or Decimal("0.00")
        )

    @property
    def current_balance(self) -> Decimal:
        """
        Current balance based on the latest transaction:
        - If there are transactions, use latest.amount_due
        - If none, the balance == total_fee
        """
        last_tx = self.fee_transactions.order_by("-created", "-id").first()
        if last_tx:
            return last_tx.amount_due
        return self.total_fee

    def get_balance_for_term(self, term=None, academic_year=None) -> Decimal:
        """
        Balance filtered by term + academic year.
        If no term/academic_year is provided, behaves like current_balance
        (i.e. total_fee - total_paid).
        """
        qs = self.fee_transactions.all()
        if term:
            qs = qs.filter(term=term)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)

        total_paid = qs.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0.00")
        return max(Decimal("0.00"), self.total_fee - total_paid)


class FeeTransaction(models.Model):
    """
    One record per PAYMENT.

    We use StudentTuitionDescription.total_fee as the full fee,
    and calculate running balance (amount_due) based on all transactions
    for that student's tuition.

    Relationships:
      - student: FK to StudentTuitionDescription (NOT directly to Student)
      - grade: FK for reports / filtering (auto-set from tuition.grade if empty)
    """

    PAYMENT_METHOD_CHOICES = (
        ("cash", "Cash"),
        ("card", "Card"),
        ("online_transfer", "Online Transfer"),
        ("mobile_money", "Mobile Money"),
        ("bank", "Bank Transfer"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("partial", "Partial"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )

    TERM_CHOICES = (
        ("T1", "Term 1"),
        ("T2", "Term 2"),
        ("T3", "Term 3"),
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="fee_transactions",
        null=True,
        blank=True,
    )

    # Link to StudentTuitionDescription (which holds total_fee)
    student = models.ForeignKey(
        StudentTuitionDescription,
        on_delete=models.CASCADE,
        related_name="fee_transactions",
    )

    # Term + Academic year for term-by-term tracking
    term = models.CharField(
        max_length=2,
        choices=TERM_CHOICES,
        null=True,
        blank=True,
        help_text="Term for this payment (used for term-by-term balances).",
    )
    academic_year = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        help_text="Academic year e.g. 2025/2026",
    )

    # Remaining balance AFTER all payments (for that student's tuition)
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0.00"),
    )
    # Amount paid in THIS transaction
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
    )
    due_date = models.DateField(null=True, blank=True, editable=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    last_payment_date = models.DateField(null=True, blank=True, editable=True)
    payment_reference = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
    )
    receipt_url = models.URLField(null=True, blank=True)
    remarks = models.TextField(
        null=True,
        blank=True,
        help_text="Any additional notes about the payment",
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "fee_transaction"
        db_table_comment = "This includes students' fees transaction data"
        ordering = ["-created"]

    def __str__(self):
        return (
            f"{self.student.student.first_name} "
            f"{self.student.student.last_name} - {self.status.capitalize()}"
        )

    def calculate_total_paid_excluding_self(self) -> Decimal:
        """
        Total amount paid in all OTHER transactions for this student's tuition.
        """
        total = (
            self.student.fee_transactions.exclude(pk=self.pk)
            .aggregate(total=Sum("amount_paid"))["total"]
            or Decimal("0.00")
        )
        return total

    def save(self, *args, **kwargs):
        """
        Automatically set grade, due_date, amount_due, and status before saving.
        Also supports 'partial' status and term/year tracking.
        """
        # Auto-set grade from student's tuition grade if missing
        if self.student and not self.grade:
            self.grade = self.student.tuition.grade

        # Default due date for new transactions
        if not self.pk and not self.due_date:
            self.due_date = now().date() + timedelta(days=30)

        # Total paid in previous transactions
        total_paid_before = self.calculate_total_paid_excluding_self()
        # Include this transaction's payment
        total_paid = total_paid_before + (self.amount_paid or Decimal("0.00"))

        total_fee = self.student.total_fee
        # Remaining balance
        self.amount_due = max(Decimal("0.00"), total_fee - total_paid)

        today = now().date()

        # Status logic: paid / partial / pending / overdue
        if self.amount_due <= 0:
            self.status = "paid"
            self.last_payment_date = today
        else:
            if self.amount_paid > 0 or total_paid_before > 0:
                # some money has been paid but not full
                self.status = "partial"
            elif self.due_date and self.due_date < today:
                self.status = "overdue"
            else:
                self.status = "pending"

        super().save(*args, **kwargs)
