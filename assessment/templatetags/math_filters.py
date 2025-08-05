from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value"""
    return value - arg

@register.filter
def mul(value, arg):
    """Multiplies the value by arg"""
    return value * arg

@register.filter
def div(value, arg):
    """Divides the value by arg"""
    try:
        return value / arg
    except ZeroDivisionError:
        return 0

@register.filter
def percentage(value, arg):
    """Calculates percentage of value from arg"""
    try:
        return (value / arg) * 100
    except ZeroDivisionError:
        return 0