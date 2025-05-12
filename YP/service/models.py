from django.db import models


class Category(models.Model):
    """Категории услуг (например, парсинг товаров, новостей, объявлений)"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    """Непосредственно услуги"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='зНАЧЕНИЕ ПО УМОЛЧАНИЮ')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """Модель услуги парсинга"""
    name = models.CharField(max_length=255)  # Название услуги
    description = models.TextField()  # Подробное описание
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Категория услуги

    customer_name = models.CharField(max_length=50, default="")
    communication_method = models.CharField(max_length=50, default="")
    contact_data = models.CharField(max_length=70, default="")

    provider = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата последнего обновления

    def __str__(self):
        return self.name


class Provider(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=12, blank=True, null=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


