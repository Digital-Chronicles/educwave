# students/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from management.models import GeneralInformation
from accounts.mixins import RoleRequiredMixin

from .models import Student, StudentAddress, CareTaker, StudentGrade
from academic.models import Grade
from .forms import (
    StudentForm,
    StudentAddressForm,
    CareTakerForm,
    StudentGradeForm,
)


# ---------------------------------------------------------------------------
# STUDENT LIST + FILTERS + AJAX
# ---------------------------------------------------------------------------
@login_required
def studentList(request):
    """
    Main student list (HTML + AJAX).

    - Normal GET: renders the table shell (students/student_list.html).
      The table body is filled via JavaScript using AJAX.

    - AJAX GET (x-requested-with=XMLHttpRequest):
      Returns JSON with:
        * filters: search, status, grade_filter, school_type
        * pagination: page, total_count, has_next, has_previous, etc.
    """

    # 1) Base queryset
    qs = Student.objects.select_related("current_grade").all()

    # 2) Read filters
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()           # "active", "graduated", "dropped out"
    grade_filter = request.GET.get("grade_filter", "").strip()  # "with", "without", or ""
    school_type = request.GET.get("school_type", "").strip()     # "day", "boarding", "bursary", "scholarhip"
    page_number = request.GET.get("page", "1")

    # 3) Search filter
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(registration_id__icontains=search)
            | Q(guardian_phone__icontains=search)
        )

    # 4) Status filter (values in DB are lowercase)
    if status:
        qs = qs.filter(current_status=status)

    # 5) Filter by having / not having a current_grade
    if grade_filter == "with":
        qs = qs.filter(current_grade__isnull=False)
    elif grade_filter == "without":
        qs = qs.filter(current_grade__isnull=True)

    # 6) School type filter
    if school_type:
        qs = qs.filter(school_type=school_type)

    qs = qs.order_by("first_name", "last_name")

    # 7) Pagination
    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(page_number)

    # 8) AJAX JSON response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        students_data = []
        for s in page_obj:
            students_data.append(
                {
                    "id": s.id,
                    "registration_id": s.registration_id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "current_grade": s.current_grade.grade_name if s.current_grade else "",
                    "date_of_birth": s.date_of_birth.strftime("%Y-%m-%d"),
                    "current_status": s.current_status,
                    "school_type": s.school_type,
                    "guardian_phone": s.guardian_phone or "",
                }
            )

        if paginator.count:
            start_index = page_obj.start_index()
            end_index = page_obj.end_index()
        else:
            start_index = 0
            end_index = 0

        return JsonResponse(
            {
                "students": students_data,
                "has_previous": page_obj.has_previous(),
                "has_next": page_obj.has_next(),
                "current_page": page_obj.number,
                "total_count": paginator.count,
                "start_index": start_index,
                "end_index": end_index,
            }
        )

    # 9) Normal HTML render
    # If you want, you can pass choices here for dropdown filters.
    context = {}
    return render(request, "students.html", context)


# ---------------------------------------------------------------------------
# REGISTER NEW STUDENT
# ---------------------------------------------------------------------------
class RegisterStudentDetails(RoleRequiredMixin, CreateView):
    """
    Create a new Student with:
    - default school from GeneralInformation
    - registered_by set to current user
    """
    model = Student
    template_name = "registerStudentDetails.html"
    form_class = StudentForm
    success_url = "/students/"
    allowed_roles = ["TEACHER", "ADMIN"]

    def form_valid(self, form):
        school = GeneralInformation.objects.first()
        if not school:
            raise Http404("No school information found")

        form.instance.school = school
        form.instance.registered_by = self.request.user
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# STUDENT DETAIL / PROFILE (EDIT + RELATED FORMS)
# ---------------------------------------------------------------------------
@login_required
def studentDetail(request, id):
    """
    Full student profile view:
    - Basic student info (StudentForm)
    - Address info (StudentAddressForm)
    - Caretakers (CareTakerForm, add/update/delete)
    - Academic history (StudentGradeForm)
      * Also updates student's current_grade with the latest assigned grade.
    """
    student = get_object_or_404(Student, id=id)

    # Related objects
    student_address = StudentAddress.objects.filter(student=student).first()
    caretakers = CareTaker.objects.filter(student=student)
    student_grades = StudentGrade.objects.filter(student=student).order_by("-assigned_date")
    grades = Grade.objects.all()

    # Default (unbound) forms for GET or when validation fails
    student_form = StudentForm(instance=student)
    address_form = StudentAddressForm(instance=student_address) if student_address else StudentAddressForm()
    caretaker_form = CareTakerForm()
    grade_form = StudentGradeForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # --- Update core student info ----------------------------------------
        if form_type == "student":
            student_form = StudentForm(request.POST, request.FILES, instance=student)
            if student_form.is_valid():
                student_form.save()
                messages.success(request, "Student information updated successfully!")
                return redirect("StudentDetail", id=id)

        # --- Update / create address ----------------------------------------
        elif form_type == "address":
            if student_address:
                address_form = StudentAddressForm(request.POST, instance=student_address)
            else:
                address_form = StudentAddressForm(request.POST)

            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.student = student
                address.save()
                messages.success(request, "Address updated successfully!")
                return redirect("StudentDetail", id=id)

        # --- Add / update caretaker -----------------------------------------
        elif form_type == "caretaker":
            caretaker_id = request.POST.get("caretaker_id")
            if caretaker_id:
                caretaker_instance = get_object_or_404(CareTaker, id=caretaker_id, student=student)
                caretaker_form = CareTakerForm(request.POST, instance=caretaker_instance)
            else:
                caretaker_form = CareTakerForm(request.POST)

            if caretaker_form.is_valid():
                caretaker = caretaker_form.save(commit=False)
                caretaker.student = student
                caretaker.save()
                action = "updated" if caretaker_id else "added"
                messages.success(request, f"Caretaker {action} successfully!")
                return redirect("StudentDetail", id=id)

        # --- Add / update academic grade record -----------------------------
        elif form_type == "grade":
            grade_id = request.POST.get("grade_id")
            if grade_id:
                grade_instance = get_object_or_404(StudentGrade, id=grade_id, student=student)
                grade_form = StudentGradeForm(request.POST, instance=grade_instance)
            else:
                grade_form = StudentGradeForm(request.POST)

            if grade_form.is_valid():
                grade_record = grade_form.save(commit=False)
                grade_record.student = student
                grade_record.save()

                # Update student's current grade based on the latest assigned_date
                latest_grade = (
                    StudentGrade.objects.filter(student=student)
                    .order_by("-assigned_date")
                    .first()
                )
                if latest_grade and latest_grade.id == grade_record.id:
                    student.current_grade = grade_record.class_assigned
                    student.save()

                messages.success(request, "Academic record updated successfully!")
                return redirect("StudentDetail", id=id)

        # --- Delete caretaker -----------------------------------------------
        elif form_type == "delete_caretaker":
            caretaker_id = request.POST.get("caretaker_id")
            caretaker = get_object_or_404(CareTaker, id=caretaker_id, student=student)
            caretaker.delete()
            messages.success(request, "Caretaker deleted successfully!")
            return redirect("StudentDetail", id=id)

    # GET request or invalid POST → render with bound forms (showing errors)
    context = {
        "student": student,
        "student_address": student_address,
        "caretakers": caretakers,
        "student_grades": student_grades,
        "grades": grades,
        "student_form": student_form,
        "address_form": address_form,
        "caretaker_form": caretaker_form,
        "grade_form": grade_form,
    }
    return render(request, "studentDetail.html", context)
