from django.contrib import admin
from .models import Student, StudentAddress, CareTaker, StudentGrade

# Customizing the display of the Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_id', 'first_name', 'last_name',
                    'current_status', 'current_grade', 'guardian_name', 'created', 'updated')
    search_fields = ('registration_id', 'first_name',
                     'last_name', 'current_grade')
    list_filter = ('current_status', 'current_grade', 'created')
    ordering = ('first_name',)
    readonly_fields = ('created', 'updated')  # To make the fields read-only

# Customizing the display of the StudentAddress model
class StudentAddressAdmin(admin.ModelAdmin):
    list_display = ('student', 'address', 'city', 'state', 'zip_code', 'created', 'updated')
    search_fields = ('student__first_name', 'student__last_name', 'city', 'state')
    list_filter = ('state', 'created')
    readonly_fields = ('created', 'updated')

# Customizing the display of the CareTaker model
class CareTakerAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'relationship', 'contact_number', 'email', 'created', 'updated')
    search_fields = ('student__first_name', 'student__last_name', 'name', 'contact_number')
    list_filter = ('relationship', 'created')
    readonly_fields = ('created', 'updated')

# Customizing the display of the StudentGrade model
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_assigned', 'assigned_date', 'created', 'updated')
    search_fields = ('student__first_name', 'student__last_name', 'class_assigned__name')
    list_filter = ('assigned_date', 'created')
    readonly_fields = ('created', 'updated')

# Register the models and their customized admin views
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentAddress, StudentAddressAdmin)
admin.site.register(CareTaker, CareTakerAdmin)
admin.site.register(StudentGrade, StudentGradeAdmin)
