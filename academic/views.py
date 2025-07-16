import csv
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.views import generic
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from .models import (
    Grade, Subject, Curriculum, Topic, Exam, Notes,
    TermExamSession, StudentMarkSummary
)
from .forms import (
    GradeForm, SubjectForm, CurriculumForm, TopicForm, ExamForm, NotesForm
)
from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required
from assessment.models import ExamResult
from students.models import Student


@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
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
class ExamList(ListView, RoleRequiredMixin):
    model = Exam
    template_name = "exams.html"
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

    
# View details of a specific exam
@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, 'exam_detail.html', {'exam': exam})


# Edit an exam
@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
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
@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return HttpResponseRedirect(reverse('exam_list'))
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})

@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def grades(requests):
    grades_list = Grade.objects.all()
    return render(requests, "grades.html", {"grades_list": grades_list})

@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def subjects(requests):
    subject_list = Subject.objects.all()
    return render(requests, "subjects.html", {"subject_list":subject_list})


class RegisterGrade(generic.CreateView, RoleRequiredMixin):
    model = Grade
    template_name = "registerGrade.html"
    form_class = GradeForm
    success_url = "/"
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

class RegisterSubject(generic.CreateView, RoleRequiredMixin):
    model = Subject
    template_name = "registerSubject.html"
    form_class = SubjectForm
    success_url = "/"
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

class RegisterCurriculum(generic.CreateView, RoleRequiredMixin):
    model = Curriculum
    template_name = "registerCurriculum.html"
    form_class = CurriculumForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

class RegisterTopic(generic.CreateView, RoleRequiredMixin):
    model = Topic
    template_name = "registerTopic.html"
    form_class = TopicForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

class UploadExamView(generic.CreateView, RoleRequiredMixin):
    model = Exam
    template_name = "uploadExam.html"
    form_class = ExamForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

    def form_valid(self, form):
        form.instance.created_by = self.request.user.teacher
        return super().form_valid(form)

class UploadNotesView(generic.CreateView, RoleRequiredMixin):
    model = Notes
    form_class = NotesForm
    template_name = 'uploadNotes.html'
    success_url = "/"
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

    def form_valid(self, form):
        form.instance.created_by = self.request.user 
        return super().form_valid(form)

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Max, Min, Count
from .models import StudentMarkSummary, TermExamSession, Grade, Subject
from students.models import Student
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from django.http import HttpResponse


@login_required
def mark_summary_report(request):
    # Get filter parameters from request
    term_exam_id = request.GET.get('term_exam')
    grade_id = request.GET.get('grade')
    subject_id = request.GET.get('subject')
    
    # Get all active term exams for filter dropdown
    term_exams = TermExamSession.objects.all().order_by('-year', 'term_name')
    
    # Base queryset
    summaries = StudentMarkSummary.objects.select_related(
        'student', 'term_exam', 'grade', 'subject'
    ).order_by('student__last_name', 'student__first_name')
    
    # Apply filters if provided
    if term_exam_id:
        summaries = summaries.filter(term_exam_id=term_exam_id)
    if grade_id:
        summaries = summaries.filter(grade_id=grade_id)
    if subject_id:
        summaries = summaries.filter(subject_id=subject_id)
    
    # Calculate aggregates for the filtered results
    aggregates = summaries.aggregate(
        avg_percentage=Avg('percentage'),
        max_percentage=Max('percentage'),
        min_percentage=Min('percentage'),
        total_students=Count('student', distinct=True)
    )
    
    context = {
        'summaries': summaries,
        'term_exams': term_exams,
        'grades': Grade.objects.all(),
        'subjects': Subject.objects.all(),
        'selected_term_exam': int(term_exam_id) if term_exam_id else None,
        'selected_grade': int(grade_id) if grade_id else None,
        'selected_subject': int(subject_id) if subject_id else None,
        'aggregates': aggregates,
    }
    
    return render(request, 'reports/mark_summary_report.html', context)


