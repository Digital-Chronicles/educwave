from django.db import models

from accounts.models import CustomUser

from .districts import Districts
from django.conf import settings
from django.core.validators import RegexValidator




# Create your models here.
class Teacher(models.Model):
    GENDER = (
        ("male", "male"),
        ("female", "female"),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="teacher_profile")
    initials = models.CharField(blank=True, null=True, max_length=5, default="NJ")
    registration_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=50, choices= GENDER, default= 'male')
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
    profile_picture = models.ImageField(upload_to="teacher_profile_pictures", null=True, blank=True)
    school = models.ForeignKey('management.GeneralInformation', on_delete=models.CASCADE, related_name="teachers")
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="registered_teachers")

        # ADD THIS FIELD - For teacher status
    is_active = models.BooleanField(default=True, help_text="Whether this teacher is currently active")
    class Meta:
        db_table = "teachers"

        # ADD THESE HELPER METHODS
    def get_assigned_classes(self):
        """Get all classes assigned to this teacher"""
        from academic.models import Grade 
        return Grade.objects.filter(class_teacher=self, is_active=True)
    
    def get_assigned_subjects(self):
        """Get all subjects assigned to this teacher"""
        from academic.models import Subject 
        return Subject.objects.filter(teacher=self, is_active=True)
    
    def get_student_count(self):
        """Get total number of students in assigned classes"""
        classes = self.get_assigned_classes()
        from students.models import Student 
        return Student.objects.filter(current_grade__in=classes).count()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.registration_id:
            if self.year_of_entry and self.school:
                school_abbr = self.school.get_abbr()
                
                # Find the highest existing count for the same year and school
                last_teacher = Teacher.objects.filter(
                    year_of_entry=self.year_of_entry,
                    school=self.school
                ).order_by('-registration_id').first()

                if last_teacher:
                    # Extract the numeric part and increment
                    last_number = int(last_teacher.registration_id.split('/')[-1])
                    new_number = last_number + 1
                else:
                    new_number = 1

                self.registration_id = f"{school_abbr}/{new_number:03d}"
            else:
                raise ValueError("Year of entry and school are required to generate a registration ID.")

        super().save(*args, **kwargs)

      
# Payroll Information Table
class PayrollInformation(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name="payroll_information")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, unique=True)
    tax_identification_number = models.CharField(max_length=50, unique=True)
    nssf_number = models.CharField(max_length=50, unique=True)
    payment_frequency = models.CharField(max_length=20, choices=(
        ('monthly', 'Monthly'),
        ('bi-weekly', 'Bi-Weekly'),
        ('weekly', 'Weekly'),
    ))

    class Meta:
        db_table = "payroll_information"

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}" 

# Education Background Table
class EducationBackground(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="education_background")
    education_award = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    result_obtained = models.CharField(max_length=10)
    additional_certifications = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "education_background"

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}" 
    
# Employment History Table
class EmploymentHistory(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="employment_history")
    organization = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    responsibilities = models.TextField()

    class Meta:
        db_table = "employment_history" 

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}" 


# Next of Kin Table
class NextOfKin(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name="next_of_kin")
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()

    class Meta:
        db_table = "next_of_kin"

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}"
    
# Current Employment Table
class CurrentEmployment(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name="current_employment")
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    # supervisor_name = models.OneToOneField(Teacher, on_delete=models.DO_NOTHING, null=True, blank = True)

    class Meta:
        db_table = "current_employment"

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}"
