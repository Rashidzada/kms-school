import calendar
from django import template

register = template.Library()

@register.filter(name="month_name")
def month_name(value):
    """
    Converts a month number (1-12) or string into its full English name.
    Example: 1 -> 'January', 9 -> 'September'
    """
    try:
        m = int(value)
        if 1 <= m <= 12:
            return calendar.month_name[m]
    except (ValueError, TypeError, IndexError):
        pass
    return value

@register.filter(name="month_abbr")
def month_abbr(value):
    """
    Converts a month number (1-12) or string into its 3-letter abbreviation.
    Example: 1 -> 'Jan', 9 -> 'Sep'
    """
    try:
        m = int(value)
        if 1 <= m <= 12:
            return calendar.month_abbr[m]
    except (ValueError, TypeError, IndexError):
        pass
    return value
