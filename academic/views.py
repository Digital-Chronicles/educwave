from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.views import generic
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from django.db.models import Sum, Avg
from .models import Grade, Subject, Curriculum, Topic, Exam, Notes, StudentMark, TermExamSession
from .forms import GradeForm, SubjectForm, CurriculumForm, TopicForm, ExamForm, NotesForm, StudentMarksForm
from students.models import Student
from management.models import GeneralInformation
from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required


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
    allowed_roles = ['TEACHER', 'FINANCE']

    
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
    allowed_roles = ['TEACHER', 'FINANCE']

class RegisterSubject(generic.CreateView, RoleRequiredMixin):
    model = Subject
    template_name = "registerSubject.html"
    form_class = SubjectForm
    success_url = "/"
    allowed_roles = ['TEACHER', 'FINANCE']

class RegisterCurriculum(generic.CreateView, RoleRequiredMixin):
    model = Curriculum
    template_name = "registerCurriculum.html"
    form_class = CurriculumForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'FINANCE']

class RegisterTopic(generic.CreateView, RoleRequiredMixin):
    model = Topic
    template_name = "registerTopic.html"
    form_class = TopicForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'FINANCE']

class UploadExamView(generic.CreateView, RoleRequiredMixin):
    model = Exam
    template_name = "uploadExam.html"
    form_class = ExamForm
    success_url = '/'
    allowed_roles = ['TEACHER', 'FINANCE']

    def form_valid(self, form):
        form.instance.created_by = self.request.user.teacher
        return super().form_valid(form)

class UploadNotesView(generic.CreateView, RoleRequiredMixin):
    model = Notes
    form_class = NotesForm
    template_name = 'uploadNotes.html'
    success_url = "/"
    allowed_roles = ['TEACHER', 'FINANCE']

    def form_valid(self, form):
        form.instance.created_by = self.request.user 
        return super().form_valid(form)
    
class RegisterStudentMarksView(RoleRequiredMixin, generic.CreateView):
    model = StudentMark
    form_class = StudentMarksForm
    template_name = "registerStudentMarks.html"
    allowed_roles = ['TEACHER', 'FINANCE']

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
    

