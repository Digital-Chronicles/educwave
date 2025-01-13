from django.shortcuts import render
from students.models import Student
from .models import StudentTuitionDescription, FeeTransaction
from django.db.models import Sum

# Create your views here.
def finance(request):
    # Get all StudentTuitionDescription records and calculate the total fees
    recent_fees_transactions = FeeTransaction.objects.all().order_by('-created')[:10]
    estimated_collections = StudentTuitionDescription.objects.aggregate(total=Sum('total_fee'))['total'] or 0


    return render(request, "finance.html", {"estimated_collections": estimated_collections, "recent_fees_transactions":recent_fees_transactions})