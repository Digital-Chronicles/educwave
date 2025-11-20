from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Avg
from .models import StudentMarkSummary
from assessment.models import ExamResult, Question

@receiver([post_save, post_delete], sender=ExamResult)
def update_mark_summary(sender, instance, **kwargs):
    """
    Update StudentMarkSummary when ExamResult is saved or deleted.
    Handles both individual questions and subject totals.
    """
    
    # Skip if we don't have the required relationships
    if not instance.exam_session or not instance.subject:
        return
    
    try:
        # For subject totals (no question), use the data directly
        if instance.question is None:
            # This is a subject total - create/update summary directly
            StudentMarkSummary.objects.update_or_create(
                student=instance.student,
                term_exam=instance.exam_session.term,  # Use exam_session.term
                subject=instance.subject,
                defaults={
                    'grade': instance.grade,
                    'exam_type': instance.exam_session.exam_type,
                    'total_score': instance.total_score or instance.score,
                    'max_possible': instance.max_possible or 100,
                    'percentage': instance.percentage or 0,
                }
            )
        
        # For individual questions, calculate aggregates
        else:
            # Get all results for this student, subject, and exam session
            results = ExamResult.objects.filter(
                student=instance.student,
                subject=instance.subject,
                exam_session=instance.exam_session,
                question__isnull=False  # Only include individual questions
            )
            
            # Calculate totals
            total_score = results.aggregate(total=Sum('score'))['total'] or 0
            max_possible = results.aggregate(total=Sum('question__max_score'))['total'] or 0
            percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
            
            # Get or create the summary
            StudentMarkSummary.objects.update_or_create(
                student=instance.student,
                term_exam=instance.exam_session.term,  # Use exam_session.term instead of question.term_exam
                subject=instance.subject,
                defaults={
                    'grade': instance.grade,
                    'exam_type': instance.exam_session.exam_type,
                    'total_score': total_score,
                    'max_possible': max_possible,
                    'percentage': round(percentage, 2)
                }
            )
        
        # Calculate class averages and positions
        update_class_statistics(instance.exam_session.term, instance.subject)
        
    except Exception as e:
        # Log the error but don't crash
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating mark summary for student {instance.student}: {str(e)}")

def update_class_statistics(term_exam, subject):
    """Update class averages and positions for a subject and term"""
    try:
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
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating class statistics: {str(e)}")