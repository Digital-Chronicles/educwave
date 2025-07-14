
from django.db.models import Avg
from django.db.models import Sum
from collections import defaultdict
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import *
from .forms import *
from academic.models import *
from students.models import *
# Create your views here.


def Assessment(request):
    grading = Grade.objects.all()
    return render(request, "assess.html", {"grading": grading})


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
    return render(request, "all_topics.html", {'form': form})


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


#RESULTS


def Exam_Results(request):
    grades = Grade.objects.all()
    selected_grade_id = request.GET.get('grade_id')
    selected_subject_id = request.GET.get('subject_id')

    subjects = Subject.objects.filter(
        grade_id=selected_grade_id) if selected_grade_id else []
    students = []
    questions = []
    results_matrix = {}
    student_totals = {}
    topic_scores = defaultdict(
        lambda: {'total_score': 0, 'max_score': 0, 'count': 0})
    topic_students = defaultdict(list)

    if selected_grade_id and selected_subject_id:
        students = Student.objects.filter(current_grade_id=selected_grade_id)
        questions = Question.objects.filter(subject_id=selected_subject_id).select_related(
            'topic').order_by('topic__name', 'question_number')

        results = ExamResult.objects.filter(
            grade_id=selected_grade_id,
            subject_id=selected_subject_id,
            question__in=questions
        ).select_related('student', 'question', 'question__topic')

        # Initialize results matrix and totals
        for student in students:
            results_matrix[student.id] = {}
            student_totals[student.id] = {
                'total_score': 0, 'total_possible': 0}

            for question in questions:
                results_matrix[student.id][question.id] = None
                student_totals[student.id]['total_possible'] += question.max_score

        for result in results:
            percentage = (result.score / result.question.max_score) * \
                100 if result.question.max_score else 0
            results_matrix[result.student.id][result.question.id] = {
                'score': result.score,
                'percentage': percentage
            }

            student_totals[result.student.id]['total_score'] += result.score

            topic = result.question.topic.name
            topic_scores[topic]['total_score'] += result.score
            topic_scores[topic]['max_score'] += result.question.max_score
            topic_scores[topic]['count'] += 1

            # Add student performance for each topic
            topic_students[topic].append({
                'student': result.student,
                'score': result.score,
                'percentage': percentage,
            })

        # Select top 3 and bottom 3 students per topic
        topic_top_bottom_students = {}
        for topic, students_data in topic_students.items():
            # Sort students based on their percentage for each topic
            sorted_students = sorted(
                students_data, key=lambda x: x['percentage'], reverse=True)

            top_students = sorted_students[:3]  # Top 3
            bottom_students = sorted_students[-3:]  # Bottom 3

            topic_top_bottom_students[topic] = {
                'top': top_students,
                'bottom': bottom_students
            }

        # Compute topic performance percentages
        topic_performance = []
        for topic, data in topic_scores.items():
            percentage = (data['total_score'] / data['max_score']
                          ) * 100 if data['max_score'] else 0
            topic_performance.append(
                {'topic': topic, 'percentage': percentage})

        # Sort topics by performance
        topic_performance_sorted = sorted(
            topic_performance, key=lambda x: x['percentage'], reverse=True)
        best_done_topics = topic_performance_sorted[:2]
        worst_done_topics = topic_performance_sorted[-2:]

    else:
        best_done_topics = []
        worst_done_topics = []
        student_totals = {}
        topic_top_bottom_students = {}

    return render(request, 'results.html', {
        'grades': grades,
        'subjects': subjects,
        'questions': questions,
        'students': students,
        'results_matrix': results_matrix,
        'student_totals': student_totals,
        'selected_grade': selected_grade_id,
        'selected_subject': selected_subject_id,
        'best_done_topics': best_done_topics,
        'worst_done_topics': worst_done_topics,
        'topic_top_bottom_students': topic_top_bottom_students,  # Add this to pass the data
    })


# BULK RECORDS
def bget_subjects_by_grade(request):
    grade_id = request.GET.get('grade_id')
    subjects = Subject.objects.filter(grade_id=grade_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)


def bulk_exam_entry(request):
    if request.method == "POST":
        grade_id = request.POST.get('grade')
        subject_id = request.POST.get('subject')
        exam_id = request.POST.get('exam')

        if not grade_id or not subject_id or not exam_id:
            messages.error(request, "All selections are required.")
            return redirect('bulk-items')  # Replace with your URL name

        try:
            grade = Grade.objects.get(id=grade_id)
            subject = Subject.objects.get(id=subject_id)
            exam = TermExamSession.objects.get(id=exam_id)
        except (Grade.DoesNotExist, Subject.DoesNotExist, TermExamSession.DoesNotExist):
            messages.error(request, "Invalid grade, subject, or exam.")
            return redirect('bulk-items')

        students = Student.objects.filter(current_grade=grade)
        questions = Question.objects.filter(subject=subject, term_exam=exam)

        if 'save' in request.POST:  # Check if the save button was pressed
            for student in students:
                for question in questions:
                    # Get the score from the form data using the student and question IDs
                    score_key = f'student_{student.id}_question_{question.id}'
                    score = request.POST.get(score_key)

                    if score:  # If there's a score entered, save it
                        try:
                            score = int(score)
                            # Create an ExamResult entry
                            exam_result = ExamResult(
                                student=student,
                                grade=grade,
                                subject=subject,
                                question=question,
                                topic=question.topic,  # Assuming Topic is a field in Question
                                score=score,
                            )
                            exam_result.save()
                        except ValueError:
                            messages.error(
                                request, f"Invalid score for {student.first_name} {student.last_name} on question {question.question_number}")
                            return redirect('bulk-items')
                        except ValidationError as e:
                            messages.error(
                                request, f"Validation error for {student.first_name} {student.last_name}: {e.message}")
                            return redirect('bulk-items')

            messages.success(request, "Scores saved successfully!")
            return redirect('bulk-items')  # Redirect after saving

        context = {
            'grade': grade,
            'subject': subject,
            'exam': exam,
            'students': students,
            'questions': questions,
        }

        return render(request, 'bulk_entry_table.html', context)

    # GET request (render the selection form)
    grades = Grade.objects.all()
    exams = TermExamSession.objects.all()
    return render(request, 'bulk_entry_select.html', {
        'grades': grades,
        'exams': exams
    })
