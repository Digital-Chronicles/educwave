from django.shortcuts import redirect, render
from django.views import generic
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


class StudentList(LoginRequiredMixin, ListView):
    template_name = "students.html"
    paginate_by = 10

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


class RegisterStudentDetails(LoginRequiredMixin, CreateView):
    model = Student
    template_name = "registerStudentDetails.html"
    form_class = StudentForm

    def form_valid(self, form):
        student = form.save()
        return redirect(f'/students/register/student-address/{student.pk}/')


class RegisterStudentAddress(LoginRequiredMixin, CreateView):
    model = StudentAddress
    template_name = "registerStudentAddress.html"
    form_class = StudentAddressForm

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


class CareTakerCreateView(LoginRequiredMixin, CreateView):
    model = CareTaker
    form_class = CareTakerForm
    template_name = 'registerStudentCaretaker.html'

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


class StudentGradeCreateView(LoginRequiredMixin, CreateView):
    model = StudentGrade
    form_class = StudentGradeForm
    template_name = 'registerStudentGrade.html'

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
@login_required(login_url='login')
def studentDetail(request, id):
    # Fetch the student using get_object_or_404, which will raise a 404 error if the student doesn't exist
    student = get_object_or_404(Student, id=id)
    
    # You can also fetch related data, like address or guardians, if needed
    student_address = student.studentaddress if hasattr(student, 'studentaddress') else None
    caretakers = student.caretaker_set.all()  # All caretakers related to the student
    
    # Pass the student and related data to the template
    return render(request, "studentDetail.html", {
        "student": student,
        "student_address": student_address,
        "caretakers": caretakers
    })
