from django.shortcuts import render
from .models import ExamResult
from .forms import ExamResultForm
from .models import ExamResult, Student, Topics, Question, Grade
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import *
from academic.models import Grade
from .forms import *
# Create your views here.


def Assessment(request):
    grading = Grade.objects.all()
    return render(request, "assess.html",{"grading":grading})


# RECORD TOPIC

def get_Tsubjects_by_grade(request):
    grade_id = request.GET.get('grade_id')
    subjects = Subject.objects.filter(grade_id=grade_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)

def RecordTopic(request):
    if request.method == 'POST':
        form = TopicsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_topics')
    else:
        form = TopicsForm()
    return render(request, "all_topics.html", {'form':form})


def topic_lists(request):
    grades = Grade.objects.all()
    selected_grade = request.GET.get('grade_id')

    topics = Topics.objects.all()
    if selected_grade:
        topics = topics.filter(grade_id=selected_grade)

    return render(request, "all_topics.html", {
        'grades': grades,
        'topics': topics,
        'selected_grade': selected_grade
    })

# RECORD QUESTIONS


def get_Qsubjects_by_grade(request):
    grade_id = request.GET.get('grade_id')
    subjects = Subject.objects.filter(grade_id=grade_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)


def get_Qtopics_by_subject(request):
    subject_id = request.GET.get('subject_id')
    topics = Topics.objects.filter(subject_id=subject_id).values('id', 'name')
    return JsonResponse(list(topics), safe=False)

def RecordQuestion(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assess')
    else:
        form = QuestionForm()
    return render(request, "record_question.html", {'form': form})

#RECORD RESULT
def get_subjects_by_grade(request):
    grade_id = request.GET.get('grade_id')
    subjects = Subject.objects.filter(grade_id=grade_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)


def get_topics_by_subject(request):
    subject_id = request.GET.get('subject_id')
    topics = Topics.objects.filter(subject_id=subject_id).values('id', 'name')
    return JsonResponse(list(topics), safe=False)


def get_students_by_grade(request):
    grade_id = request.GET.get('grade_id')
    students = Student.objects.filter(current_grade_id=grade_id).values(
        'id', 'first_name', 'last_name')
    return JsonResponse(list(students), safe=False)


# def get_topics_by_grade(request):
#     grade_id = request.GET.get('grade_id')
#     topics = Topics.objects.filter(grade_id=grade_id).values('id', 'name')
#     return JsonResponse(list(topics), safe=False)


def get_questions_by_topic(request):
    topic_id = request.GET.get('topic_id')
    questions = Question.objects.filter(
        topic_id=topic_id).values('id', 'question_number')
    return JsonResponse(list(questions), safe=False)


def record_result(request):
    if request.method == "POST":
        form = ExamResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('results')
    else:
        form = ExamResultForm()
    return render(request, 'record_result.html', {'form': form})


def Exam_Results(request):
    grades = Grade.objects.all()
    selected_grade = request.GET.get('grade_id')

    if selected_grade:
        results = ExamResult.objects.filter(grade_id=selected_grade)
    else:
        results = ExamResult.objects.none()  # Show nothing initially

    return render(request, 'results.html', {'grades': grades, 'results': results, 'selected_grade': selected_grade})