@login_required
def export_mark_summary_csv(request):
    # Get filter parameters from request
    term_exam_id = request.GET.get('term_exam')
    grade_id = request.GET.get('grade')
    subject_id = request.GET.get('subject')
    
    # Create response with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_mark_summary.csv"'
    
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Student ID', 'Student Name', 'Grade', 'Term Exam', 
        'Subject', 'Total Score', 'Max Possible', 'Percentage',
        'Subject Position', 'Class Average'
    ])
    
    # Base queryset
    summaries = StudentMarkSummary.objects.select_related(
        'student', 'term_exam', 'grade', 'subject'
    ).order_by('student__last_name', 'student__first_name')
    
    # Apply filters if provided
    if term_exam_id:
        summaries = summaries.filter(term_exam_id=term_exam_id)
    if grade_id:
        summaries = summaries.filter(grade_id=grade_id)
    if subject_id:
        summaries = summaries.filter(subject_id=subject_id)
    
    # Write data rows
    for summary in summaries:
        writer.writerow([
            summary.student.student_id,
            f"{summary.student.last_name}, {summary.student.first_name}",
            summary.grade.grade_name,
            str(summary.term_exam),
            summary.subject.name,
            summary.total_score,
            summary.max_possible,
            f"{summary.percentage}%",
            summary.subject_position or '',
            summary.class_average or ''
        ])
    
    return response


class StudentMarkSummaryDetailView(LoginRequiredMixin, DetailView):
    model = StudentMarkSummary
    template_name = 'reports/mark_summary_detail.html'
    context_object_name = 'summary'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = self.object
        
        # Get exam results with calculated percentages
        exam_results = ExamResult.objects.filter(
            student=summary.student,
            question__term_exam=summary.term_exam,
            subject=summary.subject
        ).select_related('question', 'topic')
        
        # Calculate percentage for each result
        for result in exam_results:
            result.percentage = (result.score / result.question.max_score) * 100 if result.question.max_score > 0 else 0
            result.percentage_rounded = round(result.percentage, 1)
        
        context['exam_results'] = exam_results
        
        # Calculate topic performance for charts
        topic_performance = {}
        for result in exam_results:
            topic_name = result.topic.name
            if topic_name not in topic_performance:
                topic_performance[topic_name] = {
                    'total': result.percentage,
                    'count': 1
                }
            else:
                topic_performance[topic_name]['total'] += result.percentage
                topic_performance[topic_name]['count'] += 1
        
        # Prepare data for charts
        context['topic_labels'] = list(topic_performance.keys())
        context['topic_averages'] = [
            round(topic['total'] / topic['count']) 
            for topic in topic_performance.values()
        ]
        
        # Score distribution data
        context['score_distribution'] = {
            'correct': summary.total_score,
            'incorrect': summary.max_possible - summary.total_score,
            'unattempted': 0  # Assuming all questions were attempted
        }
        
        # Performance comparison
        if summary.class_average:
            context['performance_comparison'] = round(summary.percentage - summary.class_average, 1)
        
        return context


