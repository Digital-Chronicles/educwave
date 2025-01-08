from django.db import models
from academic.models import Grade
from accounts.models import CustomUser
from django.core.exceptions import ValidationError

# Create your models here.
class SchoolFees(models.Model):
    FEES_TYPE = (
        ("boarding", "boarding"),
        ("day", "day"),
        ("breakfast", "breakfast"),
        ("lunch", "lunch"),
        ("development", "development"),
        ("sports", "sports"),
    )
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="school_fees")
    fees_type = models.CharField(choices=FEES_TYPE, max_length=150)
    amount = models.IntegerField()
    description = models.TextField(default="No Description ...")
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = "SchoolFees"
        
    def __str__(self):
        return self.grade.grade_name
    

class TransportFee(models.Model):
    location = models.CharField(max_length=150)
    amount = models.IntegerField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)  

    def __str__(self):
        return self.location  
