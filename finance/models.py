from django.db import models
from academic.models import Grade
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from students.models import Student
from django.utils.timezone import now
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError

# Create your models here.
class SchoolFees(models.Model):
    grade = models.OneToOneField(Grade, on_delete=models.CASCADE, related_name="school_fees")
    tuitionfee = models.DecimalField(
        default=0.0,  max_digits=10, decimal_places=2)
    hostelfee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    breakfastfee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    lunchfee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(default="No Description ...")
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.grade.grade_name

    class Meta:
        verbose_name_plural = "SchoolFees"

    
class OtherSchoolPayments(models.Model):
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
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    fees_type = models.CharField(choices=FEES_TYPE, max_length=150, unique=True)
    amount = models.IntegerField()
    description = models.TextField(default="No Description ...")
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    unique_code = models.CharField(blank=True, null=True, unique=True, max_length=150)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return super().__str__()

    def __str__(self):
        return self.grade.grade_name
    
    def save(self, *args, **kwargs):
        # Generate unique code using grade and fees_type
        if not self.unique_code:
            self.unique_code = f"{slugify(self.grade.grade_name)}-{slugify(self.fees_type)}"
        super().save(*args, **kwargs)


class TransportFee(models.Model):
    location = models.CharField(max_length=150)
    amount = models.IntegerField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)  

    def __str__(self):
        return self.location
    
class StudentTuitionDescription(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="tuition_description")
    tuition = models.ForeignKey(
        SchoolFees, default=200000, on_delete=models.CASCADE, related_name="student_tuition_descriptions")
    hostel = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)
   
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    def calculate_total_fee(self):
        """
        Calculate the total fee based on tuition and selected options.
        """
        # Add optional fees if selected
        base_fee = Decimal(str(self.tuition.tuitionfee))
        if self.hostel:
            base_fee += Decimal(str(self.tuition.hostelfee))
        if self.lunch:
            base_fee += Decimal(str(self.tuition.lunchfee))
        if self.breakfast:
            base_fee += Decimal(str(self.tuition.breakfastfee))

        return base_fee
 

    def save(self, *args, **kwargs):
  
        self.total_fee = self.calculate_total_fee()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.tuition.grade.grade_name}"


class FeeTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online_transfer', 'Online Transfer'),
        ('mobile_money', 'Mobile Money'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )

    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, related_name="fee_transactions", null=True, blank=True
    )
   
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)

    student = models.ForeignKey(StudentTuitionDescription, on_delete=models.CASCADE, related_name="fee_transactions")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    due_date = models.DateField(null=True, blank=True, editable=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_payment_date = models.DateField(null=True, blank=True, editable=True)
    payment_reference = models.CharField(max_length=50, null=True, blank=True, unique=True)
    receipt_url = models.URLField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True, help_text="Any additional notes about the payment")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "fee_transaction"
        db_table_comment = "This includes students' fees transaction data"
        ordering = ['-created']  # Orders by the most recent transactions

    def __str__(self):
        return f"{self.student.student.first_name} {self.student.student.last_name} - {self.status.capitalize()}"


    

    def save(self, *args, **kwargs):
        """Save the transaction, updating amount_due and status dynamically."""
        if not self.pk:  # If this is a new transaction
            self.amount_due = self.student.total_fee  # Set `amount_due` from `total_fee`
        
        # Determine the status of the transaction

    def calculate_due_amount(self):
        """
        Calculate the due amount for the student by subtracting the total amount paid so far 
        from the student's total fee.
        """
        total_paid = self.student.fee_transactions.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0
        return self.student.total_fee - total_paid

    def save(self, *args, **kwargs):
        """
        Automatically set due_date, amount_due, and other fields before saving.
        """
        # Set the due amount automatically
        self.amount_due = self.calculate_due_amount()

        # Set the due date automatically (e.g., 30 days from creation)
        if not self.due_date:
            self.due_date = now().date() + timedelta(days=30)

        # Update status and last payment date

        if self.amount_paid >= self.amount_due:
            self.status = 'paid'
            self.last_payment_date = now().date()
        elif self.due_date and self.due_date < now().date():
            self.status = 'overdue'
        else:
            self.status = 'pending'


        # Adjust `amount_due` to reflect remaining balance
        self.amount_due = max(Decimal(0), self.student.total_fee - self.amount_paid)



        super().save(*args, **kwargs)




