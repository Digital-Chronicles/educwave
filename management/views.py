# management/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q  # 👈 NEW

from students.models import Student
from academic.models import Grade
from teachers.models import Teacher

from management.forms import (
    ApplicationSettingForm,
    LessonForm,
    SchedulingSettingForm,
    CertificateAwardForm,
    GradeForm,
    TransactionSettingForm,
    GeneralInformationForm,
)
from management.models import (
    GeneralInformation,
    ApplicationSetting,
    Lesson,
    SchedulingSetting,
    CertificateAward,
    Ranking_Grade,
    TransactionSetting,
)
from accounts.decorators import role_required


@login_required
def dashboard(request):
    """
    Main school dashboard:
    - High-level counts (students, teachers, grades)
    - Active vs inactive students
    - Gender distribution (active students)
    - School type breakdown (Day / Boarding / Bursary)
    - Per-grade student stats
    - Recently registered students
    """

    # ---------- Base querysets ----------
    students_qs = Student.objects.select_related("current_grade")
    teachers_qs = Teacher.objects.all()

    # ---------- Global counts ----------
    students_count = students_qs.count()
    teachers_count = teachers_qs.count()
    grades_count = Grade.objects.count()

    # ---------- Status counts ----------
    active_student_count = students_qs.filter(current_status="active").count()
    graduated_student_count = students_qs.filter(current_status="graduated").count()
    dropped_out_student_count = students_qs.filter(current_status="dropped out").count()
    inactive_student_count = graduated_student_count + dropped_out_student_count

    # ---------- Gender counts (only active students) ----------
    male_count = students_qs.filter(
        current_status="active", gender="Male"
    ).count()
    female_count = students_qs.filter(
        current_status="active", gender="Female"
    ).count()

    # ---------- School type breakdown (only active students) ----------
    school_type_raw = (
        students_qs.filter(current_status="active")
        .values("school_type")
        .annotate(count=Count("id"))
    )
    # Normalise keys so your template has nice labels
    school_type_label_map = {
        "day": "Day",
        "boarding": "Boarding",
        "bursary": "Bursary",
        "scholarhip": "Scholarship",
        None: "Unknown",
        "": "Unknown",
    }
    school_type_counts = {
        school_type_label_map.get(row["school_type"], row["school_type"] or "Unknown"): row["count"]
        for row in school_type_raw
    }

    # ---------- Data structures suitable for charts/cards ----------
    student_status_data = {
        "Active": active_student_count,
        "Graduated": graduated_student_count,
        "Dropped Out": dropped_out_student_count,
    }

    student_gender_data = {
        "Male": male_count,
        "Female": female_count,
    }

    # ---------- Per-grade stats (active + total students per grade) ----------
    grade_stats = (
        Grade.objects
        .annotate(
            total_students=Count("student"),
            active_students=Count(
                "student",
                filter=Q(student__current_status="active"),
            ),
        )
        .order_by("grade_name")
    )
    # NOTE:
    # The reverse relation name "student" is the default from Student.current_grade FK.

    # ---------- Recently registered students (latest 5) ----------
    recent_students = students_qs.order_by("-created")[:5]

    context = {
        # Top-level counts
        "students_count": students_count,
        "teachers_count": teachers_count,
        "grades_count": grades_count,

        # Status & gender
        "active_student_count": active_student_count,
        "graduated_student_count": graduated_student_count,
        "inactive_student_count": inactive_student_count,
        "student_status_data": student_status_data,
        "student_gender_data": student_gender_data,

        # School type stats
        "school_type_counts": school_type_counts,

        # Per-grade stats & recent students
        "grade_stats": grade_stats,
        "recent_students": recent_students,
    }
    return render(request, "dashboard.html", context)


@role_required(allowed_roles=["ADMIN", "ACADEMIC"])
def create_general_information(request):
    # Only one GeneralInformation instance allowed
    if GeneralInformation.objects.exists():
        existing_instance = GeneralInformation.objects.first()
        return render(
            request,
            "generalInformation.html",
            {"existing_instance": existing_instance},
        )

    if request.method == "POST":
        form = GeneralInformationForm(request.POST, request.FILES)
        if form.is_valid():
            general_info = form.save(commit=False)
            general_info.registered_by = request.user
            try:
                general_info.save()
                return redirect("/")
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = GeneralInformationForm()

    return render(request, "create_general_information.html", {"form": form})


@role_required(allowed_roles=["ADMIN"])
def create_application_setting(request):
    if request.method == "POST":
        form = ApplicationSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("application_setting_list")
    else:
        form = ApplicationSettingForm()
    return render(request, "create_application_setting.html", {"form": form})


@role_required(allowed_roles=["ADMIN", "ACADEMIC"])
def create_lesson(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lesson_list")
    else:
        form = LessonForm()
    return render(request, "create_lesson.html", {"form": form})


@role_required(allowed_roles=["ADMIN"])
def create_scheduling_setting(request):
    if request.method == "POST":
        form = SchedulingSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("scheduling_setting_list")
    else:
        form = SchedulingSettingForm()
    return render(request, "create_scheduling_setting.html", {"form": form})


@role_required(allowed_roles=["ADMIN", "ACADEMIC"])
def create_certificate_award(request):
    if request.method == "POST":
        form = CertificateAwardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("certificate_award_list")
    else:
        form = CertificateAwardForm()
    return render(request, "create_certificate_award.html", {"form": form})


@role_required(allowed_roles=["ADMIN", "ACADEMIC"])
def create_grade(request):
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("grade_list")
    else:
        form = GradeForm()
    return render(request, "create_grade.html", {"form": form})


@role_required(allowed_roles=["ADMIN"])
def create_transaction_setting(request):
    if request.method == "POST":
        form = TransactionSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("transaction_setting_list")
    else:
        form = TransactionSettingForm()
    return render(request, "create_transaction_setting.html", {"form": form})
