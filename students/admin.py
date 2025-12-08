from django.contrib import admin
from .models import Student, StudentAddress, CareTaker, StudentGrade


class HasGradeFilter(admin.SimpleListFilter):
    title = "Grade status"          # label in the sidebar
    parameter_name = "has_grade"    # query param name

    def lookups(self, request, model_admin):
        return (
            ("yes", "With grade"),
            ("no", "Without grade"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "yes":
            return queryset.exclude(current_grade__isnull=True)
        if value == "no":
            return queryset.filter(current_grade__isnull=True)
        return queryset


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'registration_id',
        'lin_id',
        'first_name',
        'last_name',
        'school_type',
        'current_status',
        'current_grade',
        'guardian_name',
        'finance_balance',   # 👈 NEW: shows balance from finance
        'created',
        'updated',
    )

    search_fields = (
        'registration_id',
        'first_name',
        'last_name',
        'lin_id',
        'school_type',
        'current_grade__grade_name',
    )

    list_filter = (
        'current_status',
        'current_grade',
        HasGradeFilter,      # “with / without grade” filter
        'created',
        'school_type',
        'gender',
    )

    ordering = ('first_name',)
    readonly_fields = ('created', 'updated')

    # ==== BALANCE COLUMN ====
    def finance_balance(self, obj):
        """
        Uses Student.get_finance_balance() helper.
        Returns "-" if no tuition description yet.
        """
        balance = getattr(obj, "get_finance_balance", None)
        if callable(balance):
            value = balance()
        else:
            value = None

        if value is None:
            return "-"

        return value

    finance_balance.short_description = "Balance"
    # If you later annotate/queryset with a balance field,
    # you can also add: finance_balance.admin_order_field = '...' 


class StudentAddressAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'address',
        'city',
        'state',
        'zip_code',
        'created',
        'updated',
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'city',
        'state',
    )
    list_filter = ('state', 'created')
    readonly_fields = ('created', 'updated')


class CareTakerAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'name',
        'relationship',
        'contact_number',
        'email',
        'created',
        'updated',
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'name',
        'contact_number',
    )
    list_filter = ('relationship', 'created')
    readonly_fields = ('created', 'updated')


class StudentGradeAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'class_assigned',
        'assigned_date',
        'created',
        'updated',
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'class_assigned__grade_name',
    )
    list_filter = ('assigned_date', 'created')
    readonly_fields = ('created', 'updated')


admin.site.register(Student, StudentAdmin)
admin.site.register(StudentAddress, StudentAddressAdmin)
admin.site.register(CareTaker, CareTakerAdmin)
admin.site.register(StudentGrade, StudentGradeAdmin)
