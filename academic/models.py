from django.db import models
from teachers.models import *
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
import datetime

#Grade
class Grade(models.Model):
    grade_name = models.CharField(max_length=50)
    class_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, related_name="grades")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "class"
        db_table_comment = "This includes Students address data"
        ordering = ["grade_name"]

    def __str__(self):
        return self.grade_name

# Subjects Table
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    grade = models.ForeignKey(
        Grade, blank=True, on_delete=models.DO_NOTHING, related_name="subject_grade")
    curriculum = models.ForeignKey(
        'Curriculum', on_delete=models.CASCADE, related_name="subjects")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "subject"
        db_table_comment = "This includes Subject data"
        ordering = ["name"]

    def __str__(self):
        return f'{self.name}-{self.grade} '

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
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="topics")
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
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="exams")
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    file = models.FileField(
        upload_to='exam_uploads/',
        blank=True,
        # Add file type validation
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'docx', 'pptx'])]
    )
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey(
        'Grade', blank=True, on_delete=models.DO_NOTHING, related_name="exams")
    created_by = models.ForeignKey(
        Teacher, blank=True, on_delete=models.DO_NOTHING, related_name="exams")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "exam"
        db_table_comment = "This includes exams data"
        order_with_respect_to = "subject"

    def __str__(self):
        return f"{self.subject}"

# Classes Table




# Notes


class Notes(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="notes")
    topics = models.ManyToManyField(Topic, related_name="notes")
    notes_file = models.FileField(
        upload_to='notes_uploads/',
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'docx', 'pptx'])]
    )
    notes_content = CKEditor5Field('Text', config_name='extends')
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey(
        'Grade', blank=True, on_delete=models.DO_NOTHING, related_name="exam")
    created_by = models.ForeignKey(
        Teacher, blank=True, on_delete=models.DO_NOTHING, related_name="exam")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "Notes"
        db_table = "notes"
        db_table_comment = "This includes notes data"
        order_with_respect_to = "subject"

    def __str__(self):
        return f"{self.subject}"


def academic_year_choices():
    current_year = datetime.date.today().year
    return [(year, str(year)) for year in range(current_year - 10, current_year + 2)]


class TermExamSession(models.Model):
    class TermChoices(models.TextChoices):
        TERM_1 = "TERM_1", "Term 1"
        TERM_2 = "TERM_2", "Term 2"
        TERM_3 = "TERM_3", "Term 3"

    class ExamChoices(models.TextChoices):
        BOT = "BOT", "Beginning of Term"
        MOT = "MOT", "Mid of Term"
        EOT = "EOT", "End of Term"

    term_name = models.CharField(max_length=10, choices=TermChoices.choices,
                                 verbose_name="Term Name", help_text="Select the term for this exam session")
    year = models.PositiveIntegerField(default=datetime.date.today().year, choices=academic_year_choices,
                                       verbose_name="Academic Year", help_text="Select the academic year for this exam session", db_index=True)
    exam_type = models.CharField(max_length=3, choices=ExamChoices.choices,
                                 verbose_name="Exam Type", help_text="Select the type of examination")
    start_date = models.DateField(help_text="Start date of the exam session")
    end_date = models.DateField(help_text="End date of the exam session")
    created_by = models.ForeignKey(Teacher, on_delete=models.PROTECT,
                                   related_name="terms", help_text="Teacher who created this exam session")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "term_exam_session"
        ordering = ["-year", "term_name"]
        unique_together = ("term_name", "year", "exam_type")
        indexes = [
            models.Index(fields=['-year', 'term_name']),
            models.Index(fields=['term_name', 'year', 'exam_type']),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({
                'start_date': "Start date must be before end date.",
                'end_date': "End date must be after start date."
            })

    def __str__(self):
        return f"{self.get_term_name_display()} - {self.year} ({self.get_exam_type_display()})"


class StudentMark(models.Model):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="marks")
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="marks")
    term = models.ForeignKey(
        TermExamSession, on_delete=models.CASCADE, related_name="marks")
    marks = models.PositiveIntegerField(validators=[MinValueValidator(
        0), MaxValueValidator(100)], help_text="Marks must be between 0 and 100.")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_marks"
        ordering = ["-term__year", "term__term_name",
                    "student__registration_id"]
        unique_together = ["student", "subject", "term"]

    def clean(self):
        if not (0 <= self.marks <= 100):
            raise ValidationError("Marks should be between 0 and 100.")

    def get_grade(self):
        if self.marks >= 90:
            return 1
        elif self.marks >= 80:
            return 2
        elif self.marks >= 70:
            return 3
        elif self.marks >= 60:
            return 4
        elif self.marks >= 55:
            return 5
        elif self.marks >= 50:
            return 6
        elif self.marks >= 45:
            return 7
        elif self.marks >= 40:
            return 8
        else:
            return 9

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.subject.name} - {self.term} - {self.marks} ({self.get_grade()})"


class StudentExamSummary(models.Model):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="exam_summaries")
    term = models.ForeignKey(
        TermExamSession, on_delete=models.CASCADE, related_name="exam_summaries")
    total_marks = models.PositiveIntegerField(default=0)
    average_marks = models.FloatField(default=0.0)

    class Meta:
        db_table = "student_exam_summary"
        ordering = ["-term__year", "term__term_name",
                    "student__registration_id"]
        unique_together = ["student", "term"]

    def calculate_totals(self):
        marks = self.student.marks.filter(term=self.term)
        self.total_marks = sum(mark.marks for mark in marks)
        self.average_marks = self.total_marks / \
            marks.count() if marks.count() > 0 else 0
        self.save()

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.term}: {self.total_marks} (Avg: {self.average_marks:.2f})"
