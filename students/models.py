from django.db import models
from academic.models import *
from accounts.models import CustomUser
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.conf import settings


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

    GRADE_CHOICES = (
        ("KIN", "Kindergarten"),
        ("BBY", "Baby"),
        ("MID", "Middle"),
        ("UPP", "Upper"),
        ("TOP", "Top"),
        ("grade_7", "Grade 7"),
        ("grade_6", "Grade 6"),
        ("grade_5", "Grade 5"),
        ("grade_4", "Grade 4"),
        ("grade_3", "Grade 3"),
        ("grade_2", "Grade 2"),
        ("grade_1", "Grade 1"),
    )

    registration_id = models.CharField(max_length=150, unique=True, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, blank=True, null=True)
    grade_of_entry = models.CharField(max_length=150, choices=GRADE_CHOICES, blank=True, null=True)
    year_of_entry = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message="Year must be in YYYY format.",
            )
        ],
        verbose_name="Year of Entry",
        blank=True, null=True
    )
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_phone = models.CharField(max_length=150, blank=True, null=True)
    current_grade = models.ForeignKey('academic.Grade', on_delete=models.CASCADE, blank=True, null=True)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    father_phone = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    mother_phone = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="", null=True, blank=True)
    school = models.ForeignKey('management.GeneralInformation', on_delete=models.CASCADE, related_name="students")
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students"
        db_table_comment = "This includes Students data"
        ordering = ["first_name"]

    def get_full_name(self):
        """Return the full name of the student"""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.first_name} {self.last_name} "

    def save(self, *args, **kwargs):
        current_year = now().year

        grade_years_mapping = {
            "grade_7": current_year - 6,
            "grade_6": current_year - 5,
            "grade_5": current_year - 4,
            "grade_4": current_year - 3,
            "grade_3": current_year - 2,
            "grade_2": current_year - 1,
            "grade_1": current_year
        }

        # Auto-set year_of_entry based on grade_of_entry
        if self.grade_of_entry in grade_years_mapping:
            self.year_of_entry = str(grade_years_mapping[self.grade_of_entry])
        else:
            self.year_of_entry = str(current_year)

        # Generate registration ID
        if not self.registration_id:
            if self.year_of_entry and self.school:
                school_abbr = self.school.get_abbr()
                count = Student.objects.filter(year_of_entry=self.year_of_entry, school=self.school).count() + 1

                if self.grade_of_entry in ["KIN", "BBY", "MID", "UPP", "TOP"]:
                    # Format: year/class/school_abbr/unique_number
                    self.registration_id = f"{current_year}/{self.grade_of_entry}/{school_abbr}/{count:03d}"
                else:
                    # Format remains unchanged for Grade 1 - Grade 7
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
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
    

