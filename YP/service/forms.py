from django import forms
from django.utils.translation import gettext_lazy


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
                "autocomplete": "phone",
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