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
# from academic.utils import update_student_mark_summary
from management.models import GeneralInformation
from .models import (
    Grade, Subject, Curriculum, Exam, Notes,
    TermExamSession, StudentMarkSummary, ExamSession
)
from .forms import (
    GradeForm, SubjectForm, CurriculumForm, ExamForm, NotesForm
)
from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required
from assessment.models import ExamResult
from students.models import Student
from assessment.models import Topics

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction

from academic.models import ExamSession, TermExamSession, Subject, Grade,  StudentMarkSummary



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
            'topics_count': Topics.objects.all().count(),
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
    topics_count = Topics.objects.all().count()

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
    success_url = "/academics/subjects/"
    allowed_roles = ['TEACHER', 'ADMIN', 'FINANCE']

class RegisterCurriculum(generic.CreateView, RoleRequiredMixin):
    model = Curriculum
    template_name = "registerCurriculum.html"
    form_class = CurriculumForm
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
   
# @login_required
# def student_term_report(request, student_id):
#     # --- School Info ---
#     info = GeneralInformation.objects.first()
#     schoolname = info.school_name if info else ''
#     schoolbadge = info.school_badge if info else ''
#     schoolemail = info.email if info else ''
#     schoolcontact = info.contact_number if info else ''
#     schoolbox = info.box_no if info else ''
#     school_location = info.location if info else ''

#     # --- Student ---
#     student = get_object_or_404(Student, id=student_id)

#     # --- Fetch all exam results for this student ---
#     results = (
#         ExamResult.objects.filter(student=student)
#         .select_related('question', 'subject', 'grade', 'exam_session', 'exam_session__term')
#         .order_by('exam_session__term__year', 'exam_session__term__term_name', 'subject__name')
#     )

#     # --- Organize results by term and exam type ---
#     report_data = {}

#     for res in results:
#         if not res.exam_session or not res.subject:
#             continue

#         term = res.exam_session.term
#         exam_type = res.exam_session.exam_type  # BOT, MOT, EOT
#         subject = res.subject

#         term_key = f"{term.get_term_name_display()} {term.year}"

#         # Initialize term record if missing
#         if term_key not in report_data:
#             report_data[term_key] = {
#                 'BOT': {},
#                 'MOT': {},
#                 'EOT': {},
#                 'BOT_average': 0,
#                 'MOT_average': 0,
#                 'EOT_average': 0,
#             }

#         # Initialize subject in that exam type
#         if subject.name not in report_data[term_key][exam_type]:
#             report_data[term_key][exam_type][subject.name] = {
#                 'subject': subject.name,
#                 'total_score': 0,
#                 'max_possible': 0,
#                 'teacher_initials': getattr(subject.teacher, 'initials', '') if hasattr(subject, 'teacher') else ''
#             }

#         # --- Add up all question scores for that subject & exam type ---
#         entry = report_data[term_key][exam_type][subject.name]
#         entry['total_score'] += res.score
#         entry['max_possible'] += res.question.max_score if res.question else 0

#     # --- Convert subjects dicts into lists and calculate percentages ---
#     for term_key, data in report_data.items():
#         for ex_type in ['BOT', 'MOT', 'EOT']:
#             subjects_dict = data[ex_type]
#             subject_list = []
#             for sub, val in subjects_dict.items():
#                 max_possible = val['max_possible']
#                 percentage = (val['total_score'] / max_possible * 100) if max_possible else 0
#                 val['percentage'] = round(percentage, 2)
#                 val['auto_remark'] = (
#                     "Excellent work" if percentage >= 75 else
#                     "Fair — keep improving" if percentage >= 50 else
#                     "Needs serious effort"
#                 )
#                 subject_list.append(val)

#             # Replace dict with list for template use
#             data[ex_type] = subject_list

#             # --- Calculate average ---
#             if subject_list:
#                 avg = sum(s['percentage'] for s in subject_list) / len(subject_list)
#                 data[f"{ex_type}_average"] = round(avg, 2)

#     # --- Determine next term start date ---
#     all_exam_sessions = [res.exam_session for res in results if res.exam_session]
#     next_term_date = None
#     if all_exam_sessions:
#         last_exam = max(
#             all_exam_sessions,
#             key=lambda x: (x.term.year, ['TERM_1', 'TERM_2', 'TERM_3'].index(x.term.term_name))
#         )
#         term_order = ['TERM_1', 'TERM_2', 'TERM_3']
#         current_index = term_order.index(last_exam.term.term_name)
#         next_term_name = None
#         next_year = last_exam.term.year

