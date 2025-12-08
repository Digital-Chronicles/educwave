# management/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from accounts.models import CustomUser


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
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "general_information"
        db_table_comment = "This includes general information about the school"

    def __str__(self):
        return self.school_name

    def get_abbr(self) -> str:
        """
        Generates an abbreviation from the school_name field.
        Picks the first letter of each word in the name.
        """
        return ''.join(word[0].upper() for word in self.school_name.split() if word)

    def save(self, *args, **kwargs):
        # Enforce singleton: only one GeneralInformation instance
        if not self.pk and GeneralInformation.objects.exists():
            raise ValidationError(
                "There is already a GeneralInformation instance. "
                "You can only update the existing one."
            )
        super().save(*args, **kwargs)


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


class Lesson(models.Model):
    class_assigned = models.ForeignKey(
        'academic.Grade',
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    subject = models.ForeignKey(
        'academic.Subject',
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    topic = models.ForeignKey(
        'assessment.Topics',
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    lesson_date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "lesson"
        db_table_comment = "This includes lessons data"
        order_with_respect_to = "class_assigned"

    def __str__(self):
        return f"{self.class_assigned} - {self.subject} ({self.lesson_date})"


class SchedulingSetting(models.Model):
    setting_name = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "scheduling_setting"
        db_table_comment = "This includes scheduling settings about the school"

    def __str__(self):
        return self.setting_name


class CertificateAward(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name="certificate_awards",
    )
    award_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    awarded_by = models.CharField(max_length=255)
    date_awarded = models.DateField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "certificate_award"
        db_table_comment = "This includes certificate awards for students"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.award_name}"


class Ranking_Grade(models.Model):
    grade = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "ranking_grade"
        db_table_comment = "This includes grade ranking information"

    def __str__(self):
        return self.grade


class TransactionSetting(models.Model):
    setting_name = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "transaction_setting"
        db_table_comment = "This includes transaction settings about the school"

    def __str__(self):
        return self.setting_name