class StudentProgressReportView(LoginRequiredMixin, ListView):
    template_name = 'reports/student_progress_report.html'
    context_object_name = 'summaries'
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        self.student = get_object_or_404(Student, pk=student_id)
        
        return StudentMarkSummary.objects.filter(
            student=self.student
        ).select_related('term_exam', 'grade', 'subject').order_by('term_exam__year', 'term_exam__term_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        
        # Calculate overall performance statistics
        summaries = context['summaries']
        if summaries:
            context['subjects'] = set(s.subject for s in summaries)
            context['terms'] = set(s.term_exam for s in summaries)
            
            # Calculate average percentage per term
            term_performance = {}
            for term in context['terms']:
                term_summaries = [s for s in summaries if s.term_exam == term]
                avg = sum(s.percentage for s in term_summaries) / len(term_summaries)
                term_performance[term] = round(avg, 2)
            
            context['term_performance'] = term_performance
            
            # Calculate performance by subject
            subject_performance = {}
            for subject in context['subjects']:
                subject_summaries = [s for s in summaries if s.subject == subject]
                percentages = [s.percentage for s in subject_summaries]
                if percentages:
                    subject_performance[subject] = {
                        'average': round(sum(percentages) / len(percentages), 2),
                        'trend': 'up' if len(percentages) > 1 and percentages[-1] > percentages[0] else 'down'
                    }
            
            context['subject_performance'] = subject_performance
        
        return context



class TermExamListView(LoginRequiredMixin, ListView):
    model = TermExamSession
    template_name = 'reports/term_exam_list.html'
    context_object_name = 'term_exams'
    paginate_by = 10
    ordering = ['-year', 'term_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by year if provided
        year = self.request.GET.get('year')
        if year and year.isdigit():
            queryset = queryset.filter(year=int(year))
            
        # Filter by term if provided
        term = self.request.GET.get('term')
        if term in dict(TermExamSession.TermChoices.choices):
            queryset = queryset.filter(term_name=term)
            
        return queryset.select_related('created_by').prefetch_related('mark_summaries')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'assessment'
        
        # Generate year choices for filter dropdown (last 5 years and next year)
        current_year = timezone.now().year
        context['year_choices'] = range(current_year - 5, current_year + 2)
        
        # Get filter values to maintain form state
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_term'] = self.request.GET.get('term', '')
        
        # Calculate pagination values
        page_obj = context['page_obj']
        context['total_results'] = page_obj.paginator.count
        context['showing_start'] = page_obj.start_index()
        context['showing_end'] = page_obj.end_index()
        
        # Add term choices for filter
        context['term_choices'] = TermExamSession.TermChoices.choices
        
        return context


class TermExamDetailView(LoginRequiredMixin, DetailView):
    model = TermExamSession
    template_name = 'reports/term_exam_detail.html'
    context_object_name = 'term_exam'
    
    def get_queryset(self):
        return super().get_queryset().select_related('created_by').prefetch_related(
            'mark_summaries__student',
            'mark_summaries__subject',
            'mark_summaries__grade'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'assessment'
        
        # Get aggregated data for performance metrics
        summaries = self.object.mark_summaries.all()
        
        # Calculate overall statistics
        if summaries.exists():
            # Get top performing student
            top_student = summaries.order_by('-percentage').first()
            context['top_student'] = {
                'name': top_student.student.get_full_name(),
                'grade': top_student.grade.grade_name,
                'score': top_student.percentage,
                'subject': top_student.subject.name
            }
            
            # Calculate class averages
            context['class_averages'] = {
                'overall': summaries.aggregate(avg=Avg('percentage'))['avg'],
                'by_subject': summaries.values('subject__name').annotate(
                    avg_score=Avg('percentage'),
                    max_score=Max('percentage')
                ).order_by('-avg_score')
            }
            
            # Count of unique subjects and students
            context['stats'] = {
                'subject_count': summaries.values('subject').distinct().count(),
                'student_count': summaries.values('student').distinct().count(),
                'grade_count': summaries.values('grade').distinct().count()
            }
            
            # Performance distribution data for charts
            context['performance_distribution'] = self.get_performance_distribution(summaries)
            
        return context
    
    def get_performance_distribution(self, summaries):
        """Generate data for performance distribution charts"""
        distribution = {
            'ranges': ['90-100%', '80-89%', '70-79%', '60-69%', '50-59%', 'Below 50%'],
            'counts': [0, 0, 0, 0, 0, 0]
        }
        
        for summary in summaries:
            percentage = summary.percentage
            if percentage >= 90:
                distribution['counts'][0] += 1
            elif percentage >= 80:
                distribution['counts'][1] += 1
            elif percentage >= 70:
                distribution['counts'][2] += 1
            elif percentage >= 60:
                distribution['counts'][3] += 1
            elif percentage >= 50:
                distribution['counts'][4] += 1
            else:
                distribution['counts'][5] += 1
                
        return distribution


@login_required
def student_term_report(request, student_id):
    marks = StudentMarkSummary.objects.filter(student_id=student_id) \
        .select_related('term_exam', 'subject', 'grade') \
        .order_by('term_exam__year', 'term_exam__term_name')
    
    terms = {}
    for mark in marks:
        term_key = f"{mark.term_exam.get_term_name_display()} {mark.term_exam.year}"
        if term_key not in terms:
            terms[term_key] = {
                'term_obj': mark.term_exam,
                'marks': [],
                'total_percentage': 0,
                'subject_count': 0
            }
        terms[term_key]['marks'].append(mark)
        terms[term_key]['total_percentage'] += mark.percentage
        terms[term_key]['subject_count'] += 1
    
    # Calculate average for each term
    for term_data in terms.values():
        if term_data['subject_count'] > 0:
            term_data['average_percentage'] = term_data['total_percentage'] / term_data['subject_count']
        else:
            term_data['average_percentage'] = 0
    
    return render(request, 'reports/student_term_report.html', {
        'terms': terms,
        'student': marks[0].student if marks else None 
    })