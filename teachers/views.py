from urllib import request
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views import generic 
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *       
from django.urls import reverse_lazy
from django.db.models import Q
from academic.models import Exam
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Teacher
from academic.models import Grade, Subject, TermExamSession, ExamSession
from students.models import Student
from assessment.models import ExamResult
import pandas as pd

@login_required
def teacher_dashboard(request):
    """Simple, task-oriented dashboard for teachers"""
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        # If user is not a teacher, redirect to appropriate dashboard
        return redirect('teachers:teachers')
    
    # Auto-detect current context
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    # Get teacher's context
    assigned_classes = Grade.objects.filter(class_teacher=teacher)
    assigned_subjects = Subject.objects.filter(teacher=teacher)
    pending_tasks = get_pending_mark_entries(teacher, current_term, current_exam)
    
    context = {
        'teacher': teacher,
        'current_term': current_term,
        'current_exam': current_exam,
        'assigned_classes': assigned_classes,
        'assigned_subjects': assigned_subjects,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'teachers/dashboard.html', context)

@login_required
def quick_mark_entry(request):
    """One-click mark entry - auto-detects context"""
    teacher = request.user.teacher_profile
    
    # Get request parameters or use defaults
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    
    # Auto-detect context
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    # Get teacher's classes
    assigned_classes = Grade.objects.filter(class_teacher=teacher, is_active=True)
    
    # Determine selected class
    selected_class = assigned_classes.first()
    if class_id:
        selected_class = get_object_or_404(Grade, id=class_id, class_teacher=teacher)
    
    # Get subjects ONLY for the selected class
    assigned_subjects = Subject.objects.filter(
        teacher=teacher,
        grade=selected_class,  # Filter by selected class
        is_active=True
    ) if selected_class else Subject.objects.none()
    
    # Determine selected subject
    selected_subject = assigned_subjects.first()
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id, teacher=teacher, grade=selected_class)
    
    # Get students and existing marks
    students = Student.objects.filter(current_grade=selected_class) if selected_class else []
    existing_marks = get_existing_marks(students, selected_subject, current_exam) if selected_subject else {}
    
    if request.method == 'POST':
        if not selected_subject or not current_exam:
            messages.error(request, "Please select a subject and ensure an active exam session exists.")
            return redirect('teachers:quick_mark_entry')
        return handle_quick_mark_submission(request, students, selected_subject, selected_class, current_exam)
    
    context = {
        'current_term': current_term,
        'current_exam': current_exam,
        'assigned_classes': assigned_classes,
        'assigned_subjects': assigned_subjects,
        'selected_class': selected_class,
        'selected_subject': selected_subject,
        'students': students,
        'existing_marks': existing_marks,
    }
    return render(request, 'teachers/quick_mark_entry.html', context)

@login_required
def bulk_marks_upload(request):
    """Excel upload for marks"""
    teacher = request.user.teacher_profile
    
    if request.method == 'POST' and request.FILES.get('marks_file'):
        excel_file = request.FILES['marks_file']
        
        try:
            success_count = process_excel_marks(excel_file, teacher)
            messages.success(request, f"Successfully imported {success_count} marks!")
            return redirect('teachers:dashboard')
            
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
    
    return render(request, 'teachers/bulk_upload.html')

# Helper functions
def get_current_term():
    """Get current active term"""
    return TermExamSession.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first() or TermExamSession.objects.order_by('-start_date').first()

def get_current_exam(term):
    """Get current exam session"""
    if term:
        return ExamSession.objects.filter(
            term=term,
            exam_type='EOT'  # Default to End of Term
        ).first()
    return None

def get_pending_mark_entries(teacher, term, exam):
    """Get classes/subjects that need mark entry"""
    if not term or not exam:
        return []
    
    pending = []
    for class_obj in Grade.objects.filter(class_teacher=teacher):
        for subject in Subject.objects.filter(teacher=teacher, grade=class_obj):
            has_marks = ExamResult.objects.filter(
                exam_session=exam,
                subject=subject,
                grade=class_obj
            ).exists()
            
            if not has_marks:
                student_count = Student.objects.filter(current_grade=class_obj).count()
                pending.append({
                    'class': class_obj,
                    'subject': subject,
                    'student_count': student_count
                })
    
    return pending

