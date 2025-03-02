from django import template
from service.models import Service


register = template.Library()


@register.simple_tag
def get_services(category_id):
    """Возвращает все услуги"""
    return Service.objects.filter(category_id=category_id)
