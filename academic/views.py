from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Grade, Subject, Curriculum, Topic, Exam
from .forms import GradeForm, SubjectForm, CurriculumForm, TopicForm, ExamForm

# Create your views here.
def academics(requests):
    exams = Exam.objects.all().order_by('subject')
    grades_count = Grade.objects.all().count()
    subjects_count = Subject.objects.all().count()
    exams_count = Exam.objects.all().count()
    curriculum_count = Curriculum.objects.all().count()
    topics_count = Topic.objects.all().count()

    context = {
        'exams': exams,
        'grades_count':grades_count,
        'subjects_count':subjects_count,
        'exams_count':exams_count,
        'curriculum_count':curriculum_count,
        'topics_count':topics_count,
        }
    return render(requests, "academics.html", context)

# Exams
# View details of a specific exam
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, 'exam_detail.html', {'exam': exam})

# Add a new exam
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('exam_list'))
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form})

# Edit an exam
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
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return HttpResponseRedirect(reverse('exam_list'))
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})

def grades(requests):
    grades_list = Grade.objects.all()
    return render(requests, "grades.html", {"grades_list": grades_list})

def subjects(requests):
    subject_list = Subject.objects.all()
    return render(requests, "subjects.html", {"subject_list":subject_list})

class RegisterGrade(generic.CreateView):
    model = Grade
    template_name = "registerGrade.html"
    form_class = GradeForm
    success_url = "/"

class RegisterSubject(generic.CreateView):
    model = Subject
    template_name = "registerSubject.html"
    form_class = SubjectForm
    success_url = "/"

class RegisterCurriculum(generic.CreateView):
    model = Curriculum
    template_name = "registerCurriculum.html"
    form_class = CurriculumForm
    success_url = '/'

class RegisterTopic(generic.CreateView):
    model = Topic
    template_name = "registerTopic.html"
    form_class = TopicForm
    success_url = '/'

class RegisterExam(generic.CreateView):
    model = Exam
    template_name = "registerExam.html"
    form_class = ExamForm
    success_url = '/'