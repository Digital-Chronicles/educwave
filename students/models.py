from django.db import models
from academic.models import *
from accounts.models import CustomUser
from django.core.validators import RegexValidator


# Create your models here.
class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('dropped out', 'Dropped Out'),
    )
    registration_id = models.CharField(max_length=150, unique=True, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    year_of_entry = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message="Year must be in YYYY format.",
            )
        ],
        verbose_name="Year of Entry"
    )
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_phone = models.CharField(max_length=150, blank=True, null=True)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    father_phone = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    mother_phone = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="",null=True, blank=True)
    school = models.ForeignKey('management.GeneralInformation', on_delete=models.CASCADE, related_name="students")
    registered_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students"
        db_table_comment = "This includes Students data"
        ordering = ["first_name"]

    def __str__(self):
        return self.first_name + " " + self.last_name

    def save(self, *args, **kwargs):
        if not self.registration_id:
            if self.year_of_entry and self.school:
                # Get the abbreviation of the school
                school_abbr = self.school.get_abbr()

                # Count existing students for the same year and school
                count = Student.objects.filter(
                    year_of_entry=self.year_of_entry,
                    school=self.school
                ).count() + 1

                # Generate the registration ID
                self.registration_id = f"{self.year_of_entry}/{school_abbr}/{count:03d}"
            else:
                raise ValueError("Year of entry and school are required to generate a registration ID.")

        super().save(*args, **kwargs)


# Student Address Table
class StudentAddress(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students_address"
        db_table_comment = "This includes Students address data"
        order_with_respect_to = "student"

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name

# Guardian Contacts Table
class CareTaker(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "caretaker"
        db_table_comment = "This includes Students care taker data"
        order_with_respect_to = "student"

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name

# Student Class Assignment Table
class StudentGrade(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Grade, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students_class"
        db_table_comment = "This includes Students class data"
        order_with_respect_to = "student"

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name
    
# Fees Transactions Table
class FeeTransaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=(
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online transfer', 'Online Transfer'),
    ))
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ))
    last_payment_date = models.DateField(null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "fee_transaction"
        db_table_comment = "This includes Students fees transaction data"
        order_with_respect_to = "student"
