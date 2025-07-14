from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Avg
from .models import StudentMarkSummary
from assessment.models import ExamResult, Question

@receiver([post_save, post_delete], sender=ExamResult)
def update_mark_summary(sender, instance, **kwargs):
    # Get all results for this student, subject, and term exam
    results = ExamResult.objects.filter(
        student=instance.student,
        subject=instance.subject,
        question__term_exam=instance.question.term_exam
    )
    
    # Calculate totals
    total_score = results.aggregate(total=Sum('score'))['total'] or 0
    max_possible = results.aggregate(total=Sum('question__max_score'))['total'] or 0
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    # Get or create the summary
    summary, created = StudentMarkSummary.objects.update_or_create(
        student=instance.student,
        term_exam=instance.question.term_exam,
        subject=instance.subject,
        grade=instance.grade,
        defaults={
            'total_score': total_score,
            'max_possible': max_possible,
            'percentage': round(percentage, 2)
        }
    )
    
    # Calculate class averages and positions (can be done periodically if performance is concern)
    update_class_statistics(instance.question.term_exam, instance.subject)

def update_class_statistics(term_exam, subject):
    # Get all summaries for this subject and term
    summaries = StudentMarkSummary.objects.filter(
        term_exam=term_exam,
        subject=subject
    )
    
    # Calculate class average
    class_avg = summaries.aggregate(avg=Avg('percentage'))['avg'] or 0
    
    # Update all summaries with class average
    summaries.update(class_average=round(class_avg, 2))
    
    # Calculate and update positions
    ordered_summaries = summaries.order_by('-percentage')
    for index, summary in enumerate(ordered_summaries, start=1):
        summary.subject_position = index
        summary.save()