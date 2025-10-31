# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# @register.filter
# def calculate_total(marks_dict):
#     if not marks_dict:
#         return 0
#     total = 0
#     for mark in marks_dict.values():
#         try:
#             if mark and str(mark).strip():  # Check if mark is not empty or whitespace
#                 total += float(mark)
#         except (ValueError, TypeError):
#             continue
#     return round(total, 2)  # Round to 2 decimal places


@register.filter
def get_dict_value(dictionary, key):
    """Get value from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def calculate_total(marks_dict):
    """Calculate total from marks dictionary"""
    if not marks_dict:
        return 0
    return sum(float(mark) for mark in marks_dict.values() if mark and mark != '-')




@register.filter
def get_item(dictionary, key):
    """Safely gets a dictionary value by key in templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
