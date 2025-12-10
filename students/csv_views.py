import csv
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from .models import Student
from django.contrib.auth.decorators import login_required
from .forms import StudentCSVUploadForm
from management.models import GeneralInformation
from io import StringIO


@login_required
def download_student_csv_template(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header row
    headers = [
        "first_name", "last_name", "date_of_birth", "current_status", "current_grade",
        "gender", "grade_of_entry", "year_of_entry", "guardian_name",
        "guardian_phone", "father_name", "father_phone", "mother_name",
        "mother_phone"
    ]
    writer.writerow(headers)
    
    # Add example data row
    example_data = [
        "John", "Doe", "2015-05-15", "active", "Primary 1", "Male", "grade_1", "2023",
        "Jane Smith", "+1234567890", "Mike Doe", "+1234567891", 
        "Sarah Doe", "+1234567892"
    ]
    writer.writerow(example_data)
    
    return response


@login_required
def student_csv_view(request):
    school = GeneralInformation.objects.first()
    if not school:
        messages.error(request, "No school information found. Please add General Information first.")
        return redirect('students')

    if request.method == 'POST':
        form = StudentCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            created_count = 0
            for row in reader:
                try:
                    from academic.models import Grade 
                    grade_name = row['current_grade']
                    try:
                        grade_instance = Grade.objects.get(grade_name=grade_name)
                    except Grade.DoesNotExist:
                        messages.warning(request, f"Grade '{grade_name}' not found for student {row.get('first_name')} {row.get('last_name')}")
                        continue
                    except Grade.MultipleObjectsReturned:
                        grade_instance = Grade.objects.filter(name=grade_name).first()
                    student = Student(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        date_of_birth=row['date_of_birth'],
                        current_status=row.get('current_status', 'active'),
                        current_grade=grade_instance,
                        gender=row.get('gender', None),
                        grade_of_entry=row.get('grade_of_entry', None),
                        year_of_entry=row.get('year_of_entry', None),
                        guardian_name=row.get('guardian_name', None),
                        guardian_phone=row.get('guardian_phone', None),
                        father_name=row.get('father_name', None),
                        father_phone=row.get('father_phone', None),
                        mother_name=row.get('mother_name', None),
                        mother_phone=row.get('mother_phone', None),
                        school=school,
                        registered_by=request.user
                    )
                    student.save()
                    created_count += 1
                except Exception as e:
                    messages.warning(request, f"Error creating student {row.get('first_name')} {row.get('last_name')}: {str(e)}")
                    continue

            messages.success(request, f"{created_count} students created successfully.")
            return redirect('students')
    else:
        form = StudentCSVUploadForm()
    
    return render(request, 'students_upload_csv.html', {'form': form})

