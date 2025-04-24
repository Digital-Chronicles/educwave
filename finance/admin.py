from django.contrib import admin
from .models import SchoolFees, OtherSchoolPayments, TransportFee, StudentTuitionDescription, FeeTransaction

@admin.register(SchoolFees)
class SchoolFeesAdmin(admin.ModelAdmin):
    list_display = ('grade', 'tuitionfee', 'hostelfee', 'breakfastfee', 'lunchfee', 'created', 'updated', 'created_by')
    search_fields = ('grade__grade_name', 'created_by__username')
    list_filter = ('created', 'updated', 'grade')
    readonly_fields = ('created', 'updated')

@admin.register(OtherSchoolPayments)
class OtherSchoolPaymentsAdmin(admin.ModelAdmin):
    list_display = ('grade', 'fees_type', 'amount', 'created', 'updated', 'created_by')
    search_fields = ('grade__grade_name', 'fees_type', 'created_by__username')
    list_filter = ('fees_type', 'created', 'updated', 'grade')
    readonly_fields = ('created', 'updated')

@admin.register(TransportFee)
class TransportFeeAdmin(admin.ModelAdmin):
    list_display = ('location', 'amount', 'created', 'updated', 'created_by')
    search_fields = ('location', 'created_by__username')
    list_filter = ('created', 'updated')
    readonly_fields = ('created', 'updated')

@admin.register(StudentTuitionDescription)
class StudentTuitionDescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'student', 
        'tuition', 
        'hostel', 
        'lunch', 
        'breakfast', 
        'total_fee'
    )
    list_filter = ('hostel', 'lunch', 'breakfast',"tuition")
    search_fields = ('student__name', 'tuition__grade__grade_name',)
    readonly_fields = ('total_fee',)

@admin.register(FeeTransaction)
class FeeTransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_due', 'amount_paid', 'status', 'payment_method', 'due_date', 'last_payment_date', 'created')
    list_filter = ('status', 'payment_method', 'created', 'updated')
    search_fields = ('student__student__first_name', 'student__student__last_name', 'payment_reference', 'remarks')
    ordering = ('-created',)
    readonly_fields = ('created', 'updated', 'last_payment_date')

    fieldsets = (
        ("Payment Details", {
            "fields": (
                'student', 'amount_paid', 'payment_method', 'payment_reference', 'receipt_url',
                'remarks',
            ),
        }),
        ("Status & Dates", {
            "fields": ('status', 'last_payment_date', 'created', 'updated'),
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset for admin."""
        queryset = super().get_queryset(request)
        return queryset.select_related('student')

    def student(self, obj):
        """Display the student's full name."""
        return f"{obj.student.student.first_name} {obj.student.student.last_name}"
    student.admin_order_field = 'student__student__first_name'
    student.short_description = 'Student'

    def save_model(self, request, obj, form, change):
        """Custom save logic for FeeTransaction."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
