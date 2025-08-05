from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Sum, Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import TopicsForm, QuestionForm
from .models import Topics, Question, ExamResult
from students.models import Student
from academic.models import Grade, Subject
from academic.models import TermExamSession


# -------------------------
# Helper Functions
# -------------------------

def get_grade_context(grade_id=None):
    return {
        'grades': Grade.objects.all(),
        'selected_grade': grade_id
    }


def handle_topic_form(request, form):
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Topic saved successfully!")
            return True
        except Exception as e:
            messages.error(request, f"Error saving topic: {str(e)}")
    return False


def handle_question_form(request, form):
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Question saved successfully!")
            return True
        except Exception as e:
            messages.error(request, f"Error saving question: {str(e)}")
    return False


# -------------------------
# Dashboard / Home View
# -------------------------
@login_required
@require_http_methods(["GET"])
def assessment_home(request):
    """Home dashboard for assessment system with comprehensive statistics"""
    context = get_grade_context()
    
    grades = Grade.objects.all().order_by('grade_name')
    subjects = Subject.objects.all().order_by('name')
    topics = Topics.objects.select_related('subject', 'grade')
    questions = Question.objects.select_related('term_exam', 'topic', 'grade', 'subject')
    results = ExamResult.objects.select_related('student', 'question', 'grade', 'subject', 'topic')
    
    context.update({
        'total_grades': grades.count(),
        'total_subjects': subjects.count(),
        'total_topics': topics.count(),
        'total_questions': questions.count(),
        'total_results': results.count(),
        'performance_data_exists': results.exists(),
    })
    
    if results.exists():
        overall_stats = results.aggregate(
            avg_score=Avg('score'),
            total_possible=Sum('question__max_score'),
            total_achieved=Sum('score'),
        )
        
        total_possible = overall_stats['total_possible'] or 0
        total_achieved = overall_stats['total_achieved'] or 0
        overall_stats['percentage'] = round((total_achieved / total_possible * 100), 2) if total_possible else 0
        circumference = 283
        overall_stats['dashoffset'] = circumference - (circumference * overall_stats['percentage'] / 100)

        context['overall_stats'] = overall_stats
        
        # Grade-level statistics
        context['grade_stats'] = grades.annotate(
            total_students=Count('student', distinct=True),
            total_questions=Count('grade_questions', distinct=True),
            avg_score=Avg('grade_exam_result__score'),
        )

        # Subject-level statistics
        context['subject_stats'] = subjects.annotate(
            total_topics=Count('assessment_topics', distinct=True),
            total_questions=Count('subject_question', distinct=True),
            avg_score=Avg('subject_xamrsults__score'),
        )

        context['recent_results'] = results.order_by('-id')[:5]

        context['chart_data'] = {
            'grade_labels': [g.grade_name for g in grades],
            'grade_avg_scores': [
                results.filter(grade=g).aggregate(avg=Avg('score'))['avg'] or 0 
                for g in grades
            ],
            'subject_labels': [s.name for s in subjects][:10],
            'subject_avg_scores': [
                results.filter(subject=s).aggregate(avg=Avg('score'))['avg'] or 0 
                for s in subjects
            ][:10],
        }

    return render(request, "assess.html", context)


# -------------------------
# Topic Views
# -------------------------

@require_http_methods(["GET"])
def topic_lists(request):
    grade_id = request.GET.get('grade_id')
    topics = Topics.objects.all()
    if grade_id:
        topics = topics.filter(grade_id=grade_id).select_related('subject', 'grade')
    
    context = get_grade_context(grade_id)
    context['topics'] = topics
    return render(request, "all_topics.html", context)


@require_http_methods(["GET", "POST"])
def record_topic(request):
    if request.method == 'POST':
        form = TopicsForm(request.POST)
        if handle_topic_form(request, form):
            return redirect('assessment:topic_list')
    else:
        form = TopicsForm()
    
    context = get_grade_context()
    context['form'] = form
    return render(request, "record_topic.html", context)


