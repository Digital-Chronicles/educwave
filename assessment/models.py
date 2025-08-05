from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class Topics(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING, related_name="assessment_topics")  
    grade = models.ForeignKey("academic.Grade", on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return f"{self.name}-{self.grade}"
    
    
class Question (models.Model):
    term_exam = models.ForeignKey("academic.TermExamSession", on_delete=models.CASCADE)
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
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    grade = models.ForeignKey(
        "academic.Grade", on_delete=models.DO_NOTHING, related_name="grade_exam_result")
    subject = models.ForeignKey("academic.Subject", on_delete=models.DO_NOTHING,
                                related_name="subject_xamrsults", null=True, blank=True )
    
    topic = models.ForeignKey(
        Topics, on_delete=models.CASCADE, related_name="exam_results")
    score = models.PositiveIntegerField()

    def clean(self):
        """Ensure score does not exceed the max_score of the related question."""
        if self.score > self.question.max_score:
            raise ValidationError(
                {"score": f"Score cannot exceed {self.question.max_score}"})

    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.question.question_number}: {self.score}/{self.question.max_score}"
