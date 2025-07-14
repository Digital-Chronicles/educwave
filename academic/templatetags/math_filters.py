from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='divide')
def divide(value, arg):
    """Divides the value by the arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies the value by the arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='percentage')
def percentage(value, arg):
    """Calculates percentage of value out of arg"""
    try:
        return round((float(value) / float(arg)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0