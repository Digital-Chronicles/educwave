from django.contrib import admin
from .models import *

# Customizing the display of the Teacher model
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('initials','registration_id' , 'first_name','last_name','gender')
    search_fields = ('registration_id','first_name','last_name',)
    list_filter = ('gender','registered_by')
    ordering = ('first_name',)
    readonly =('registered_by')


# Customizing the display of the PayrollInfo model
@admin.register(PayrollInformation)
class PayrollInformationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'salary','account_number','payment_frequency')
    search_fields = ('teacher','bank_name','salary')
    list_filter = ('bank_name','payment_frequency')
   
    readonly =('tax_identification_number','nssf_number')
    
# Customizing the display of the EducationBackground model
@admin.register(EducationBackground)
class EducationBackgroundAdmin(admin.ModelAdmin):
    list_display = ('teacher' , 'education_award','institution','graduation_year')
    search_fields = ('teacher','institution','education_award')
    list_filter = ('education_award','institution','graduation_year')
    
    readonly =('result_obtained')

# Customizing the display of the EmploymentHistory model
@admin.register(EmploymentHistory)
class EmploymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('teacher' , 'organization','department','role', 'responsibilities')
    search_fields = ('teacher','organuzation','department','role')
    list_filter = ('organization','department')
    


# Customizing the display of the NextOfKin model
@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ('teacher' , 'name','relationship','contact_number')
    search_fields = ('teacher','name','relationship',)
    list_filter = ('relationship',)
    ordering = ('teacher',)




# Customizing the display of the CurrentEmployment model
@admin.register(CurrentEmployment)
class CurrentEmploymentAdmin(admin.ModelAdmin):
    list_display = ('teacher' , 'position','department')
    search_fields = ('teacher','department')
    list_filter = ('position','department')
