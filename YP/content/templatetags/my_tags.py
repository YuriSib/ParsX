from django import template
from ..models import Articles


register = template.Library()


@register.simple_tag
def get_articles():
    """Возвращает все категории услуг"""
    return Articles.objects.all()

