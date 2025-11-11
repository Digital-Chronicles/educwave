import csv
from io import TextIOWrapper
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.db import transaction
from academic.models import Grade, StudentMarkSummary, Subject, TermExamSession,ExamSession
from students.models import Student
from assessment.models import Question, ExamResult


class ExamResultsView(View):
    """Main view to display exam results entry interface"""
    template_name = 'assessment/exam_results.html'
    
    def get(self, request):
        term_id = request.GET.get('term_id')
        grade_id = request.GET.get('grade_id')

        # Filter exam types based on selected term
        if term_id:
            exam_types = ExamSession.objects.filter(term_id=term_id)
        else:
            exam_types = ExamSession.objects.none()  # Empty until a term is chosen

        # Filter subjects based on selected grade
        if grade_id:
            subjects = Subject.objects.filter(grade_id=grade_id).select_related('curriculum').order_by('name')
        else:
            subjects = Subject.objects.none()  # Empty until grade is chosen

        context = {
            'grades': Grade.objects.all().order_by('grade_name'),
            'subjects': subjects,
            'terms': TermExamSession.objects.all().order_by('-year', 'term_name'),
            'exam_types': exam_types,
        }
        return render(request, self.template_name, context)

class ExamResultsEntryView(View):
    """View for entering and managing exam results"""
    template_name = 'assessment/exam_results_entry.html'
    
    def _get_required_objects(self, grade_id, subject_id, exam_id):
        """Helper method to fetch and validate required objects"""
        try:
            exam = ExamSession.objects.get(id=exam_id)
            print(exam.exam_type)  # prints "BOT"
            print(exam.id)         # prints an integer, e.g., 2
            return {
                'grade': Grade.objects.get(id=grade_id),
                'subject': Subject.objects.get(id=subject_id),
                'term': exam.term,   # each exam session belongs to a term
                'exam': exam,        # the specific exam type (BOT, MOT, EOT)
            }
        except (Grade.DoesNotExist, Subject.DoesNotExist, ExamSession.DoesNotExist) as e:
            raise ValueError(f"Invalid selection: {str(e)}")
    
    def _prepare_context(self, grade, subject, term, exam):
        """Prepare context data with students, questions and existing results"""
        students = Student.objects.filter(current_grade=grade).order_by('first_name')
        
        # Filter questions by both term_exam and exam_type
        questions = Question.objects.filter(
            grade=grade,
            subject=subject,
            term_exam=term,
            exam_type=exam
        ).select_related('topic').order_by('question_number')
        
        # Prefetch existing results
        existing_results = ExamResult.objects.filter(
            grade=grade,
            subject=subject,
            question__in=questions,
            student__in=students
        ).select_related('student', 'question')
        
        results_dict = {
            (result.student_id, result.question_id): result.score
            for result in existing_results
        }
        
        return {
            'grade': grade,
            'subject': subject,
            'term': term,
            'exam': exam,
            'students': students,
            'questions': questions,
            'existing_results': results_dict,
        }
    
    def get(self, request):
        grade_id = request.GET.get('grade_id')
        subject_id = request.GET.get('subject_id')
        exam_id = request.GET.get('exam_id')
        
        if not all([grade_id, subject_id, exam_id]):
            messages.error(request, "Please select grade, subject and exam.")
            return redirect('assessment:exam_results')
        
        try:
            objects = self._get_required_objects(grade_id, subject_id, exam_id)
            context = self._prepare_context(**objects)
            return render(request, self.template_name, context)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('assessment:exam_results')
    
    @transaction.atomic
    def post(self, request):
        grade_id = request.POST.get('grade_id')
        subject_id = request.POST.get('subject_id')
        exam_id = request.POST.get('exam_id')  # ExamSession.id

        if not all([grade_id, subject_id, exam_id]):
            messages.error(request, "Please select grade, subject and exam.")
            return redirect('assessment:exam_results')

        try:
            objects = self._get_required_objects(grade_id, subject_id, exam_id)
            grade = objects['grade']
            subject = objects['subject']
            term = objects['term']
            exam = objects['exam']

            students = Student.objects.filter(current_grade=grade)
            questions = Question.objects.filter(
                grade=grade,
                subject=subject,
                term_exam=term,
                exam_type=exam
            )

            # --- Save each student's question-level result ---
            for student in students:
                for question in questions:
                    score_key = f"score_{student.id}_{question.id}"
                    score = request.POST.get(score_key, '').strip()
                    if not score:
                        continue
                    try:
                        score = int(score)
                        if score < 0 or score > question.max_score:
                            messages.error(
                                request,
                                f"Invalid score for {student} on Q{question.question_number}."
                            )
                            continue

                        ExamResult.objects.update_or_create(
                            student=student,
                            question=question,
                            defaults={
                                'grade': grade,
                                'subject': subject,
                                'topic': question.topic,
                                'exam_session': exam,  # ✅ Attached exam session
                                'score': score,
                            }
                        )
                    except ValueError:
                        messages.error(request, f"Invalid score format for {student}.")

            # --- Aggregate results into StudentMarkSummary ---
            for student in students:
                student_results = ExamResult.objects.filter(
                    student=student,
                    subject=subject,
                    exam_session=exam
                )

                if not student_results.exists():
                    continue

                total_score = sum(r.score for r in student_results)
                max_possible = sum(r.question.max_score for r in student_results if r.question)
                percentage = (total_score / max_possible * 100) if max_possible else 0

                StudentMarkSummary.objects.update_or_create(
                    student=student,
                    term_exam=term,
                    subject=subject,
                    exam_type=exam,
                    defaults={
                        'grade': grade,
                        'exam_type': exam,  # ✅ Fixed: ensures NOT NULL field is set
                        'total_score': total_score,
                        'max_possible': max_possible,
                        'percentage': round(percentage, 2),
                    }
                )

            messages.success(request, "Exam results saved successfully!")
            return redirect(f"{reverse('assessment:exam_results_entry')}?grade_id={grade_id}&subject_id={subject_id}&exam_id={exam_id}")

        except Exception as e:
            messages.error(request, f"Error saving results: {str(e)}")
            return redirect('assessment:exam_results')
     