#         if current_index + 1 < len(term_order):
#             next_term_name = term_order[current_index + 1]
#         else:
#             next_term_name = 'TERM_1'
#             next_year += 1

#         next_session = ExamSession.objects.filter(
#             term__year=next_year,
#             term__term_name=next_term_name,
#             exam_type='BOT'
#         ).first()

#         if next_session:
#             next_term_date = next_session.start_date

#     # --- Grading system ---
#     grading_system = [
#         {"grade": "A", "range": "80–100", "comment": "Excellent"},
#         {"grade": "B", "range": "70–79", "comment": "Very Good"},
#         {"grade": "C", "range": "60–69", "comment": "Good"},
#         {"grade": "D", "range": "50–59", "comment": "Fair"},
#         {"grade": "E", "range": "0–49", "comment": "Poor"},
#     ]

#     exam_types = ["BOT", "MOT", "EOT"]

#     return render(request, "reports/student_term_report.html", {
#         "report_data": report_data,
#         "next_term_date": next_term_date,
#         "exam_types": exam_types,
#         "schoolname": schoolname,
#         "schoolbadge": schoolbadge,
#         "schoolemail": schoolemail,
#         "schoolcontact": schoolcontact,
#         "schoolbox": schoolbox,
#         "school_location": school_location,
#         "student": student,
#         "grading_system": grading_system,
#         "class_teacher_remark": "Keep up the good discipline and focus.",
#         "head_teacher_remark": "Promoted to next class. Congratulations!",
#     })





