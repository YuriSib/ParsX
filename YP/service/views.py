from django.shortcuts import render
from django.views.generic import ListView, View, CreateView, DetailView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Category, Service, Order
from .forms import OrderForm, CategoryForm, ServiceForm
from YP.logger import logger


class OrderAjaxView(View):
    def post(self, request):
        customer_name = request.POST.get('customer_name')
        communication_method = request.POST.get('communication_method')
        contact_data = request.POST.get('contact_data')
        description = request.POST.get('description')
        print(customer_name, communication_method, contact_data, description)

        if customer_name and contact_data:
            logger.warning('Внимание!')
            logger.warning('Внимание!')
            logger.warning('Внимание!')
            logger.warning(f'Посетитель {customer_name} ({contact_data}/{communication_method}) '
                           f'оставил заявку на сайте: \n{description}')
            Order.objects.create(
                name='Название по умолчанию',
                customer_name=customer_name,
                description=description,
                communication_method=communication_method,
                contact_data=contact_data,
            )
            return JsonResponse(
                data={
                    'status': 201,
                    'message': 'Вы оставили заявку, вскоре с вами свяжутся!'
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
    return render(request, 'default.html', {'services': services})


class CategoryCreate(CreateView):
    form_class = CategoryForm
    model = Category
    template_name = 'service/category_create.html'

    success_url = reverse_lazy('category_list')


class ServiceCreate(CreateView):
    form_class = ServiceForm
    model = Service
    template_name = 'service/service_create.html'

    success_url = reverse_lazy('category_list')


class ServiceDetail(DetailView):
    model = Service
    template_name = 'service/service.html'
    context_object_name = 'service'


class ServiceEdit(LoginRequiredMixin, UpdateView):
    permission_required = ('ads.change_ads',)
    form_class = ServiceForm
    model = Service
    template_name = 'service/service_edit.html'
    success_url = reverse_lazy('category_list')


def parsing_tovarov(request):
    return render(request, 'service/parsing_tovarov.html')


def sbor_bazy_klientov(request):
    return render(request, 'service/sbor_bazy_klientov.html')


def parsing_konkurentov(request):
    return render(request, 'service/parsing_konkurentov.html')


def costs(request):
    return render(request, 'service/cost.html')