def download_marks_template(request):
    # Get parameters from URL
    grade_id = request.GET.get('grade_id')
    subject_id = request.GET.get('subject_id')
    exam_id = request.GET.get('exam_id')
    
    if not all([grade_id, subject_id, exam_id]):
        messages.error(request, "Missing required parameters")
        return redirect('assessment:exam_results')

    try:
        # Get required data
        questions = Question.objects.filter(
            grade_id=grade_id,
            subject_id=subject_id,
            term_exam_id=exam_id
        ).order_by('question_number')
        
        students = Student.objects.filter(current_grade_id=grade_id).order_by('first_name')

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="marks_template.csv"'
        
        writer = csv.writer(response)
        
        # Write header row
        headers = ['student_id', 'first_name', 'last_name']
        headers.extend([f'Q{q.question_number}' for q in questions])
        writer.writerow(headers)
        
        # Write student rows
        for student in students:
            row = [student.id, student.first_name, student.last_name]
            row.extend([''] * questions.count())  # Empty cells for marks
            writer.writerow(row)
            
        return response
        
    except Exception as e:
        messages.error(request, f"Error generating template: {str(e)}")
        return redirect('assessment:exam_results')


def upload_marks(request):
    if request.method == 'POST' and request.FILES.get('marks_file'):
        grade_id = request.POST.get('grade_id')
        subject_id = request.POST.get('subject_id')
        exam_id = request.POST.get('exam_id')
        
        if not all([grade_id, subject_id, exam_id]):
            messages.error(request, "Missing required parameters")
            return redirect('assessment:exam_results')
        
        try:
            csv_file = TextIOWrapper(request.FILES['marks_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            
            questions = Question.objects.filter(
                grade_id=grade_id,
                subject_id=subject_id,
                term_exam_id=exam_id
            ).order_by('question_number')
            
            question_numbers = [f'Q{q.question_number}' for q in questions]
            
            # Process each row
            for row in reader:
                student_id = row['student_id']
                
                for i, question in enumerate(questions):
                    score_key = question_numbers[i]
                    score = row.get(score_key, '').strip()
                    
                    if not score:
                        continue
                    
                    try:
                        score = int(score)
                        if score < 0 or score > question.max_score:
                            messages.warning(
                                request,
                                f"Invalid score {score} for student {student_id} "
                                f"on Q{question.question_number}. Must be between 0 and {question.max_score}"
                            )
                            continue
                            
                        ExamResult.objects.update_or_create(
                            student_id=student_id,
                            question=question,
                            defaults={
                                'grade_id': grade_id,
                                'subject_id': subject_id,
                                'topic': question.topic,
                                'score': score
                            }
                        )
                        
                    except ValueError:
                        messages.warning(
                            request,
                            f"Invalid score format for student {student_id} on Q{question.question_number}"
                        )
            
            messages.success(request, "Marks uploaded successfully!")
            return redirect(
                f"{reverse('assessment:exam_results_entry')}?grade_id={grade_id}&subject_id={subject_id}&exam_id={exam_id}"
            )
                
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect('assessment:exam_results')
    
    return redirect('assessment:exam_results')
class SubjectTotalEntryView(View):
    template_name = "assessment/subject_totals_entry.html"

    def get(self, request):
        grade_id = request.GET.get("grade_id")
        exam_id = request.GET.get("exam_id")
        term_id = request.GET.get("term_id")

        if not all([grade_id, exam_id, term_id]):
            messages.error(request, "Please select grade, term, and exam.")
            return redirect("assessment:exam_results")

        grade = Grade.objects.get(id=grade_id)
        exam = ExamSession.objects.get(id=exam_id)
        term = TermExamSession.objects.get(id=term_id)
        students = Student.objects.filter(current_grade=grade).order_by("first_name")
        subjects = Subject.objects.filter(grade=grade)

        context = {
            "grade": grade,
            "exam": exam,
            "term": term,
            "students": students,
            "subjects": subjects,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        grade_id = request.POST.get("grade_id")
        exam_id = request.POST.get("exam_id")
        term_id = request.POST.get("term_id")

        grade = Grade.objects.get(id=grade_id)
        exam = ExamSession.objects.get(id=exam_id)
        term = TermExamSession.objects.get(id=term_id)

        students = Student.objects.filter(current_grade=grade)
        subjects = Subject.objects.filter(grade=grade)

        for student in students:
            for subject in subjects:
                field_name = f"total_{student.id}_{subject.id}"
                score = request.POST.get(field_name)
                if score:
                    try:
                        score = int(score)
                        StudentMarkSummary.objects.update_or_create(
                            student=student,
                            term_exam=term,
                            exam_type=exam,
                            subject=subject,
                            defaults={
                                "grade": grade,
                                "total_score": score,
                                "max_possible": 100,
                                "percentage": score,
                            }
                        )
                    except ValueError:
                        messages.error(request, f"Invalid score for {student} - {subject}")

        messages.success(request, "Subject totals saved successfully!")
        return redirect(f"{reverse('assessment:subject_total_entry')}?grade_id={grade_id}&exam_id={exam_id}&term_id={term_id}")
