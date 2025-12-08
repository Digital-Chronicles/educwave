# academic/models.py

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import datetime


class Grade(models.Model):
    grade_name = models.CharField(max_length=50)
    class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name="grades",
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "class"
        db_table_comment = "This includes class data"
        ordering = ["grade_name"]

    def __str__(self):
        return self.grade_name


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


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    grade = models.ForeignKey(
        Grade,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="grade_subjects",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects",
    )

    class Meta:
        db_table = "subject"
        db_table_comment = "This includes subject data"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.code} - {self.grade}"


class Exam(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exams",
    )
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    file = models.FileField(
        upload_to='exam_uploads/',
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'docx', 'pptx']
        )],
    )
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey(
        Grade,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="exams",
    )
    created_by = models.ForeignKey(
        'teachers.Teacher',
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="exams",
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "exam"
        db_table_comment = "This includes exams data"
        order_with_respect_to = "subject"

    def __str__(self):
        return f"{self.subject}"


class Notes(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    topics = models.ManyToManyField(
        'assessment.Topics',
        related_name="notes",
    )
    notes_file = models.FileField(
        upload_to='notes_uploads/',
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'docx', 'pptx']
        )],
    )
    notes_content = CKEditor5Field('Text', config_name='extends')
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey(
        Grade,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="notes_for_grade",
    )
    created_by = models.ForeignKey(
        'teachers.Teacher',
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="notes_created",
    )
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

    term_name = models.CharField(
        max_length=10,
        choices=TermChoices.choices,
        verbose_name="Term Name",
        help_text="Select the term for this exam session",
    )
    year = models.PositiveIntegerField(
        default=datetime.date.today().year,
        choices=academic_year_choices,
        verbose_name="Academic Year",
        help_text="Select the academic year for this exam session",
        db_index=True,
    )
    start_date = models.DateField(help_text="Start date of the exam session")
    end_date = models.DateField(help_text="End date of the exam session")
    created_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.PROTECT,
        related_name="terms",
        help_text="Teacher who created this exam session",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "term_exam_session"
        ordering = ["-year", "term_name"]
        unique_together = ("term_name", "year")
        indexes = [
            models.Index(fields=['-year', 'term_name']),
            models.Index(fields=['term_name', 'year']),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({
                'start_date': "Start date must be before end date.",
                'end_date': "End date must be after start date.",
            })

    def __str__(self):
        return f"{self.get_term_name_display()} - {self.year}"


class ExamSession(models.Model):
    class ExamChoices(models.TextChoices):
        BOT = "BOT", "Beginning of Term"
        MOT = "MOT", "Mid of Term"
        EOT = "EOT", "End of Term"

    term = models.ForeignKey(
        TermExamSession,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
    )
    exam_type = models.CharField(
        max_length=3,
        choices=ExamChoices.choices,
        verbose_name="Exam Type",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(
        'teachers.Teacher',
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="exams_sessions",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("term", "exam_type")
        ordering = ["term__year", "term__term_name", "exam_type"]
        db_table = "exam_session"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")

    def __str__(self):
        return f"{self.term} ({self.get_exam_type_display()})"


class StudentMarkSummary(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name="mark_summaries",
    )
    term_exam = models.ForeignKey(
        TermExamSession,
        on_delete=models.CASCADE,
        related_name="mark_summaries",
    )
    exam_type = models.ForeignKey(
        ExamSession,
        on_delete=models.DO_NOTHING,
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="mark_summaries",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="mark_summaries",
    )
    total_score = models.PositiveIntegerField()
    max_possible = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    subject_position = models.PositiveIntegerField(null=True, blank=True)
    class_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'term_exam', 'subject', 'exam_type')
        verbose_name_plural = "Student Mark Summaries"
        indexes = [
            models.Index(fields=['student', 'term_exam']),
            models.Index(fields=['subject', 'term_exam']),
        ]

    def __str__(self):
        return (
            f"{self.student} - {self.subject} "
            f"({self.term_exam}): {self.percentage}%"
        )


class SubjectTotalMark(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name="subject_totals",
    )
    term_exam = models.ForeignKey(
        TermExamSession,
        on_delete=models.CASCADE,
        related_name="subject_totals",
    )
    exam_type = models.ForeignKey(
        ExamSession,
        on_delete=models.DO_NOTHING,
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_totals",
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="subject_totals",
    )

    total_score = models.PositiveIntegerField()
    max_possible = models.PositiveIntegerField(default=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'term_exam', 'subject')

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.percentage}%"
