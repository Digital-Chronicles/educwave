from django.shortcuts import render
from django.views import generic
from .models import Student, StudentAddress, CareTaker, StudentGrade
from .forms import StudentForm, StudentAddressForm, CareTakerForm, StudentGradeForm
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from .models import Student
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


# Student List View with Pagination, Search, and Sorting
class StudentList(generic.ListView, LoginRequiredMixin):
    template_name = "students.html"
    context_object_name = "studentlist"
    paginate_by = 10 


    def get_queryset(self):
        queryset = Student.objects.all()
        print(queryset)
        return queryset

class RegisterStudentDetails(generic.CreateView, LoginRequiredMixin):
    model = Student
    template_name = "registerStudentDetails.html"
    form_class = StudentForm
    success_url = '/register/student-detail/registerStudentAdress' 


class RegisterStudentAddress(generic.CreateView, LoginRequiredMixin):
    model = StudentAddress
    template_name = "registerStudentAddress.html"
    form_class = StudentAddressForm
    success_url = '/' 


# Create view for adding a CareTaker
class CareTakerCreateView(generic.CreateView, LoginRequiredMixin):
    model = CareTaker
    form_class = CareTakerForm
    template_name = 'registerStudentCaretaker.html'
    success_url = reverse_lazy('caretaker_list')  # Redirect to the caretaker list page

# Update view for editing a CareTaker
class CareTakerUpdateView(generic.UpdateView, LoginRequiredMixin):
    model = CareTaker
    form_class = CareTakerForm
    template_name = 'caretaker_form.html'
    success_url = reverse_lazy('caretaker_list')  # Redirect to the caretaker list page

# List view to show all CareTakers
class CareTakerListView(generic.ListView, LoginRequiredMixin):
    model = CareTaker
    template_name = 'caretaker_list.html'
    context_object_name = 'caretakers'

# Create view for assigning class to a student
class StudentGradeCreateView(generic.CreateView, LoginRequiredMixin):
    model = StudentGrade
    form_class = StudentGradeForm
    template_name = 'registerStudentGrade.html'
    success_url = reverse_lazy('student_grade_list')  # Redirect to the student grade list page

# Update view for editing a student's class assignment
class StudentGradeUpdateView(generic.UpdateView, LoginRequiredMixin):
    model = StudentGrade
    form_class = StudentGradeForm
    template_name = 'student_grade_form.html'
    success_url = reverse_lazy('student_grade_list')  # Redirect to the student grade list page

# List view to show all student class assignments
class StudentGradeListView(generic.ListView, LoginRequiredMixin):
    model = StudentGrade
    template_name = 'student_grade_list.html'
    context_object_name = 'student_grades'


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
