from django import forms
from django.utils.translation import gettext_lazy
from .models import Category, Service


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'time_create': forms.DateInput(attrs={'type': 'date'}),
        }


class ServiceForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Выберите категорию",
        label="Категория",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Service
        fields = ['name', 'description', 'category']
        labels = {
            'name': 'Название услуги',
            'description': 'Описание',
            'category_id': 'Категория'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OrderForm(forms.Form):
    customer_name = forms.CharField(
        label=gettext_lazy("Имя"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'name',  # подсказка браузеру для автозаполнения
                'class': 'form-control',  # добавляем Bootstrap в поле
            }
        )
    )
    communication_method = forms.ChoiceField(  # Выпадающий список
        label=gettext_lazy("Выберите средство связи"),
        choices=[
            ('phone_number', 'По телефону'),
            ('telegram', 'Telegram'),
            ('whatsapp', 'WhatsApp'),
            ('email', 'E-mail'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contact_data = forms.CharField(
        label=gettext_lazy("Контактные данные"),
        strip=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "tel",
                'class': 'form-control',
                'placeholder': 'Ваши контактные данные',
            }),
    )
    description = forms.CharField(
        label=gettext_lazy("Описание задачи"),
        strip=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5,  # определяем количество строк
                'placeholder': 'Опишите вашу задачу...',
            }),
    )