def get_existing_marks(students, subject, exam):
    """Get existing marks for quick editing"""
    if not exam:
        return {}
    
    marks = ExamResult.objects.filter(
        student__in=students,
        subject=subject,
        exam_session=exam,
        question__isnull=True  # Subject totals only
    )
    return {mark.student_id: mark.score for mark in marks}

def handle_quick_mark_submission(request, students, subject, grade, exam):
    """Process quick mark entry form"""
    if not exam:
        messages.error(request, "No active exam session found.")
        return redirect('teachers:quick_mark_entry')
    
    success_count = 0
    errors = []
    
    # DEBUG: Print exam and subject info
    print(f"DEBUG: Exam: {exam}, Subject: {subject}, Grade: {grade}")
    
    for student in students:
        score_key = f"score_{student.id}"
        score_val = request.POST.get(score_key, '').strip()
        
        if score_val:  # Only process if there's a value
            try:
                score = int(score_val)
                if 0 <= score <= 100:
                    # DEBUG: Print before save
                    print(f"DEBUG: Saving mark for {student} - Score: {score}")
                    
                    # Create or update ExamResult record
                    exam_result, created = ExamResult.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_session=exam,
                        question=None,  # This makes it a subject total
                        defaults={
                            'grade': grade,
                            'score': score,
                            'total_score': score,
                            'max_possible': 100,
                            'percentage': float(score),
                        }
                    )
                    
                    # DEBUG: Verify save
                    print(f"DEBUG: {'Created' if created else 'Updated'} - ID: {exam_result.id}")
                    
                    success_count += 1
                else:
                    errors.append(f"Invalid score for {student.get_full_name()}: {score_val} (must be 0-100)")
            except Exception as e:
                errors.append(f"Error for {student.get_full_name()}: {str(e)}")
                print(f"ERROR saving {student}: {str(e)}")  # Debug
    
    # Show messages
    if success_count > 0:
        messages.success(request, f"✅ Successfully saved marks for {success_count} students!")
    
    if errors:
        for error in errors[:5]:
            messages.warning(request, error)
    
    return redirect('teachers:quick_mark_entry')
def process_excel_marks(excel_file, teacher):
    """Process Excel file for bulk mark upload"""
    df = pd.read_excel(excel_file)
    success_count = 0
    
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    for index, row in df.iterrows():
        try:
            registration_id = str(row['registration_id']).strip()
            subject_name = str(row['subject']).strip()
            score = int(row['score'])
            
            student = Student.objects.get(registration_id=registration_id)
            subject = Subject.objects.get(name=subject_name, teacher=teacher)
            
            if current_exam:
                ExamResult.objects.update_or_create(
                    student=student,
                    subject=subject,
                    exam_session=current_exam,
                    question=None,
                    defaults={
                        'grade': student.current_grade,
                        'score': score,
                        'total_score': score,
                        'max_possible': 100,
                        'percentage': (score / 100) * 100,
                    }
                )
                success_count += 1
                
        except (Student.DoesNotExist, Subject.DoesNotExist, KeyError, ValueError):
            continue
    
    return success_count


@login_required
def teacher_reports(request):
    """Placeholder for teacher reports"""
    teacher = request.user.teacher_profile
    # You can implement this later
    return render(request, 'teachers/reports.html', {'teacher': teacher})

@login_required
def class_reports(request, class_id):
    """Placeholder for class-specific reports"""
    teacher = request.user.teacher_profile
    class_obj = get_object_or_404(Grade, id=class_id, class_teacher=teacher)
    # You can implement this later
    return render(request, 'teachers/class_reports.html', {
        'teacher': teacher,
        'class_obj': class_obj
    })

@login_required
def my_classes(request):
    """Detailed view of teacher's classes"""
    teacher = request.user.teacher_profile
    assigned_classes = Grade.objects.filter(class_teacher=teacher, is_active=True)
    
    return render(request, 'teachers/my_classes.html', {
        'teacher': teacher,
        'assigned_classes': assigned_classes,
    })