@require_http_methods(["GET"])
def get_topics(request):
    grade_id = request.GET.get('grade_id')
    subject_id = request.GET.get('subject_id')
    
    if grade_id and subject_id:
        topics = Topics.objects.filter(grade_id=grade_id, subject_id=subject_id)
    else:
        topics = Topics.objects.none()
        
    data = [{'id': topic.id, 'name': topic.name} for topic in topics]
    return JsonResponse(data, safe=False)


# -------------------------
# Question Views
# -------------------------

@require_http_methods(["GET", "POST"])
def record_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if handle_question_form(request, form):
            return redirect('assessment:question_list')
    else:
        form = QuestionForm()
    
    grade_id = request.GET.get('grade_id')
    subject_id = request.GET.get('subject_id')
    
    questions = Question.objects.select_related(
        'term_exam', 'grade', 'subject', 'topic'
    ).order_by('-id')[:15]
    
    if grade_id:
        questions = questions.filter(grade_id=grade_id)
    if subject_id:
        questions = questions.filter(subject_id=subject_id)
    
    context = {
        'form': form,
        'questions': questions,
        'grades': Grade.objects.all(),
        'subjects': Subject.objects.all(),
        'selected_grade': grade_id,
        'selected_subject': subject_id,
    }
    
    return render(request, "record_question.html", context)


