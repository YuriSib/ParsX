from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
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


def get_service_list(request):
    """Выводит список услуг"""
    services = Service.objects.all()  # Получаем все категории
    print('request', request)
    return render(request, 'default.html', {'services': services})


def profile_view(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        form.save()
        return HttpResponseRedirect('/')
    form = OrderForm()
    return render(request, 'service/order.html', {'form': form})


@csrf_exempt  # Временно отключаем CSRF (небезопасно для продакшена)
def send_feedback(request):
    print("Метод запроса:", request.method)  # Логируем метод
    print("POST-данные:", request.POST)  # Логируем содержимое POST

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        # Можно сохранить данные в БД, отправить email и т. д.

        return JsonResponse({"message": f"Спасибо, {name}! Ваш отзыв отправлен."})

    return JsonResponse({"error": "Некорректный запрос"}, status=400)