@login_required
def teacher_profile(request):
    """Teacher profile page"""
    teacher = request.user.teacher_profile
    return render(request, 'teachers/profile.html', {'teacher': teacher})
class RegisterTeacherDetails(RoleRequiredMixin, generic.CreateView):
    model = Teacher
    template_name = 'registerteacherdetails.html'
    form_class = TeacherForm
    allowed_roles = ['TEACHER', 'FINANCE', 'ADMIN']
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_form"] = UserCreateForm()  # <-- add this
        return ctx

    def form_valid(self, form):
        teacher = form.save()
        return redirect(f'/teachers/details/{teacher.pk}/')
    
import pandas as pd
from django.http import HttpResponse
from django.utils.text import slugify
from io import BytesIO

@login_required
def bulk_marks_upload(request):
    """Bulk marks upload page with download template option"""
    teacher = request.user.teacher_profile
    
    if request.method == 'POST':
        if 'download_template' in request.POST:
            return download_template_csv(request, teacher)
        elif 'marks_file' in request.FILES:
            excel_file = request.FILES['marks_file']
            file_name = excel_file.name.lower()
            
            print(f"DEBUG: Uploading file: {file_name}")
            
            # Detect file type
            if file_name.endswith('.csv'):
                print("DEBUG: Processing as CSV file")
                return handle_csv_upload(request, excel_file, teacher)
            elif file_name.endswith(('.xlsx', '.xls')):
                print("DEBUG: Processing as Excel file")
                return handle_excel_upload(request, excel_file, teacher)
            else:
                messages.error(request, "Please upload a CSV (.csv) or Excel (.xlsx, .xls) file")
                return redirect('teachers:bulk_upload')
    
    # Get teacher's classes and subjects for the template
    assigned_classes = Grade.objects.filter(class_teacher=teacher, is_active=True)
    students = Student.objects.filter(current_grade__in=assigned_classes)
    
    context = {
        'teacher': teacher,
        'assigned_classes': assigned_classes,
        'student_count': students.count(),
        'subjects': Subject.objects.filter(teacher=teacher, is_active=True),
    }
    return render(request, 'teachers/bulk_upload.html', context)
def download_template_csv(teacher):
    """Download CSV template filtered by teacher's classes"""
    # Get current context
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    if not current_exam:
        messages.error(request, "No active exam session found")
        return redirect('teachers:bulk_upload')
    
    # Get teacher's classes
    assigned_classes = Grade.objects.filter(class_teacher=teacher, is_active=True)
    
    # Create CSV content with separate sections for each class
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    for class_obj in assigned_classes:
        # Write class header
        writer.writerow([f"CLASS: {class_obj.grade_name}"])
        
        # Get students in this class
        students = Student.objects.filter(current_grade=class_obj).order_by('first_name')
        
        # Get subjects for THIS CLASS taught by this teacher
        subjects = Subject.objects.filter(
            grade=class_obj, 
            teacher=teacher, 
            is_active=True
        ).order_by('name')
        
        if not subjects.exists():
            writer.writerow([f"No subjects assigned for {class_obj.grade_name}"])
            writer.writerow([])
            continue
        
        # Create headers for this class
        headers = ['student_id', 'registration_id', 'student_name']
        for subject in subjects:
            headers.append(subject.name)
        
        writer.writerow(headers)
        
        # Write student rows for this class
        for student in students:
            row = [
                student.id,
                student.registration_id,
                f"{student.first_name} {student.last_name}",
            ]
            
            # Add empty cells for each subject
            for subject in subjects:
                row.append('')
            
            writer.writerow(row)
        
        writer.writerow([])  # Empty row between classes
    
    # Add instructions
    writer.writerow(['INSTRUCTIONS:'])
    writer.writerow(['1. Fill scores in subject columns (0-100)'])
    writer.writerow(['2. Each class is in a separate section'])
    writer.writerow(['3. Do NOT modify student_id or registration_id'])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    filename = f"marks_template_{teacher.user.username}_{current_term.year}_{current_exam.exam_type}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
