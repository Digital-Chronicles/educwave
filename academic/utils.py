# # academic/utils.py
# from django.db.models import Sum

# from academic.models import StudentMarkSummary
# from assessment.models import ExamResult


# def update_student_mark_summary(student_id, term_exam_id, exam_session_id):
#     results = ExamResult.objects.filter(
#         student_id=student_id,
#         topic__subject__exam_sessions__id=exam_session_id,
#         grade__mark_summaries__term_exam_id=term_exam_id,
#     )

#     subjects = results.values('subject').distinct()
#     for s in subjects:
#         subject_results = results.filter(subject_id=s['subject'])
#         total_score = subject_results.aggregate(Sum('score'))['score__sum'] or 0
#         max_score = subject_results.aggregate(Sum('question__max_score'))['question__max_score__sum'] or 0
#         percentage = (total_score / max_score * 100) if max_score else 0

#         StudentMarkSummary.objects.update_or_create(
#             student_id=student_id,
#             term_exam_id=term_exam_id,
#             subject_id=s['subject'],
#             defaults={
#                 'exam_type_id': exam_session_id,
#                 'grade': subject_results.first().grade,
#                 'total_score': total_score,
#                 'max_possible': max_score,
#                 'percentage': percentage,
#             }
#         )
