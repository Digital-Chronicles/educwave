from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Safely get a dictionary value by key in templates."""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return []