def handle_csv_upload(request, csv_file, teacher):
    """Handle CSV file upload with detailed debugging"""
    try:
        print(f"DEBUG: Starting CSV upload for teacher: {teacher.user.username}")
        print(f"DEBUG: File name: {csv_file.name}, Size: {csv_file.size}")
        
        # Read CSV file
        import pandas as pd
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                csv_file.seek(0)  # Reset file pointer
                df = pd.read_csv(csv_file, encoding=encoding)
                print(f"DEBUG: Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                print(f"DEBUG: Failed to read with {encoding} encoding")
                continue
        
        if df is None:
            messages.error(request, "Unable to read CSV file. Please save as UTF-8 encoding.")
            return redirect('teachers:bulk_upload')
        
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: Columns: {list(df.columns)}")
        print(f"DEBUG: First few rows:")
        print(df.head().to_string())
        
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        # Check if we have subject columns format
        required_columns = ['student_id', 'registration_id', 'student_name', 'class']
        subject_columns = [col for col in df.columns if col not in required_columns]
        
        if subject_columns:
            print(f"DEBUG: Detected subject columns: {subject_columns}")
            return process_subject_columns_csv(request, df, teacher, subject_columns)
        else:
            print(f"DEBUG: No subject columns detected, checking for old format")
            # Check for old format columns
            if all(col in df.columns for col in ['student_id', 'subject', 'score']):
                return process_old_format_csv(request, df, teacher)
            else:
                messages.error(request, "Invalid CSV format. Please use the template from this page.")
                return redirect('teachers:bulk_upload')
        
    except Exception as e:
        print(f"FATAL ERROR in CSV upload: {str(e)}")
        import traceback
        traceback.print_exc()
        
        messages.error(request, f"❌ Error processing CSV file: {str(e)}")
        return redirect('teachers:bulk_upload')

def process_subject_columns_csv(request, df, teacher, subject_columns):
    """Process CSV with subjects as columns"""
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    print(f"DEBUG: Current term: {current_term}")
    print(f"DEBUG: Current exam: {current_exam}")
    
    if not current_exam:
        messages.error(request, "No active exam session found")
        return redirect('teachers:bulk_upload')
    
    # Map subject names to Subject objects
    subject_objects = {}
    for subject_name in subject_columns:
        subject_name = str(subject_name).strip()
        try:
            # Try exact match
            subject = Subject.objects.get(name=subject_name, teacher=teacher)
            subject_objects[subject_name] = subject
            print(f"DEBUG: Found subject: '{subject_name}' -> {subject.id}")
        except Subject.DoesNotExist:
            # Try case-insensitive
            try:
                subject = Subject.objects.get(name__iexact=subject_name, teacher=teacher)
                subject_objects[subject_name] = subject
                print(f"DEBUG: Found subject (case-insensitive): '{subject_name}'")
            except Subject.DoesNotExist:
                print(f"DEBUG: Subject not found: '{subject_name}'")
                # Try to find similar subject
                similar = Subject.objects.filter(
                    name__icontains=subject_name,
                    teacher=teacher
                ).first()
                if similar:
                    subject_objects[subject_name] = similar
                    print(f"DEBUG: Using similar subject: '{subject_name}' -> '{similar.name}'")
    
    print(f"DEBUG: Mapped {len(subject_objects)} subjects")
    
    if not subject_objects:
        messages.error(request, "No valid subjects found in the file. Please check subject names.")
        return redirect('teachers:bulk_upload')
    
    success_count = 0
    error_rows = []
    saved_details = []
    
    # Process each row (student)
    for index, row in df.iterrows():
        try:
            # Get student info
            student_id = None
            registration_id = None
            
            if 'student_id' in row and pd.notna(row['student_id']):
                student_id = int(row['student_id'])
            if 'registration_id' in row and pd.notna(row['registration_id']):
                registration_id = str(row['registration_id']).strip()
            
            if not student_id and not registration_id:
                error_rows.append(f"Row {index+2}: Missing student_id and registration_id")
                continue
            
            # Find student
            student = None
            try:
                if student_id:
                    student = Student.objects.get(id=student_id)
                elif registration_id:
                    student = Student.objects.get(registration_id=registration_id)
            except Student.DoesNotExist:
                error_rows.append(f"Row {index+2}: Student not found (ID: {student_id}, Reg: {registration_id})")
                continue
            
            print(f"\nDEBUG: Processing student: {student} (ID: {student.id})")
            
            # Process each subject column
            for subject_name, subject in subject_objects.items():
                if subject_name in row and pd.notna(row[subject_name]) and str(row[subject_name]).strip() != '':
                    try:
                        score_str = str(row[subject_name]).strip()
                        score = float(score_str)
                        print(f"DEBUG:  Subject '{subject_name}': Score = {score}")
                        
                        # Validate score
                        if not (0 <= score <= 100):
                            error_rows.append(f"Row {index+2} ({student} - {subject_name}): Score {score} out of range")
                            continue
                        
                        # Check if student is in teacher's class
                        if not Grade.objects.filter(class_teacher=teacher, student=student).exists():
                            error_rows.append(f"Row {index+2} ({student}): Not in your classes")
                            continue
                        
                        # Save the mark
                        exam_result, created = ExamResult.objects.update_or_create(
                            student=student,
                            subject=subject,
                            exam_session=current_exam,
                            question=None,
                            defaults={
                                'grade': student.current_grade,
                                'score': int(score),
                                'total_score': int(score),
                                'max_possible': 100,
                                'percentage': float(score),
                            }
                        )
                        
                        print(f"DEBUG:  {'Created' if created else 'Updated'} mark: ID {exam_result.id}")
                        success_count += 1
                        saved_details.append(f"{student} - {subject}: {score}")
                        
                    except ValueError:
                        error_rows.append(f"Row {index+2} ({student} - {subject_name}): Invalid score '{row[subject_name]}'")
                    except Exception as e:
                        error_rows.append(f"Row {index+2} ({student} - {subject_name}): Error - {str(e)}")
                        print(f"ERROR: {e}")
        
        except Exception as e:
            error_rows.append(f"Row {index+2}: Processing error - {str(e)}")
            print(f"ERROR processing row {index+2}: {e}")
    
    print(f"\nDEBUG: Processing complete")
    print(f"DEBUG: Successfully saved {success_count} marks")
    
    # Show results
    if success_count > 0:
        messages.success(request, f"✅ Successfully imported {success_count} marks!")
        
        # Show preview of saved marks
        if saved_details:
            preview = saved_details[:5]  # Show first 5
            for detail in preview:
                messages.info(request, f"✓ {detail}")
            if len(saved_details) > 5:
                messages.info(request, f"... and {len(saved_details) - 5} more")
    
    if error_rows:
        error_message = f"⚠️ {len(error_rows)} issues found. First few:"
        for error in error_rows[:5]:
            messages.warning(request, error)
        if len(error_rows) > 5:
            messages.warning(request, f"... and {len(error_rows) - 5} more")
    
    return redirect('teachers:bulk_upload')


def process_old_format_csv(df, teacher):
    """Process old format CSV (for backward compatibility)"""
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    if not current_exam:
        messages.error(request, "No active exam session found")
        return redirect('teachers:bulk_upload')
    
    success_count = 0
    error_rows = []
    
    for index, row in df.iterrows():
        try:
            student_id = row['student_id']
            subject_name = str(row['subject']).strip()
            
            # Skip rows with empty scores
            if pd.isna(row['score']) or str(row['score']).strip() == '':
                continue
                
            score = float(row['score'])
            
            # Validate score range
            if not (0 <= score <= 100):
                error_rows.append(f"Row {index+2}: Score {score} out of range (0-100)")
                continue
            
            # Find student and subject
            student = Student.objects.get(id=int(student_id))
            subject = Subject.objects.get(name=subject_name, teacher=teacher)
            
            # Save the mark
            ExamResult.objects.update_or_create(
                student=student,
                subject=subject,
                exam_session=current_exam,
                question=None,
                defaults={
                    'grade': student.current_grade,
                    'score': int(score),
                    'total_score': int(score),
                    'max_possible': 100,
                    'percentage': float(score),
                }
            )
            success_count += 1
            
        except Student.DoesNotExist:
            error_rows.append(f"Row {index+2}: Student ID {student_id} not found")
        except Subject.DoesNotExist:
            error_rows.append(f"Row {index+2}: Subject '{subject_name}' not found or not assigned to you")
        except ValueError as e:
            error_rows.append(f"Row {index+2}: Invalid data format")
        except Exception as e:
            error_rows.append(f"Row {index+2}: Error - {str(e)}")
    
    # Show results
    if success_count > 0:
        messages.success(request, f"✅ Successfully imported {success_count} marks!")
    
    if error_rows:
        error_message = f"❌ {len(error_rows)} errors occurred. First few: " + "; ".join(error_rows[:5])
        if len(error_rows) > 5:
            error_message += f" ... and {len(error_rows) - 5} more"
        messages.warning(request, error_message)
    
    return redirect('teachers:bulk_upload')

def handle_excel_upload(request, excel_file, teacher):
    """Handle Excel file upload with detailed debugging"""
    try:
        print(f"DEBUG: Starting Excel upload for teacher: {teacher.user.username}")
        print(f"DEBUG: File name: {excel_file.name}, Size: {excel_file.size}")
        
        # Check file extension
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Please upload an Excel file (.xlsx or .xls)")
            return redirect('teachers:bulk_upload')
        
        # Read Excel file with detailed info
        import pandas as pd
        df = pd.read_excel(excel_file)
        
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: Columns: {list(df.columns)}")
        print(f"DEBUG: First few rows:")
        print(df.head())
        
        # Check required columns
        required_columns = ['student_id', 'registration_id', 'student_name', 'class']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"DEBUG: Missing columns: {missing_columns}")
            messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
            return redirect('teachers:bulk_upload')
        
        # Identify subject columns (everything after required columns)
        subject_columns = [col for col in df.columns if col not in required_columns]
        print(f"DEBUG: Subject columns found: {subject_columns}")
        
        if not subject_columns:
            messages.error(request, "No subject columns found in the file")
            return redirect('teachers:bulk_upload')
        
        # Get current context
        current_term = get_current_term()
        current_exam = get_current_exam(current_term)
        
        print(f"DEBUG: Current term: {current_term}")
        print(f"DEBUG: Current exam: {current_exam}")
        
        if not current_exam:
            messages.error(request, "No active exam session found")
            return redirect('teachers:bulk_upload')
        
        # Map subject names to Subject objects
        subject_objects = {}
        for subject_name in subject_columns:
            try:
                subject = Subject.objects.get(name=subject_name, teacher=teacher)
                subject_objects[subject_name] = subject
                print(f"DEBUG: Found subject: {subject_name} -> {subject.id}")
            except Subject.DoesNotExist:
                print(f"DEBUG: Subject not found: {subject_name}")
                # Try case-insensitive search
                try:
                    subject = Subject.objects.get(name__iexact=subject_name, teacher=teacher)
                    subject_objects[subject_name] = subject
                    print(f"DEBUG: Found subject (case-insensitive): {subject_name}")
                except Subject.DoesNotExist:
                    print(f"DEBUG: Subject not found (case-insensitive): {subject_name}")
        
        print(f"DEBUG: Mapped {len(subject_objects)} subjects")
        
        if not subject_objects:
            messages.error(request, "No valid subjects found in the file. Please check subject names.")
            return redirect('teachers:bulk_upload')
        
        success_count = 0
        error_rows = []
        saved_marks = []
        
        # Process each row (student)
        for index, row in df.iterrows():
            try:
                student_id = row['student_id']
                registration_id = row['registration_id']
                student_name = row['student_name']
                
                print(f"\nDEBUG: Processing row {index+2}: {student_name} (ID: {student_id})")
                
                # Find student
                try:
                    student = Student.objects.get(id=int(student_id))
                    print(f"DEBUG: Found student: {student}")
                except Student.DoesNotExist:
                    # Try by registration_id
                    try:
                        student = Student.objects.get(registration_id=str(registration_id))
                        print(f"DEBUG: Found student by registration_id: {student}")
                    except Student.DoesNotExist:
                        error_rows.append(f"Row {index+2}: Student '{student_name}' (ID: {student_id}) not found")
                        continue
                
                # Process each subject column
                for subject_name, subject in subject_objects.items():
                    if subject_name in row and pd.notna(row[subject_name]) and str(row[subject_name]).strip() != '':
                        try:
                            score = float(row[subject_name])
                            print(f"DEBUG:  Subject {subject_name}: Score = {score}")
                            
                            # Validate score
                            if not (0 <= score <= 100):
                                error_rows.append(f"Row {index+2} ({student} - {subject_name}): Score {score} out of range")
                                continue
                            
                            # Check if student is in teacher's class
                            if not Grade.objects.filter(class_teacher=teacher, student=student).exists():
                                error_rows.append(f"Row {index+2} ({student}): Not in your classes")
                                continue
                            
                            # Save the mark
                            exam_result, created = ExamResult.objects.update_or_create(
                                student=student,
                                subject=subject,
                                exam_session=current_exam,
                                question=None,
                                defaults={
                                    'grade': student.current_grade,
                                    'score': int(score),
                                    'total_score': int(score),
                                    'max_possible': 100,
                                    'percentage': float(score),
                                }
                            )
                            
                            print(f"DEBUG:  {'Created' if created else 'Updated'} mark: ID {exam_result.id}")
                            success_count += 1
                            saved_marks.append(f"{student} - {subject}: {score}")
                            
                        except ValueError as e:
                            error_rows.append(f"Row {index+2} ({student} - {subject_name}): Invalid score format '{row[subject_name]}'")
                        except Exception as e:
                            error_rows.append(f"Row {index+2} ({student} - {subject_name}): Error - {str(e)}")
                            print(f"ERROR: {e}")
                
            except Exception as e:
                error_rows.append(f"Row {index+2}: Processing error - {str(e)}")
                print(f"ERROR processing row {index+2}: {e}")
        
        print(f"\nDEBUG: Processing complete")
        print(f"DEBUG: Successfully saved {success_count} marks")
        print(f"DEBUG: Errors: {len(error_rows)}")
        
        # Show results
        if success_count > 0:
            messages.success(request, f"✅ Successfully imported {success_count} marks!")
            # Show first few saved marks
            if saved_marks:
                preview = ", ".join(saved_marks[:3])
                messages.info(request, f"Saved: {preview}" + ("..." if len(saved_marks) > 3 else ""))
        
        if error_rows:
            error_message = f"⚠️ {len(error_rows)} warnings: " + "; ".join(error_rows[:3])
            if len(error_rows) > 3:
                error_message += f" ... and {len(error_rows) - 3} more"
            messages.warning(request, error_message)
        
        # Return to show results
        return redirect('teachers:bulk_upload')
        
    except Exception as e:
        print(f"FATAL ERROR in Excel upload: {str(e)}")
        import traceback
        traceback.print_exc()
        
        messages.error(request, f"❌ Error processing Excel file: {str(e)}")
        return redirect('teachers:bulk_upload')

