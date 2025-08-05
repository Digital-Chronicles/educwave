from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get dictionary item with default empty dict if not found"""
    return dictionary.get(key, {})

@register.filter
def avg_value(iterable, attr):
    """Calculate average of an attribute in a list of dictionaries"""
    try:
        values = [float(item[attr]) for item in iterable if attr in item]
        return sum(values) / len(values) if values else 0
    except (TypeError, ValueError, AttributeError):
        return 0

@register.filter
def student_avg_score(students, question_id):
    """Calculate average score for a specific question across students"""
    total = 0
    count = 0
    for student in students:
        result = student.filtered_results.filter(question_id=question_id).first()
        if result:
            total += result.score
            count += 1
    return total / count if count else 0

@register.filter
def group_by_topic(questions):
    """Group questions by their topic"""
    from collections import defaultdict
    grouped = defaultdict(list)
    for question in questions:
        grouped[question.topic].append(question)
    return grouped.items()

@register.filter
def percentage(score, max_score):
    """Calculate percentage safely"""
    if max_score == 0:
        return 0
    return (score / max_score) * 100

@register.filter
def divide(value, divisor):
    """Safe division filter"""
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, multiplier):
    """Safe multiplication filter"""
    try:
        return float(value) * float(multiplier)
    except ValueError:
        return 0

@register.simple_tag
def calculate_dashoffset(circumference, percentage):
    """Calculates the dashoffset for circular progress indicators"""
    return circumference - (circumference * percentage / 100)

@register.filter
def score_class(score, max_score):
    """Returns the appropriate CSS class based on score percentage"""
    if max_score == 0:
        return "bg-gray-100 text-gray-800"
    
    percentage = (score / max_score) * 100
    if percentage >= 80:
        return "bg-green-100 text-green-800"
    elif percentage >= 50:
        return "bg-yellow-100 text-yellow-800"
    return "bg-red-100 text-red-800"