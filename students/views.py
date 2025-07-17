from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, CreateView
from django.contrib import messages
from management.models import GeneralInformation
from .models import Student, StudentAddress, CareTaker, StudentGrade
from academic.models import Grade
from .forms import StudentForm, StudentAddressForm, CareTakerForm, StudentGradeForm
from accounts.mixins import RoleRequiredMixin

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
    success_url = '/students/'
    allowed_roles = ['TEACHER', 'ADMIN']
    
    def form_valid(self, form):
        school = GeneralInformation.objects.first()
        if not school:
            raise Http404("No school information found")
        form.instance.school = school
        form.instance.registered_by = self.request.user
        return super().form_valid(form)


def studentDetail(request, id):
    student = get_object_or_404(Student, id=id)
    student_address = StudentAddress.objects.filter(student=student).first()
    caretakers = CareTaker.objects.filter(student=student)
    student_grades = StudentGrade.objects.filter(student=student).order_by('-assigned_date')
    grades = Grade.objects.all()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'student':
            form = StudentForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Student information updated successfully!')
                return redirect('StudentDetail', id=id)
        
        elif form_type == 'address':
            if student_address:
                form = StudentAddressForm(request.POST, instance=student_address)
            else:
                form = StudentAddressForm(request.POST)
            
            if form.is_valid():
                address = form.save(commit=False)
                address.student = student
                address.save()
                messages.success(request, 'Address updated successfully!')
                return redirect('StudentDetail', id=id)
        
        elif form_type == 'caretaker':
            caretaker_id = request.POST.get('caretaker_id')
            if caretaker_id:
                caretaker = get_object_or_404(CareTaker, id=caretaker_id, student=student)
                form = CareTakerForm(request.POST, instance=caretaker)
            else:
                form = CareTakerForm(request.POST)
            
            if form.is_valid():
                caretaker = form.save(commit=False)
                caretaker.student = student
                caretaker.save()
                action = 'updated' if caretaker_id else 'added'
                messages.success(request, f'Caretaker {action} successfully!')
                return redirect('StudentDetail', id=id)
        
        elif form_type == 'grade':
            grade_id = request.POST.get('grade_id')
            if grade_id:
                # Updating existing grade record
                grade_record = get_object_or_404(StudentGrade, id=grade_id, student=student)
                form = StudentGradeForm(request.POST, instance=grade_record)
            else:
                # Creating new grade record
                form = StudentGradeForm(request.POST)
            
            if form.is_valid():
                grade_record = form.save(commit=False)
                grade_record.student = student
                grade_record.save()
                
                # Update student's current grade only if this is the most recent assignment
                latest_grade = StudentGrade.objects.filter(student=student).order_by('-assigned_date').first()
                if latest_grade and latest_grade.id == grade_record.id:
                    student.current_grade = grade_record.class_assigned
                    student.save()
                
                messages.success(request, 'Academic record updated successfully!')
                return redirect('StudentDetail', id=id)

        
        elif form_type == 'delete_caretaker':
            caretaker_id = request.POST.get('caretaker_id')
            caretaker = get_object_or_404(CareTaker, id=caretaker_id, student=student)
            caretaker.delete()
            messages.success(request, 'Caretaker deleted successfully!')
            return redirect('StudentDetail', id=id)

    context = {
        'student': student,
        'student_address': student_address,
        'caretakers': caretakers,
        'student_grades': student_grades,
        'grades': grades,
    }
    return render(request, 'studentDetail.html', context)