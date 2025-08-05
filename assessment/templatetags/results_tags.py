from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Get dictionary item by key"""
    return dictionary.get(key)

@register.simple_tag
def calculate_total(student, questions, existing_results):
    """Calculate total score for a student"""
    total = 0
    for question in questions:
        score = existing_results.get((student.id, question.id), 0)
        total += score
    return total if total > 0 else '-'