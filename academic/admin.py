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
    list_display = ('name', 'description', 'curriculum', 'created', )
    search_fields = ('name', 'description', 'curriculum')
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


# Exam Model
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'duration_minutes', 'grade', 'created_by', 'created', 'updated')
    search_fields = ('subject__name', 'description', 'grade__grade_name', 'created_by__name')
    list_filter = ('date', 'subject', 'grade', 'created_by')
    ordering = ['date', 'subject']
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'date' 

# Notes Model
@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_by', 'grade', 'created', 'updated')
    list_filter = ('subject', 'grade', 'created_by')  
    search_fields = ('subject__name', 'created_by__name', 'notes_content') 
    ordering = ('-created',)
    fields = ('subject', 'topics', 'notes_file', 'notes_content', 'description', 'grade', 'created_by') 
    filter_horizontal = ('topics',)  
    readonly_fields = ('created', 'updated') 

    class Media:
        css = {
            'all': ('notes_admin.css',) 
        }


@admin.register(TermExamSession)
class TermsAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'start_date', 'end_date', 'created_by', 'created', 'updated')
    list_filter = ('start_date', 'end_date', 'created_by')
    search_fields = ('term_name', 'created_by__name')
    date_hierarchy = 'start_date'
    ordering = ['term_name']


admin.site.register(StudentMarkSummary)