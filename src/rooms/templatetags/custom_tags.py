import datetime

from django import template

register = template.Library()


@register.filter
def time_left(value):
    today = datetime.datetime.now().date()
    left = value - today
    if left > datetime.timedelta(days=1):
        return f'{left.days} dni'
    return f'{left.seconds // (60 * 60)} godzin i {left.seconds % (60 * 60)} sekund'
