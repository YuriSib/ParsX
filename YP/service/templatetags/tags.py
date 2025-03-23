from django import template
from service.models import Service, Category


register = template.Library()


@register.simple_tag
def get_categories():
    """Возвращает все категории услуг"""
    return Category.objects.all()


@register.simple_tag
def get_services():
    """Возвращает все услуги"""
    return Service.objects.all()
