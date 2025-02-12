from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views import generic 
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *       
from django.urls import reverse_lazy
from django.db.models import Q
from academic.models import Exam
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
                        "registration_id", "first_name", "last_name", "gender", "year_of_entry"
                    )
                ),
                "has_next":page_obj.has_next(),
                "has_previous":page_obj.has_previous(),
                "current_page":page_obj.number,
                "total_pages":paginator.num_pages,
            }
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

# def teachers(request):
#     teachers = Teacher.objects.all()

#     return render(request, 'teachers.html', {'teachers':teachers})

# Teacher Detail
def teacher_details(request, id):
    # Fetch teacher object
    teacher = get_object_or_404(Teacher, id=id)

    # Attempt to get PayrollInformation, return None if not found
    teacher_payroll = PayrollInformation.objects.filter(teacher=teacher).first()
    education_background = EducationBackground.objects.filter(teacher=teacher)
    employment_history = EmploymentHistory.objects.filter(teacher=teacher)
    next_of_kin = NextOfKin.objects.filter(teacher=teacher).first()
    current_employment = CurrentEmployment.objects.filter(teacher=teacher).first()
    uploaded_exams = Exam.objects.filter(created_by = teacher)

    # Prepare context for template rendering
    context = {
        "teacher": teacher,
        "teacher_payroll": teacher_payroll,
        "education_background": education_background,
        "employment_history": employment_history,
        "next_of_kin": next_of_kin,
        "current_employment": current_employment,
        "uploaded_exams":uploaded_exams,
    }

    return render(request, "teachersDetails.html", context)


class RegisterTeacherDetails(LoginRequiredMixin, generic.CreateView):
    model = Teacher
    template_name = 'registerteacherdetails.html'
    form_class = TeacherForm

    def form_valid(self, form):
        teacher = form.save()
        return redirect(f'/teachers/details/{teacher.pk}/') 
    
class Teacher_Payroll(LoginRequiredMixin, generic.CreateView):
    model = PayrollInformation
    template_name = 'payroll.html'
    form_class = PayrollInformationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the education background registration page with the teacher_id
        return redirect(f'/teachers/register/educatio_nbackground/{self.object.teacher.id}')

class Teacher_EducationBackground(LoginRequiredMixin, generic.CreateView):
    model = EducationBackground
    template_name = 'educationback.html'
    form_class = EducationBackgroundForm

    def get_initial(self):
        # Retrieve teacher_id from query parameters
        teacher_id = self.request.GET.get('teacher_id')
        return {'teacher': teacher_id}

    def form_valid(self, form):
        # Associate the education background with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the employment history registration page with the teacher_id
        return reverse_lazy('teacher_employmenthistory') + f'?teacher_id={self.object.teacher.id}'

class Teacher_EmploymentHistory(LoginRequiredMixin, generic.CreateView):
    model = EmploymentHistory
    template_name = 'employmenthistory.html'
    form_class = EmploymentHistoryForm

    def get_initial(self):
        # Retrieve teacher_id from query parameters
        teacher_id = self.request.GET.get('teacher_id')
        return {'teacher': teacher_id}

    def form_valid(self, form):
        # Associate the employment history with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the next of kin registration page with the teacher_id
        return reverse_lazy('teacher_nextofkin') + f'?teacher_id={self.object.teacher.id}'

class Teacher_Next_of_Kin(LoginRequiredMixin, generic.CreateView):
    model = NextOfKin
    template_name = 'nextofkin.html'
    form_class = NextOfKinForm

    def get_initial(self):
        # Retrieve teacher_id from query parameters
        teacher_id = self.request.GET.get('teacher_id')
        return {'teacher': teacher_id}

    def form_valid(self, form):
        # Associate the next of kin with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the current employment registration page with the teacher_id
        return reverse_lazy('teacher_currentemployment') + f'?teacher_id={self.object.teacher.id}'

class Teacher_Current_Employment(LoginRequiredMixin, generic.CreateView):
    model = CurrentEmployment
    template_name = 'currentemployment.html'
    form_class = CurrentEmploymentForm

    def get_initial(self):
        # Retrieve teacher_id from query parameters
        teacher_id = self.request.GET.get('teacher_id')
        return {'teacher': teacher_id}

    def form_valid(self, form):
        # Associate the current employment with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the teachers list page after completing the registration
        return reverse_lazy('teachers')