@login_required
def download_class_template(request, class_id):
    """Download CSV template for specific class with subjects as columns"""
    teacher = request.user.teacher_profile
    class_obj = get_object_or_404(Grade, id=class_id, class_teacher=teacher)
    
    # Get current context
    current_term = get_current_term()
    current_exam = get_current_exam(current_term)
    
    # Get students in this class
    students = Student.objects.filter(current_grade=class_obj).order_by('first_name')
    
    # Get subjects for this class taught by this teacher
    subjects = Subject.objects.filter(grade=class_obj, teacher=teacher, is_active=True).order_by('name')
    
    # Create CSV content with subjects as columns
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Create headers
    headers = ['student_id', 'registration_id', 'student_name']
    for subject in subjects:
        headers.append(subject.name)  # Each subject as column
    
    writer.writerow(headers)
    
    # Write data rows - one row per student
    for student in students:
        row = [
            student.id,
            student.registration_id,
            f"{student.first_name} {student.last_name}",
        ]
        
        # Add empty cells for each subject
        for subject in subjects:
            row.append('')  # Empty score
        
        writer.writerow(row)
    
    # Add max score info
    writer.writerow([''])  # Empty row
    writer.writerow(['MAX_SCORE:'] + ['100'] * len(subjects))
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    filename = f"{class_obj.grade_name}_marks_{current_term.year}_{current_exam.exam_type}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
#Creating a user account for the teacher  
@login_required
@role_required(allowed_roles=['ADMIN', 'FINANCE'])
def create_user_account(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "TEACHER"
            user.save()
            messages.success(
                request, "User account created! You can now register teacher details.")
            return redirect("teacher_details")   # adjust URL name
    else:
        form = UserCreateForm()
    return render(request, "features/teachers-create_user.html", {"user_form": form})



class TeacherList(LoginRequiredMixin, ListView):
    template_name = "teachers.html"
    paginate_by = 10
    allowed_roles = ['ADMIN', 'FINANCE']

    def get_queryset(self):
        queryset = Teacher.objects.all()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(registration_id__icontains=search_query)
            )
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset =self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                "students":list(
                    page_obj.object_list.values(
                        "id", "registration_id", "first_name", "last_name", "gender", "year_of_entry"
                    )
                ),
                "has_next":page_obj.has_next(),
                "has_previous":page_obj.has_previous(),
                "current_page":page_obj.number,
                "total_pages":paginator.num_pages,
            }
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


