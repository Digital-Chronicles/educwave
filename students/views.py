from django.shortcuts import redirect, render
from django.views import generic
from finance.forms import StudentTuitionDescriptionForm
from finance.models import StudentTuitionDescription
from .models import Student, StudentAddress, CareTaker, StudentGrade
from .forms import StudentForm, StudentAddressForm, CareTakerForm, StudentGradeForm
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from .models import Student
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required


class StudentList(RoleRequiredMixin, ListView):
    template_name = "students.html"
    paginate_by = 10
    allowed_roles = ['TEACHER', 'ADMIN', "STUDENT"]

    def get_queryset(self):
        queryset = Student.objects.all()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(registration_id__icontains=search_query)
            )
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                "students": list(
                    page_obj.object_list.values(
                        "id", "registration_id", "first_name", "last_name",
                        "current_grade", "date_of_birth", "current_status"
                    )
                ),
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
            }
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


class RegisterStudentDetails(RoleRequiredMixin, CreateView):
    model = Student
    template_name = "registerStudentDetails.html"
    form_class = StudentForm
    allowed_roles = ['TEACHER', 'ADMIN']

    def form_valid(self, form):
        student = form.save()
        return redirect(f'/students/register/student-address/{student.pk}/')


class RegisterStudentAddress(RoleRequiredMixin, CreateView):
    model = StudentAddress
    template_name = "registerStudentAddress.html"
    form_class = StudentAddressForm
    allowed_roles = ['TEACHER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs['pk']
        student = get_object_or_404(Student, pk=student_id)
        context['student'] = student
        return context

    def form_valid(self, form):
        student_id = self.kwargs['pk']
        student = get_object_or_404(Student, pk=student_id)
        form.instance.student = student
        return super().form_valid(form)

    def get_success_url(self):
        return f'/students/register/student-caretaker/{self.object.student.pk}/'


class CareTakerCreateView(RoleRequiredMixin, CreateView):
    model = CareTaker
    form_class = CareTakerForm
    template_name = 'registerStudentCaretaker.html'
    allowed_roles = ['TEACHER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_pk')
        context['student_id'] = student_id
        return context

    def form_valid(self, form):
        student_id = self.kwargs.get('student_pk')
        student = get_object_or_404(Student, pk=student_id)
        form.instance.student = student
        return super().form_valid(form)

    def get_success_url(self):
        return f'/students/register/student-grade/{self.object.student.pk}/'


class StudentGradeCreateView(RoleRequiredMixin, CreateView):
    model = StudentGrade
    form_class = StudentGradeForm
    template_name = 'registerStudentGrade.html'
    allowed_roles = ['TEACHER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_pk')
        context['student_id'] = student_id
        return context

    def form_valid(self, form):
        student_id = self.kwargs.get('student_pk')
        student = get_object_or_404(Student, pk=student_id)
        form.instance.student = student
        return super().form_valid(form)

    def get_success_url(self):
        return "/students/"

# Student Detail View
@role_required(allowed_roles=['ADMIN', 'TEACHER'])
def studentDetail(request, id):
    student = get_object_or_404(Student, id=id)
    student_address = student.studentaddress if hasattr(
        student, 'studentaddress') else None
    caretakers = student.caretaker_set.all()

    return render(request, "studentDetail.html", {
        "student": student,
        "student_address": student_address,
        "caretakers": caretakers,
      
    })
  