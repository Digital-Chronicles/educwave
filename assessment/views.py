from django.shortcuts import redirect, render
from .models import *
from academic.models import Grade
from .forms import *
# Create your views here.


def Assessment(request):
    grading = Grade.objects.all()
    return render(request, "assess.html",{"grading":grading})


# RECORD TOPIC
def RecordTopic(request):
    if request.method == 'POST':
        form = TopicsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assess')
    else:
        form = TopicsForm()
    return render(request, "record_topic.html", {'form':form})

def TopicLists(request):
    lists = Topics.objects.all()
    return render(request, "all_topics.html",{'lists':lists})

# RECORD QUESTIONS


def RecordQuestion(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assess')
    else:
        form = QuestionForm()
    return render(request, "record_question.html", {'form': form})


# EXAM RESULTS
def record_result(request):
    if request.method == "POST":
        form = ExamResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assess')

    else:
        form = ExamResultForm()  
    return render(request, 'record_result.html', {'form': form})

def Exam_Results(request):
    results= ExamResult.objects.all()
    return render(request,'results.html', {'results':results})