# Teacher Detail
@role_required(allowed_roles=['ADMIN', 'FINANCE', "TEACHER"])
def teacher_details(request, id):
    # Fetch teacher object
    teacher = get_object_or_404(Teacher, id=id)

    # Attempt to get PayrollInformation, return None if not found
    teacher_payroll = PayrollInformation.objects.filter(teacher=teacher).first()
    education_background = EducationBackground.objects.filter(teacher=teacher)
    employment_history = EmploymentHistory.objects.filter(teacher=teacher)
    next_of_kin = NextOfKin.objects.filter(teacher=teacher).first()
    current_employment = CurrentEmployment.objects.filter(teacher=teacher).first()
    uploaded_exams = Exam.objects.filter(created_by = teacher)

    # Prepare context for template rendering
    context = {
        "teacher": teacher,
        "teacher_payroll": teacher_payroll,
        "education_background": education_background,
        "employment_history": employment_history,
        "next_of_kin": next_of_kin,
        "current_employment": current_employment,
        "uploaded_exams":uploaded_exams,
    }

    return render(request, "teachersDetails.html", context)



    
class Teacher_Payroll(RoleRequiredMixin, generic.CreateView):
    model = PayrollInformation
    template_name = 'payroll.html'
    form_class = PayrollInformationForm
    allowed_roles = ['ADMIN', 'FINANCE', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        form.save()
        return redirect(f'/teachers/details/{self.object.teacher.id}')

        

class Teacher_EducationBackground(RoleRequiredMixin, generic.CreateView):
    model = EducationBackground
    template_name = 'educationback.html'
    form_class = EducationBackgroundForm
    allowed_roles = ['ADMIN', 'FINANCE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        form.save()
        return redirect(f'/teachers/details/{self.object.teacher.id}')

class Teacher_EmploymentHistory(RoleRequiredMixin, generic.CreateView):
    model = EmploymentHistory
    template_name = 'employmenthistory.html'
    form_class = EmploymentHistoryForm
    allowed_roles = ['ADMIN', 'FINANCE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        form.save()
        return redirect(f'/teachers/details/{self.object.teacher.id}')

class Teacher_Next_of_Kin(RoleRequiredMixin, generic.CreateView):
    model = NextOfKin
    template_name = 'nextofkin.html'
    form_class = NextOfKinForm
    allowed_roles = ['ADMIN', 'FINANCE']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        form.save()
        return redirect(f'/teachers/details/{self.object.teacher.id}')

class Teacher_Current_Employment(RoleRequiredMixin, generic.CreateView):
    model = CurrentEmployment
    template_name = 'currentemployment.html'
    form_class = CurrentEmploymentForm
    allowed_roles = ['TEACHER', 'FINANCE','ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_id = self.kwargs['pk']
        teacher = get_object_or_404(Teacher, pk=teacher_id)
        context['teacher'] = teacher
        return context

    def form_valid(self, form):
        # Associate the payroll information with the correct teacher
        teacher_id = self.request.GET.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        form.instance.teacher = teacher
        form.save()
        return redirect(f'/teachers/details/{self.object.teacher.id}')