@login_required
def student_term_report(request, student_id):
    # --- School Info ---
    info = GeneralInformation.objects.first()
    schoolname = info.school_name if info else ''
    schoolbadge = info.school_badge if info else ''
    schoolemail = info.email if info else ''
    schoolcontact = info.contact_number if info else ''
    schoolbox = info.box_no if info else ''
    school_location = info.location if info else ''

    # --- Student ---
    student = get_object_or_404(Student, id=student_id)

    # --- Fetch all exam results for this student ---
    results = (
        ExamResult.objects.filter(student=student)
        .select_related('question', 'subject', 'grade', 'exam_session', 'exam_session__term')
        .order_by('exam_session__term__year', 'exam_session__term__term_name', 'subject__name')
    )

    # --- Organize results by term and exam type ---
    report_data = {}

    for res in results:
        if not res.exam_session or not res.subject:
            continue

        term = res.exam_session.term
        exam_type = res.exam_session.exam_type  # BOT, MOT, EOT
        subject = res.subject

        term_key = f"{term.get_term_name_display()} {term.year}"

        # Initialize term record if missing
        if term_key not in report_data:
            report_data[term_key] = {
                'BOT': {},
                'MOT': {},
                'EOT': {},
                'BOT_average': 0,
                'MOT_average': 0,
                'EOT_average': 0,
                'BOT_aggregate': 0,
                'MOT_aggregate': 0,
                'EOT_aggregate': 0,
                'BOT_division': '',
                'MOT_division': '',
                'EOT_division': '',
            }

        # Initialize subject in that exam type
        if subject.name not in report_data[term_key][exam_type]:
            report_data[term_key][exam_type][subject.name] = {
                'subject': subject.name,
                'total_score': 0,
                'max_possible': 0,
                'percentage': 0,
                'points': 0,
                'teacher_initials': getattr(subject.teacher, 'initials', '') if hasattr(subject, 'teacher') else ''
            }

        # --- Handle both subject totals and individual questions ---
        entry = report_data[term_key][exam_type][subject.name]
        
        # If this is a SUBJECT TOTAL, use it directly
        if res.is_subject_total:
            entry['total_score'] = res.total_score or res.score
            entry['max_possible'] = res.max_possible or 100
            entry['percentage'] = res.percentage or ((res.total_score or res.score) / (res.max_possible or 100) * 100)
        
        # If this is an INDIVIDUAL QUESTION, accumulate scores
        else:
            entry['total_score'] += res.score
            entry['max_possible'] += res.question.max_score if res.question else 0
            if entry['max_possible'] > 0:
                entry['percentage'] = (entry['total_score'] / entry['max_possible']) * 100

    # --- Calculate points, aggregates, and divisions ---
    for term_key, data in report_data.items():
        for ex_type in ['BOT', 'MOT', 'EOT']:
            subjects_dict = data[ex_type]
            subject_list = []
            total_points = 0
            subject_count = 0

            for sub, val in subjects_dict.items():
                # Ensure percentage is calculated
                if val['percentage'] == 0 and val['max_possible'] > 0:
                    val['percentage'] = (val['total_score'] / val['max_possible']) * 100
                
                percentage = val['percentage']
                
                # Calculate points based on Uganda primary system
                points = calculate_points_uganda(percentage)
                val['points'] = points
                
                # Add to aggregate calculation (only for subjects with valid scores)
                if points > 0:
                    total_points += points
                    subject_count += 1
                
                # Auto remark based on percentage
                val['auto_remark'] = (
                    "Excellent work" if percentage >= 75 else
                    "Fair — keep improving" if percentage >= 50 else
                    "Needs serious effort"
                )
                
                subject_list.append(val)

            # Replace dict with list for template use
            data[ex_type] = subject_list

            # --- Calculate average percentage ---
            if subject_list:
                avg = sum(float(s['percentage']) for s in subject_list) / len(subject_list)
                data[f"{ex_type}_average"] = round(avg, 2)
            else:
                data[f"{ex_type}_average"] = 0

            # --- Calculate aggregate and division ---
            if subject_count > 0:
                aggregate = total_points
                data[f"{ex_type}_aggregate"] = aggregate
                data[f"{ex_type}_division"] = calculate_division_uganda(aggregate)
            else:
                data[f"{ex_type}_aggregate"] = 0
                data[f"{ex_type}_division"] = "Ungraded"

    # --- Determine next term start date ---
    all_exam_sessions = [res.exam_session for res in results if res.exam_session]
    next_term_date = None
    if all_exam_sessions:
        last_exam = max(
            all_exam_sessions,
            key=lambda x: (x.term.year, ['TERM_1', 'TERM_2', 'TERM_3'].index(x.term.term_name))
        )
        term_order = ['TERM_1', 'TERM_2', 'TERM_3']
        current_index = term_order.index(last_exam.term.term_name)
        next_term_name = None
        next_year = last_exam.term.year

        if current_index + 1 < len(term_order):
            next_term_name = term_order[current_index + 1]
        else:
            next_term_name = 'TERM_1'
            next_year += 1

        next_session = ExamSession.objects.filter(
            term__year=next_year,
            term__term_name=next_term_name,
            exam_type='BOT'
        ).first()

        if next_session:
            next_term_date = next_session.start_date

    # --- Division system ---
    division_system = [
        {"range": "4 – 12", "division": "Division One", "performance": "Excellent"},
        {"range": "13 – 23", "division": "Division Two", "performance": "Very Good"},
        {"range": "24 – 29", "division": "Division Three", "performance": "Good"},
        {"range": "30 – 34", "division": "Division Four", "performance": "Fair"},
        {"range": "35 and above", "division": "Ungraded / Fail", "performance": "Poor"},
    ]

    exam_types = ["BOT", "MOT", "EOT"]

    return render(request, "reports/student_term_report.html", {
        "report_data": report_data,
        "next_term_date": next_term_date,
        "exam_types": exam_types,
        "schoolname": schoolname,
        "schoolbadge": schoolbadge,
        "schoolemail": schoolemail,
        "schoolcontact": schoolcontact,
        "schoolbox": schoolbox,
        "school_location": school_location,
        "student": student,
        "division_system": division_system,
        "class_teacher_remark": "Keep up the good discipline and focus.",
        "head_teacher_remark": "Promoted to next class. Congratulations!",
    })

def calculate_points_uganda(percentage):
    """Calculate points for Uganda primary system"""
    if percentage >= 90:
        return 1
    elif percentage >= 80:
        return 2
    elif percentage >= 70:
        return 3
    elif percentage >= 65:
        return 4
    elif percentage >= 60:
        return 5
    elif percentage >= 50:
        return 6
    elif percentage >= 45:
        return 7
    elif percentage >= 35:
        return 8
    else:
        return 9

def calculate_division_uganda(aggregate):
    """Calculate division based on aggregate points for Uganda system"""
    if 4 <= aggregate <= 12:
        return "Division One"
    elif 13 <= aggregate <= 23:
        return "Division Two"
    elif 24 <= aggregate <= 29:
        return "Division Three"
    elif 30 <= aggregate <= 34:
        return "Division Four"
    else:
        return "Ungraded / Fail"