@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def studentMarks(request):
    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    term_filter = request.GET.get('term', '')
    
    
    # Build base queryset
    queryset = StudentMark.objects.select_related(
        'student',
        'subject',
        'term'
    ).order_by('-term__year', 'term__term_name', 'student__registration_id')
    
    # Apply filters
    if search_query:
        queryset = queryset.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__registration_id__icontains=search_query)
        )
    
    if term_filter:
        queryset = queryset.filter(term__id=term_filter)
    
    # Process student data
    student_data = defaultdict(lambda: {
        'reg_id': '',
        'name': '',
        'term': '',
        'marks': {},
        'total': 0,
        'count': 0
    })
    
    print("Printing Queryset: ", queryset)

    for mark in queryset:
        student_key = f"{mark.student.registration_id}_{mark.term.id}"
        data = student_data[student_key]
        
        data['reg_id'] = mark.student.registration_id
        data['name'] = f"{mark.student.first_name} {mark.student.last_name}"
        data['term'] = str(mark.term)
        data['marks'][mark.subject.name] = mark.marks
        data['total'] += mark.marks
        data['count'] += 1
        
        if data['count'] > 0:
            data['average'] = round(data['total'] / data['count'], 2)
            data['grade'] = mark.get_grade()  # Get grade for the average

    # Convert to list and calculate statistics
    final_data = list(student_data.values())
    total_students = len(final_data)
    
    if total_students > 0:
        average_score = round(sum(s['average'] for s in final_data) / total_students, 2)
        passing_rate = round(sum(1 for s in final_data if s['average'] >= 40) / total_students * 100, 2)
    else:
        average_score = passing_rate = 0
    
    # Pagination
    paginator = Paginator(final_data, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    
    context = {
        'page_obj': page_obj,
        'terms': TermExamSession.objects.all().order_by('-year', 'term_name'),
        'subjects': Subject.objects.all().order_by('name'),
        'total_students': total_students,
        'average_score': average_score,
        'passing_rate': passing_rate,
        'current_term': term_filter,
        'search_query': search_query,
    }
    
    return render(request, 'studentsMarks.html', context)

@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def studentPerformance(request, id):
    student = get_object_or_404(Student, id=id)
    
    # Get all marks and print the count for debugging
    student_marks = StudentMark.objects.filter(student=student).order_by('-term__year', 'term__term_name')
    print(f"Total marks found: {student_marks.count()}")
    marks_by_term_and_exam = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for mark in student_marks:
        year = mark.term.year
        term_name = mark.term.get_term_name_display()
        exam_type = mark.term.get_exam_type_display()
        
        marks_by_term_and_exam[year][term_name][exam_type].append(mark)
        
        print(f"Processing mark: Year={year}, Term={term_name}, Exam={exam_type}, Subject={mark.subject.name}")

    
    marks_dict = {
        year: {
            term: dict(exams) for term, exams in terms.items()
        } for year, terms in marks_by_term_and_exam.items()
    }

    print("Final marks structure:", marks_dict)

    context = {
        'student': student,
        'marks_by_term_and_exam': marks_dict
    }
    
    return render(request, "studentPerformance.html", context)

@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def studentReport(request, id, term_name, year):
    # Get student object or 404
    student = get_object_or_404(Student, id=id)
    school = GeneralInformation.objects.first()

    # Calculate term averages and total marks
    all_marks = StudentMark.objects.filter(student=student, term__term_name=term_name, term__year=year)
    beginning_of_term = StudentMark.objects.filter(student=student, term__term_name=term_name, term__year=year, term__exam_type = 'BOT',  )
    mid_of_term = StudentMark.objects.filter(student=student, term__term_name=term_name, term__year=year, term__exam_type = 'MOT')
    end_of_term = StudentMark.objects.filter(student=student, term__term_name=term_name, term__year=year, term__exam_type = 'EOT')

    # Mark Avg Sum and Count
    term_total = all_marks.aggregate(total=Sum('marks'))['total'] or 0
    term_average = all_marks.aggregate(avg=Avg('marks'))['avg'] or 0
    bot_total = beginning_of_term.aggregate(total=Sum('marks'))['total'] or 0
    bot_average = beginning_of_term.aggregate(avg=Avg('marks'))['avg'] or 0
    mot_total = mid_of_term.aggregate(total=Sum('marks'))['total'] or 0
    mot_average = mid_of_term.aggregate(avg=Avg('marks'))['avg'] or 0
    eot_total = end_of_term.aggregate(total=Sum('marks'))['total'] or 0
    eot_average = end_of_term.aggregate(avg=Avg('marks'))['avg'] or 0
    subject_count = all_marks.values('subject').distinct().count()
    bot_grade = sum(mark.get_grade() for mark in beginning_of_term)
    bot_of_total = len(beginning_of_term) * 100
    mot_of_total = len(mid_of_term) * 100
    eot_of_total = len(end_of_term) * 100
    

    context = {
        'student': student,
        'all_marks': all_marks,
        'term_total': term_total,
        'term_average': round(term_average, 1),
        'subject_count': subject_count,
        'year': year,
        'term_name': term_name,
        'school':school,
        'beginning_of_term':beginning_of_term,
        'mid_of_term':mid_of_term,
        'end_of_term':end_of_term,
        'bot_total':bot_total,
        'bot_average':bot_average,
        'mot_total':mot_total,
        'mot_average':mot_average,
        'eot_total':eot_total,
        'eot_average':eot_average,
        'bot_of_total':bot_of_total,
        'mot_of_total':mot_of_total,
        'eot_of_total':eot_of_total,
        'bot_grade': bot_grade,
        'term_display': {
            'term_1': 'Term One',
            'term_2': 'Term Two',
            'term_3': 'Term Three'
        }.get(term_name, ' ')
    }

    return render(request, "studentReport.html", context)


@role_required(allowed_roles=['ADMIN', 'ACADEMIC'])
def print_term_result(request, student_id, id):
    student = get_object_or_404(Student, id=student_id)
    marks = StudentMark.objects.filter(student=student, term__id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.first_name}_{id}_result.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    data = [["Subject", "Teacher", "Marks", "Grade"]]
    for mark in marks:
        data.append([mark.subject.name, f"{mark.teacher.first_name} {mark.teacher.last_name}", mark.marks, mark.get_grade()])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements = [Paragraph(f"Term Result for {student.first_name} - {id}", styles['Title']), table]
    doc.build(elements)

    return response
