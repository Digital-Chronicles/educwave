from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def sum_payments(transactions):
    return sum(t.amount_paid for t in transactions)