# management/admin.py

from django.contrib import admin
from .models import *

# General Information Model
@admin.register(GeneralInformation)
class GeneralInformationAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'established_year', 'contact_number', 'email', 'created', 'updated')
    search_fields = ('school_name', 'email')
    list_filter = ('established_year',)
    ordering = ['school_name']

# Application Setting Model
@admin.register(ApplicationSetting)
class ApplicationSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_name', 'value', 'last_updated', 'created', 'updated')
    search_fields = ('setting_name', 'value')
    list_filter = ('last_updated',)
    ordering = ['setting_name']

# Lesson Model
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('class_assigned', 'subject', 'teacher', 'topic', 'lesson_date', 'duration_minutes', 'created', 'updated')
    search_fields = ('subject__name', 'teacher__name', 'topic__name')
    list_filter = ('class_assigned', 'subject', 'teacher')
    ordering = ['lesson_date', 'class_assigned']

# Scheduling Setting Model
@admin.register(SchedulingSetting)
class SchedulingSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_name', 'value', 'last_updated', 'created', 'updated')
    search_fields = ('setting_name', 'value')
    list_filter = ('last_updated',)
    ordering = ['setting_name']

# Certificate Award Model
@admin.register(CertificateAward)
class CertificateAwardAdmin(admin.ModelAdmin):
    list_display = ('student', 'award_name', 'awarded_by', 'date_awarded', 'created', 'updated')
    search_fields = ('award_name', 'student__first_name', 'student__last_name', 'awarded_by')
    list_filter = ('date_awarded',)
    ordering = ['date_awarded']

# Grade Model
@admin.register(Ranking_Grade)
class RankingGradeAdmin(admin.ModelAdmin):
    list_display = ('grade', 'min_percentage', 'max_percentage', 'description', 'created', 'updated')
    search_fields = ('grade',)
    list_filter = ('min_percentage', 'max_percentage')
    ordering = ['grade']

# Transaction Setting Model
@admin.register(TransactionSetting)
class TransactionSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_name', 'value', 'last_updated', 'created', 'updated')
    search_fields = ('setting_name', 'value')
    list_filter = ('last_updated',)
    ordering = ['setting_name']
