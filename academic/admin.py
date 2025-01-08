from django.contrib import admin
from .models import *

# Custom Action Example
def mark_as_updated(modeladmin, request, queryset):
    queryset.update(updated=True)
mark_as_updated.short_description = "Mark selected as updated"

# Grade Model
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('grade_name', 'class_teacher', 'created', 'updated')
    search_fields = ('grade_name', 'class_teacher__name')
    list_filter = ('grade_name', 'class_teacher')
    ordering = ['grade_name']
    readonly_fields = ('created', 'updated')
    actions = [mark_as_updated]

# Subject Model
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'curriculum', 'created', 'updated')
    search_fields = ('name', 'description', 'curriculum__name')
    list_filter = ('name', 'curriculum')
    ordering = ['name']
    readonly_fields = ('created', 'updated')

# Curriculum Model
@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('name', 'objectives', 'learning_outcomes', 'created', 'updated')
    search_fields = ('name', 'objectives', 'learning_outcomes')
    list_filter = ('name',)
    ordering = ['name']
    readonly_fields = ('created', 'updated')

# Topic Model
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'order', 'created', 'updated')
    search_fields = ('name', 'subject__name')
    list_filter = ('subject', 'order')
    ordering = ['subject', 'order']
    readonly_fields = ('created', 'updated')

# Exam Model
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'duration_minutes', 'grade', 'created_by', 'created', 'updated')
    search_fields = ('subject__name', 'description', 'grade__grade_name', 'created_by__name')
    list_filter = ('date', 'subject', 'grade', 'created_by')
    ordering = ['date', 'subject']
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'date'  # Enables hierarchical navigation by date
