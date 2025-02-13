from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Grade, Subject, Curriculum, Topic, Exam, Notes, StudentMark
from .forms import GradeForm, SubjectForm, CurriculumForm, TopicForm, ExamForm, NotesForm, StudentMarksForm
from django.http import JsonResponse
from django.core.paginator import Paginator

@login_required
def academics(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Process AJAX request
        exams = list(Exam.objects.all().order_by('subject').values(
            'subject__name', 'date', 'duration_minutes', 'description', 'id', 'grade', 'created'
        ))
        
        data = {
            'grades_count': Grade.objects.all().count(),
            'subjects_count': Subject.objects.all().count(),
            'exams_count': Exam.objects.all().count(),
            'curriculum_count': Curriculum.objects.all().count(),
            'topics_count': Topic.objects.all().count(),
            'exams': exams,
        }
        return JsonResponse(data)

    # For non-AJAX requests, render the template with pagination
    exams = Exam.objects.all().order_by('subject')
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    grades_count = Grade.objects.all().count()
    subjects_count = Subject.objects.all().count()
    exams_count = Exam.objects.all().count()
    curriculum_count = Curriculum.objects.all().count()
    topics_count = Topic.objects.all().count()

    context = {
        'page_obj': page_obj,
        'grades_count': grades_count,
        'subjects_count': subjects_count,
        'exams_count': exams_count,
        'curriculum_count': curriculum_count,
        'topics_count': topics_count,
    }
    return render(request, "academics.html", context)

# Exams
class ExamList(ListView, LoginRequiredMixin):
    model = Exam
    template_name = "exams.html"

    
# View details of a specific exam
@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, 'exam_detail.html', {'exam': exam})


# Edit an exam
@login_required
def exam_update(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, request.FILES, instance=exam)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('exam_list'))
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/exam_form.html', {'form': form})

# Delete an exam
@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return HttpResponseRedirect(reverse('exam_list'))
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})

@login_required
def grades(requests):
    grades_list = Grade.objects.all()
    return render(requests, "grades.html", {"grades_list": grades_list})

@login_required
def subjects(requests):
    subject_list = Subject.objects.all()
    return render(requests, "subjects.html", {"subject_list":subject_list})


class RegisterGrade(generic.CreateView, LoginRequiredMixin):
    model = Grade
    template_name = "registerGrade.html"
    form_class = GradeForm
    success_url = "/"

class RegisterSubject(generic.CreateView, LoginRequiredMixin):
    model = Subject
    template_name = "registerSubject.html"
    form_class = SubjectForm
    success_url = "/"

class RegisterCurriculum(generic.CreateView, LoginRequiredMixin):
    model = Curriculum
    template_name = "registerCurriculum.html"
    form_class = CurriculumForm
    success_url = '/'

class RegisterTopic(generic.CreateView, LoginRequiredMixin):
    model = Topic
    template_name = "registerTopic.html"
    form_class = TopicForm
    success_url = '/'

class UploadExamView(generic.CreateView):
    model = Exam
    template_name = "uploadExam.html"
    form_class = ExamForm
    success_url = '/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user.teacher
        return super().form_valid(form)

class UploadNotesView(generic.CreateView, LoginRequiredMixin):
    model = Notes
    form_class = NotesForm
    template_name = 'uploadNotes.html'
    success_url = "/"

    def form_valid(self, form):
        form.instance.created_by = self.request.user 
        return super().form_valid(form)
    
class RegisterStudentMarksView(LoginRequiredMixin, generic.CreateView):
    model = StudentMark
    form_class = StudentMarksForm
    template_name = "registerStudentMarks.html"

    def form_valid(self, form):
        """Assign the logged-in teacher before saving."""
        form.instance.teacher = self.request.user.teacher  # Ensure `Teacher` is linked to `User`
        self.object = form.save()
        return JsonResponse({"message": "Marks recorded successfully!"}, status=200)

    def form_invalid(self, form):
        """Return JSON response for invalid form submission."""
        return JsonResponse(
            {"error": "Failed to save marks. Please check the form data."}, 
            status=400
        )