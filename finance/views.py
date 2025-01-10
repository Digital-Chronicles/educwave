from django.shortcuts import render
from students.models import Student
from .models import StudentTuitionDescription
from django.db.models import Sum

# Create your views here.
def finance(request):
    # Get all StudentTuitionDescription records and calculate the total fees
    total_fees = StudentTuitionDescription.objects.aggregate(total=Sum('total_fee'))['total'] or 0

    return render(request, "finance.html", {"total_fees": total_fees})