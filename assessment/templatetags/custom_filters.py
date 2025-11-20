from django import template
register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Safely get a dictionary item or return None if missing."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None




register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using key"""
    return dictionary.get(key, {})

@register.filter
def get_nested_item(dictionary, keys):
    """Get nested item from dictionary using tuple key"""
    if isinstance(keys, tuple):
        return dictionary.get(keys[0], {}).get(keys[1], "")
    return ""