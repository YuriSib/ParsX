from django.shortcuts import render
from django.views.generic import ListView, View
from django.http import JsonResponse

from .models import Category, Service
from .forms import OrderForm


class CategoryList(ListView):
    model = Category
    ordering = 'name'
    template_name = 'service/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter()


class OrderAjaxView(View):
    def post(self, request):
        customer_name = request.POST.get('customer_name')
        communication_method = request.POST.get('communication_method')
        contact_data = request.POST.get('contact_data')
        description = request.POST.get('description')
        print(customer_name, communication_method, contact_data, description)

        if customer_name and contact_data:
            return JsonResponse(
                data={
                    'status': 201
                },
                status=200
            )
        return JsonResponse(
            data={
                'status': 400,
                'error': 'Введите ваше имя или контактные данные!'
            },
            status=200
        )



def get_service_list(request):
    """Выводит список услуг"""
    services = Service.objects.all()  # Получаем все категории
    print('request', request)
    return render(request, 'default.html', {'services': services})



