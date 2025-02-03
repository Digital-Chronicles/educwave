from django.shortcuts import render, get_object_or_404
from .models import *
from django.views import generic 
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *       
from django.urls import reverse_lazy
from django.db.models import Q
from academic.models import Exam, StudentMark, Notes
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 

class TeacherList(LoginRequiredMixin, ListView):
    template_name = "teachers.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Teacher.objects.all()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(registration_id__icontains=search_query)
            )
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset =self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                "students":list(
                    page_obj.object_list.values(
                        "id","registration_id", "first_name", "last_name", "gender", "year_of_entry"
                    )
                ),
                "has_next":page_obj.has_next(),
                "has_previous":page_obj.has_previous(),
                "current_page":page_obj.number,
                "total_pages":paginator.num_pages,
            }
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


# Teacher Detail
@login_required
def teacher_details(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    teacher_payroll = PayrollInformation.objects.filter(teacher=teacher).first()
    education_background = EducationBackground.objects.filter(teacher=teacher)
    employment_history = EmploymentHistory.objects.filter(teacher=teacher)
    next_of_kin = NextOfKin.objects.filter(teacher=teacher).first()
    current_employment = CurrentEmployment.objects.filter(teacher=teacher).first()
    exams = Exam.objects.filter(created_by = teacher)[:5]
    uploaded_marks = StudentMark.objects.filter(teacher = teacher)[:5]
    notes = Notes.objects.all().filter(created_by = teacher)[:5][:5]

    context = {
        "teacher": teacher,
        "teacher_payroll": teacher_payroll,
        "education_background": education_background,
        "employment_history": employment_history,
        "next_of_kin": next_of_kin,
        "current_employment": current_employment,
        "exams":exams,
        "notes":notes,
        "uploaded_marks":uploaded_marks,
    }

    return render(request, "teachersDetails.html", context)


class RegisterTeacherDetails(LoginRequiredMixin, generic.CreateView):
    model = Teacher
    template_name = 'registerteacherdetails.html'
    form_class = TeacherForm

    def get_success_url(self):
        return reverse_lazy('teacher_payroll') + f'?teacher_id={self.object.id}'
    
class Teacher_Payroll(LoginRequiredMixin, generic.CreateView):
    model = PayrollInformation
    template_name = 'payroll.html'
    form_class = PayrollInformationForm
    success_url = reverse_lazy('teacher_educationbackground')  # Redirect to education background next

class Teacher_EducationBackground(LoginRequiredMixin, generic.CreateView):
    model = EducationBackground
    template_name = 'educationback.html'
    form_class = EducationBackgroundForm
    success_url = reverse_lazy('teacher_employmenthistory')  # Redirect to employment history next

class Teacher_EmploymentHistory(LoginRequiredMixin, generic.CreateView):
    model = EmploymentHistory
    template_name = 'employmenthistory.html'
    form_class = EmploymentHistoryForm
    success_url = reverse_lazy('teacher_nextofkin')  # Redirect to next of kin next

class Teacher_Next_of_Kin(LoginRequiredMixin, generic.CreateView):
    model = NextOfKin
    template_name = 'nextofkin.html'
    form_class = NextOfKinForm
    success_url = reverse_lazy('teacher_currentemployment')  # Redirect to current employment next

class Teacher_Current_Employment(LoginRequiredMixin, generic.CreateView):
    model = CurrentEmployment
    template_name = 'currentemployment.html'
    form_class = CurrentEmploymentForm
    success_url = reverse_lazy('teachers')  # Redirect back to teachers overview or home after the last step
