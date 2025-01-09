from django.shortcuts import render
from .models import *
from django.views import generic 
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *       
from django.urls import reverse_lazy



def teachers(request):
    teachers = Teacher.objects.all()

    return render(request, 'teachers.html', {'teachers':teachers})



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
