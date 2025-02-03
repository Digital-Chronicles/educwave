from django.db import models
from teachers.models import *
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Subjects Table
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, related_name="subjects")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "subject"
        db_table_comment = "This includes Subject data"
        ordering = ["name"]

    def __str__(self):
        return f'{self.name} - {self.curriculum.name}'

# Curriculum Table
class Curriculum(models.Model):
    name = models.CharField(max_length=150)
    objectives = models.TextField()
    learning_outcomes = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "curriculum"
        db_table_comment = "This includes curriculum data"
        order_with_respect_to = "name"

    def __str__(self):
        return self.name

# Topics Table
class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "topic"
        db_table_comment = "This includes topic data"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.subject.name}"

# Exams Table
class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    file = models.FileField(
        upload_to='exam_uploads/', 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'pptx'])]  # Add file type validation
    )
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey('Grade', blank=True, on_delete=models.DO_NOTHING, related_name="exams")
    created_by = models.ForeignKey(Teacher, blank=True, on_delete=models.DO_NOTHING, related_name="exams")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "exam"
        db_table_comment = "This includes exams data"
        order_with_respect_to = "subject"

    def __str__(self):
        return f"{self.subject}"

# Classes Table
class Grade(models.Model):
    grade_name = models.CharField(max_length=50)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="grades")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "class"
        db_table_comment = "This includes Students address data"
        ordering = ["grade_name"]

    def __str__(self):
        return self.grade_name
    
# Notes
class Notes(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="notes")
    topics = models.ManyToManyField(Topic, related_name="notes")
    notes_file = models.FileField(
        upload_to='notes_uploads/', 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'pptx'])]
    )
    notes_content = CKEditor5Field('Text', config_name='extends')
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey('Grade', blank=True, on_delete=models.DO_NOTHING, related_name="exam")
    created_by = models.ForeignKey(Teacher, blank=True, on_delete=models.DO_NOTHING, related_name="exam")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Notes"
        db_table = "notes"
        db_table_comment = "This includes notes data"
        order_with_respect_to = "subject"

    def __str__(self):
        return f"{self.subject}"
    

class TermExamSession(models.Model):
    term_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, related_name="terms")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "term"
        db_table_comment = "This includes terms data"
        ordering = ["term_name"]

    def __str__(self):
        return self.term_name
    

class StudentMark(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="marks", db_index=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks", db_index=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="marks", db_index=True)
    term = models.ForeignKey(TermExamSession, on_delete=models.CASCADE, related_name="marks", db_index=True )
    marks = models.PositiveIntegerField( validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Marks must be between 0 and 100.")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_marks"
        db_table_comment = "This includes student marks data"
        order_with_respect_to = "term"
        constraints = [
            models.UniqueConstraint(fields=["student", "subject", "term"], name="unique_student_subject_term")
        ]
        indexes = [
            models.Index(fields=["student", "subject", "term"]),
            models.Index(fields=["term", "subject"]),
        ]

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.subject.name} - {self.term.term_name}: {self.marks} Marks"

    def clean(self):
        """Ensure marks are within an acceptable range (0-100)."""
        if not (0 <= self.marks <= 100):
            raise ValidationError("Marks should be between 0 and 100.")
