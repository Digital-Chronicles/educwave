from django.shortcuts import render, redirect
from students.models import Student,Grade
from management.forms import *
from management.models import *
from django.core.exceptions import ValidationError
from .models import GeneralInformation
from .forms import GeneralInformationForm

# Create your views here.
def dashboard(request):
    students_count = Student.objects.all().count()
    teachers_count = Teacher.objects.all().count()

    context = {
        "students_count":students_count,
        "teachers_count":teachers_count,
    }
    return render(request, "dashboard.html", context)



def create_general_information(request):
    # Check if an instance of GeneralInformation already exists
    if GeneralInformation.objects.exists():
        existing_instance = GeneralInformation.objects.first()
        return render(
            request, 'generalInformation.html', {'existing_instance': existing_instance}
        )

    if request.method == 'POST':
        form = GeneralInformationForm(request.POST)
        if form.is_valid():
            general_info = form.save(commit=False)
            general_info.registered_by = request.user
            try:
                general_info.save()
                return redirect('/')
            except ValidationError as e:
                form.add_error(None, e.message)  # Add the error to the form for user feedback
    else:
        form = GeneralInformationForm()

    return render(request, 'create_general_information.html', {'form': form})



def create_application_setting(request):
    if request.method == 'POST':
        form = ApplicationSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('application_setting_list')
    else:
        form = ApplicationSettingForm()
    return render(request, 'create_application_setting.html', {'form': form})


def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lesson_list')
    else:
        form = LessonForm()
    return render(request, 'create_lesson.html', {'form': form})


def create_scheduling_setting(request):
    if request.method == 'POST':
        form = SchedulingSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('scheduling_setting_list')
    else:
        form = SchedulingSettingForm()
    return render(request, 'create_scheduling_setting.html', {'form': form})


def create_certificate_award(request):
    if request.method == 'POST':
        form = CertificateAwardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('certificate_award_list')
    else:
        form = CertificateAwardForm()
    return render(request, 'create_certificate_award.html', {'form': form})


def create_grade(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('grade_list')
    else:
        form = GradeForm()
    return render(request, 'create_grade.html', {'form': form})


def create_transaction_setting(request):
    if request.method == 'POST':
        form = TransactionSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_setting_list')
    else:
        form = TransactionSettingForm()
    return render(request, 'create_transaction_setting.html', {'form': form})
