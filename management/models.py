from django.db import models
from accounts.models import CustomUser
from teachers.models import Teacher
from students.models import Student, Grade
from academic.models import Subject, Topics
from django.core.validators import RegexValidator
from datetime import date
from django.core.exceptions import ValidationError


# Create your models here.
class GeneralInformation(models.Model):
    school_name = models.CharField(max_length=255, unique=True)
    school_badge = models.ImageField(upload_to="badges", blank=True, null=True)
    box_no = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField()
    contact_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")],
    )
    email = models.EmailField()
    website = models.URLField(null=True, blank=True)
    established_year = models.PositiveIntegerField()
    registered_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "general_information"
        db_table_comment = "This includes general information about the school"

    def __str__(self):
        return self.school_name

    def get_abbr(self):
        """
        Generates an abbreviation from the school_name field.
        Picks the first letter of each word in the name.
        """
        return ''.join(word[0].upper() for word in self.school_name.split() if word)
    
    def save(self, *args, **kwargs):
        if not self.pk and GeneralInformation.objects.exists():
            # If there's an existing instance and we're trying to create a new one, raise an error
            raise ValidationError("There is already an instance of Settings. You can only update the existing one.")
        super(GeneralInformation, self).save(*args, **kwargs)


# Application Settings Table
class ApplicationSetting(models.Model):
    setting_name = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "application_setting"
        db_table_comment = "This includes settings data"

    def __str__(self):
        return self.setting_name

# Classes and Lessons Table
class Lesson(models.Model):
    class_assigned = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="lesson")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lesson")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="lesson")
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name="lesson")
    lesson_date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "lesson"
        db_table_comment = "This includes exams data"
        order_with_respect_to = "class_assigned"

    def __str__(self):
        return self.school_name

# Scheduling Settings Table
class SchedulingSetting(models.Model):
    setting_name = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "scheduling_setting"
        db_table_comment = "This includes scheduling setting about the school"

    def __str__(self):
        return self.setting_name

# Certificates and Awards Table
class CertificateAward(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="certificate_award")
    award_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    awarded_by = models.CharField(max_length=255)
    date_awarded = models.DateField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "certificate_award"
        db_table_comment = "This includes certificate_awards about the school"

    def __str__(self):
        return self.school_name

# Grades and Scoring Table
class Ranking_Grade(models.Model):
    grade = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "ranking_grade"
        db_table_comment = "This includes grade information about the school"

    def __str__(self):
        return self.grade
    

# Transaction Settings Table
class TransactionSetting(models.Model):
    setting_name = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "transaction_setting"
        db_table_comment = "This includes transaction setting about the school"

    def __str__(self):
        return self.setting_name