@require_http_methods(["GET"])
def get_topics_by_subject(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID required'}, status=400)
    
    try:
        topics = Topics.objects.filter(subject_id=subject_id).values('id', 'name')
        return JsonResponse(list(topics), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# -------------------------
# Results Views
# -------------------------

def prepare_results_data(grade_id, subject_id):
    if not (grade_id and subject_id):
        return None

    questions = Question.objects.filter(
        subject_id=subject_id
    ).select_related('topic').order_by('topic__name', 'question_number')
    
    students = Student.objects.filter(
        current_grade_id=grade_id
    ).prefetch_related(
        Prefetch(
            'examresult_set',
            queryset=ExamResult.objects.filter(
                grade_id=grade_id,
                subject_id=subject_id,
                question__in=questions
            ).select_related('question', 'question__topic'),
            to_attr='filtered_results'
        )
    )
    
    if not questions.exists() or not students.exists():
        return None
    
    results_data = {
        'questions': questions,
        'students': students,
        'results_matrix': defaultdict(dict),
        'student_totals': defaultdict(lambda: {'total_score': 0, 'total_possible': 0}),
        'topic_data': defaultdict(lambda: {
            'total_score': 0, 
            'max_score': 0, 
            'count': 0,
            'students': []
        })
    }

    for student in students:
        for result in student.filtered_results:
            question = result.question
            percentage = (result.score / question.max_score * 100) if question.max_score else 0
            results_data['results_matrix'][student.id][question.id] = {
                'score': result.score,
                'percentage': percentage
            }
            results_data['student_totals'][student.id]['total_score'] += result.score
            results_data['student_totals'][student.id]['total_possible'] += question.max_score
            topic_data = results_data['topic_data'][question.topic.name]
            topic_data['total_score'] += result.score
            topic_data['max_score'] += question.max_score
            topic_data['count'] += 1
            topic_data['students'].append({
                'student': student,
                'score': result.score,
                'percentage': percentage,
            })
    
    return results_data


def analyze_topic_performance(topic_data):
    topic_performance = []
    topic_student_analysis = {}

    for topic_name, data in topic_data.items():
        percentage = (data['total_score'] / data['max_score'] * 100) if data['max_score'] else 0
        topic_performance.append({'topic': topic_name, 'percentage': percentage})
        sorted_students = sorted(data['students'], key=lambda x: x['percentage'], reverse=True)
        topic_student_analysis[topic_name] = {
            'top': sorted_students[:3],
            'bottom': sorted_students[-3:]
        }

    topic_performance_sorted = sorted(topic_performance, key=lambda x: x['percentage'], reverse=True)

    return {
        'best_topics': topic_performance_sorted[:2],
        'worst_topics': topic_performance_sorted[-2:],
        'topic_student_analysis': topic_student_analysis
    }


@require_http_methods(["GET"])
def exam_results(request):
    grade_id = request.GET.get('grade_id')
    subject_id = request.GET.get('subject_id')
    term_exam_id = request.GET.get('term_exam_id')
    
    # Get all available filters for the template
    grades = Grade.objects.all().order_by('grade_name')
    subjects = Subject.objects.all().order_by('name')
    term_exams = TermExamSession.objects.all().order_by('-year', 'term_name')
    
    context = {
        'grades': grades,
        'subjects': subjects,
        'term_exams': term_exams,
        'selected_grade': grade_id,
        'selected_subject': subject_id,
        'selected_term_exam': term_exam_id,
    }
    
    # Only proceed with analysis if we have both grade and subject selected
    if grade_id and subject_id:
        # Prepare base queryset with filters
        results_queryset = ExamResult.objects.filter(
            grade_id=grade_id,
            subject_id=subject_id
        ).select_related(
            'student', 'question', 'question__topic'
        )
        
        # Apply term exam filter if selected
        if term_exam_id:
            results_queryset = results_queryset.filter(question__term_exam_id=term_exam_id)
        
        # Check if we have any results
        if not results_queryset.exists():
            messages.info(request, "No results found for the selected criteria.")
            return render(request, 'results.html', context)
        
        # Get all questions for the selected criteria
        questions = Question.objects.filter(
            grade_id=grade_id,
            subject_id=subject_id
        )
        if term_exam_id:
            questions = questions.filter(term_exam_id=term_exam_id)
        
        questions = questions.select_related('topic').order_by('topic__name', 'question_number')
        
        # Get all students in the grade
        students = Student.objects.filter(
            current_grade_id=grade_id
        ).order_by('first_name', 'last_name')
        
        # Prepare data structures for the template
        results_matrix = defaultdict(dict)
        student_totals = defaultdict(lambda: {'total_score': 0, 'total_possible': 0})
        topic_data = defaultdict(lambda: {
            'total_score': 0, 
            'max_score': 0, 
            'count': 0,
            'students': []
        })
        
        # Populate the data structures
        for student in students:
            student_results = results_queryset.filter(student=student)
            
            for result in student_results:
                question = result.question
                percentage = (result.score / question.max_score * 100) if question.max_score else 0
                
                # Add to results matrix
                results_matrix[student.id][question.id] = {
                    'score': result.score,
                    'percentage': percentage,
                    'result_id': result.id
                }
                
                # Update student totals
                student_totals[student.id]['total_score'] += result.score
                student_totals[student.id]['total_possible'] += question.max_score
                
                # Update topic data
                topic = question.topic
                topic_data[topic.name]['total_score'] += result.score
                topic_data[topic.name]['max_score'] += question.max_score
                topic_data[topic.name]['count'] += 1
                topic_data[topic.name]['students'].append({
                    'student': student,
                    'score': result.score,
                    'percentage': percentage,
                    'question': question
                })
        
        # Calculate percentages for student totals
        for student_id, totals in student_totals.items():
            if totals['total_possible'] > 0:
                totals['percentage'] = (totals['total_score'] / totals['total_possible']) * 100
            else:
                totals['percentage'] = 0
        
        # Sort students by percentage (high to low)
        sorted_students = sorted(
            students,
            key=lambda s: -student_totals[s.id]['percentage']
        )
        
        # Analyze topic performance
        topic_analysis = analyze_topic_performance(topic_data)
        
        # Update context with all the prepared data
        context.update({
            'questions': questions,
            'students': sorted_students,
            'results_matrix': results_matrix,
            'student_totals': student_totals,
            'topic_data': topic_data,
            'best_topics': topic_analysis['best_topics'],
            'worst_topics': topic_analysis['worst_topics'],
            'topic_student_analysis': topic_analysis['topic_student_analysis'],
            'class_average': sum(
                student_totals[s.id]['percentage'] for s in sorted_students
            ) / len(sorted_students) if sorted_students else 0,
            'has_data': True
        })
    
    return render(request, 'results.html', context)