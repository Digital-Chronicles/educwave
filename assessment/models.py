from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import CustomUser


# Create your models here.
class Topics(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, related_name="assessment_topics")  
    grade = models.ForeignKey("academic.Grade", on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return f"{self.name}-{self.grade}"
    
    
class Question (models.Model):
    term_exam = models.ForeignKey("academic.TermExamSession", on_delete=models.CASCADE)
    exam_type = models.ForeignKey("academic.ExamSession", on_delete=models.DO_NOTHING)
    question_number = models.CharField(max_length=100, default="41a")
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name="questions")
    grade = models.ForeignKey("academic.Grade", on_delete=models.DO_NOTHING,
                              related_name="grade_questions")  # Unique related_name
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING,
                                related_name="subject_question", null=True, blank=True)

    max_score = models.PositiveIntegerField(default=5)    
    
    class Meta:
        unique_together = ('term_exam', 'question_number', 'grade', 'subject')

    def __str__(self):
        return f"Question {self.question_number}"

class ExamResult(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        help_text="Optional for subject totals"
    )
    grade = models.ForeignKey(
        "academic.Grade", on_delete=models.DO_NOTHING, related_name="grade_exam_result"
    )
    subject = models.ForeignKey(
        "academic.Subject", 
        on_delete=models.DO_NOTHING,
        related_name="subject_xamrsults", 
        null=True, 
        blank=True
    )
    topic = models.ForeignKey(
        Topics, on_delete=models.CASCADE, null=True, 
        blank=True, related_name="exam_results"
    )
    exam_session = models.ForeignKey(
        "academic.ExamSession",
        on_delete=models.CASCADE,
        related_name="exam_results",
        null=True,
        blank=True
    )
    score = models.PositiveIntegerField()
    
    total_score = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total score for the subject"
    )
    max_possible = models.PositiveIntegerField(
        default=100,
        help_text="Maximum possible score"
    )
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Percentage score"
    )
    

    def clean(self):
        """Ensure score does not exceed the max_score of the related question."""
        if self.question and hasattr(self.question, 'max_score'):
            if self.score > self.question.max_score:
                raise ValidationError(
                    {"score": f"Score cannot exceed {self.question.max_score}"}
                )
        
        if self.percentage and (self.percentage < 0 or self.percentage > 100):
            raise ValidationError(
                {"percentage": "Percentage must be between 0 and 100"}
            )

    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        
        # Auto-calculate percentage if not provided but total_score and max_possible are available
        if self.percentage is None and self.total_score is not None and self.max_possible:
            try:
                self.percentage = (self.total_score / self.max_possible) * 100
            except ZeroDivisionError:
                self.percentage = 0
        
        # Handle the override logic - whichever is saved last takes precedence
        if self.student and self.subject and self.exam_session:
            # If this is a SUBJECT TOTAL, delete individual question scores
            if self.is_subject_total:
                # Delete all individual question scores for this student-subject-exam combination
                ExamResult.objects.filter(
                    student=self.student,
                    subject=self.subject,
                    exam_session=self.exam_session,
                    question__isnull=False  # Individual questions only
                ).delete()
            
            # If this is an INDIVIDUAL QUESTION, check if subject total exists and delete it
            else:
                # Delete any existing subject total for this student-subject-exam combination
                ExamResult.objects.filter(
                    student=self.student,
                    subject=self.subject,
                    exam_session=self.exam_session,
                    question__isnull=True  # Subject totals only
                ).delete()
        
        super().save(*args, **kwargs)

    @property
    def is_subject_total(self):
        """Check if this record represents a subject total"""
        return self.question is None

    def __str__(self):
        if self.question:
            return f"{self.student.first_name} - {self.question.question_number}: {self.score}/{self.question.max_score}"
        else:
            return f"{self.student.first_name} - {self.subject.name} Total: {self.score}/100" 


# # class ExamResult(models.Model):
#     student = models.ForeignKey("students.Student", on_delete=models.CASCADE)

    
#     question = models.ForeignKey(
#         Question, 
#         on_delete=models.CASCADE, 
#         null=True,  # Make it nullable
#         blank=True,  # Allow blank in forms
#         help_text="Optional for subject totals"
#     )
#     grade = models.ForeignKey(
#         "academic.Grade", on_delete=models.DO_NOTHING, related_name="grade_exam_result"
#     )
#     subject = models.ForeignKey(
#         "academic.Subject", 
#         on_delete=models.DO_NOTHING,
#         related_name="subject_xamrsults", 
#         null=True, 
#         blank=True
#     )
#     topic = models.ForeignKey(
#         Topics, on_delete=models.CASCADE, null=True, 
#         blank=True, related_name="exam_results"
#     )
#     exam_session = models.ForeignKey(
#         "academic.ExamSession",
#         on_delete=models.CASCADE,
#         related_name="exam_results",
#         null=True,
#         blank=True
#     )
#     score = models.PositiveIntegerField()
    
#     # UPDATED FIELDS - removed exam_type since it's in ExamSession
#     total_score = models.PositiveIntegerField(
#         null=True, 
#         blank=True,
#         help_text="Total score for the subject"
#     )
#     max_possible = models.PositiveIntegerField(
#         default=100,
#         help_text="Maximum possible score"
#     )
#     percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         null=True, 
#         blank=True,
#         help_text="Percentage score"
#     )

#     def clean(self):
#         """Ensure score does not exceed the max_score of the related question."""
#         # Only validate if question is provided AND has a max_score
#         if self.question and hasattr(self.question, 'max_score'):
#             if self.score > self.question.max_score:
#                 raise ValidationError(
#                     {"score": f"Score cannot exceed {self.question.max_score}"}
#                 )
        
#         # Additional validation for percentage
#         if self.percentage and (self.percentage < 0 or self.percentage > 100):
#             raise ValidationError(
#                 {"percentage": "Percentage must be between 0 and 100"}
#             )

#     def save(self, *args, **kwargs):
#         """Validate before saving."""
#         self.clean()
        
#         # Auto-calculate percentage if not provided but total_score and max_possible are available
#         if self.percentage is None and self.total_score is not None and self.max_possible:
#             try:
#                 self.percentage = (self.total_score / self.max_possible) * 100
#             except ZeroDivisionError:
#                 self.percentage = 0
        
#         # If this is a subject total, delete individual question scores for the same student-subject-exam
#         if self.is_subject_total and self.student and self.subject and self.exam_session:
#             # Delete all individual question scores for this student-subject-exam combination
#             ExamResult.objects.filter(
#                 student=self.student,
#                 subject=self.subject,
#                 exam_session=self.exam_session,
#                 question__isnull=False  # Individual questions only
#             ).delete()
        
#         super().save(*args, **kwargs)

#     @property
#     def is_subject_total(self):
#         """Check if this record represents a subject total"""
#         return self.question is None