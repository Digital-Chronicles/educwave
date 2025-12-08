# students/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.conf import settings


class Student(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    STATUS_CHOICES = (
        ("active", "Active"),
        ("graduated", "Graduated"),
        ("dropped out", "Dropped Out"),
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

    SCHOOL_TYPE_CHOICES = (
        ("day", "Day"),
        ("boarding", "Boarding"),
        ("bursary", "Bursary"),
        ("scholarhip", "scholarship"),
    )

    registration_id = models.CharField(
        max_length=150,
        unique=True,
        editable=False,
    )
    lin_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=True,
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    current_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
    )
    gender = models.CharField(
        max_length=50,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )
    school_type = models.CharField(
        max_length=150,
        choices=SCHOOL_TYPE_CHOICES,
        blank=True,
        null=True,
        default="day",
    )
    grade_of_entry = models.CharField(
        max_length=150,
        choices=GRADE_CHOICES,
        blank=True,
        null=True,
    )
    year_of_entry = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^\d{4}$",
                message="Year must be in YYYY format.",
            )
        ],
        verbose_name="Year of Entry",
        blank=True,
        null=True,
    )
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_phone = models.CharField(max_length=150, blank=True, null=True)
    current_grade = models.ForeignKey(
        "academic.Grade",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    father_name = models.CharField(max_length=150, blank=True, null=True)
    father_phone = models.CharField(max_length=150, blank=True, null=True)
    father_NIN = models.CharField(max_length=200, null=True, blank=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    mother_phone = models.CharField(max_length=150, blank=True, null=True)
    mother_NIN = models.CharField(max_length=200, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="", null=True, blank=True)
    school = models.ForeignKey(
        "management.GeneralInformation",
        on_delete=models.CASCADE,
        related_name="students",
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students"
        db_table_comment = "This includes Students data"
        ordering = ["first_name"]

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    # 🔹 FINANCE HELPER (read-only)
    def get_finance_balance(self):
        """
        Returns the current balance from finance (if tuition is set),
        or None if student has no tuition description yet.
        Uses the latest StudentTuitionDescription.
        """
        # tuition_description related_name is plural (QuerySet of StudentTuitionDescription)
        td = self.tuition_description.order_by("-id").first()
        if not td:
            return None
        return td.current_balance

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        current_year = now().year

        grade_years_mapping = {
            "grade_7": current_year - 6,
            "grade_6": current_year - 5,
            "grade_5": current_year - 4,
            "grade_4": current_year - 3,
            "grade_3": current_year - 2,
            "grade_2": current_year - 1,
            "grade_1": current_year,
        }

        # Auto-set year_of_entry based on grade_of_entry
        if self.grade_of_entry in grade_years_mapping:
            self.year_of_entry = str(grade_years_mapping[self.grade_of_entry])
        elif not self.year_of_entry:
            # Only override if not manually set
            self.year_of_entry = str(current_year)

        # Generate registration ID
        if not self.registration_id:
            if self.year_of_entry and self.school:
                school_abbr = self.school.get_abbr()
                count = (
                    Student.objects.filter(
                        year_of_entry=self.year_of_entry,
                        school=self.school,
                    ).count()
                    + 1
                )

                if self.grade_of_entry in ["KIN", "BBY", "MID", "UPP", "TOP"]:
                    # Format: year/class/school_abbr/unique_number
                    self.registration_id = (
                        f"{current_year}/{self.grade_of_entry}/{school_abbr}/{count:03d}"
                    )
                else:
                    # Format for Grade 1 - Grade 7
                    self.registration_id = (
                        f"{self.year_of_entry}/{school_abbr}/{count:03d}"
                    )
            else:
                raise ValueError(
                    "Year of entry and school are required to generate a registration ID."
                )

        super().save(*args, **kwargs)


class StudentAddress(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        unique=True,
    )
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
        return self.student.get_full_name()


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
        db_table_comment = "This includes Students caretaker data"
        order_with_respect_to = "student"

    def __str__(self):
        return f"{self.name} ({self.student.get_full_name()})"


class StudentGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey("academic.Grade", on_delete=models.CASCADE)
    assigned_date = models.DateField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "students_class"
        db_table_comment = "This includes Students class data"
        order_with_respect_to = "student"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_assigned}"
