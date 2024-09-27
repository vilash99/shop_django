from django import template

register = template.Library()

@register.filter
def first_word(value):
    """Returns the first word of a string."""
    if value:
        return value.split()[0]
    return ""
