from django.db import models
from teachers.models import *

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
        return self.name

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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam")
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    file = models.FileField(upload_to='exam_uploads/')
    description = models.TextField(null=True, blank=True)
    grade = models.ForeignKey('Grade', blank=True, on_delete=models.DO_NOTHING, related_name="exam")
    created_by = models.ForeignKey(Teacher, blank=True, on_delete=models.DO_NOTHING, related_name="exam")
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
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="grade")
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        db_table = "class"
        db_table_comment = "This includes Students address data"
        ordering = ["grade_name"]

    def __str__(self):
        return self.grade_name
