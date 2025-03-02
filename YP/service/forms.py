from django import forms
from .models import Order


COMMUNICATION_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Телефон'),
    ('telegram', 'Telegram'),
]


class OrderForm(forms.ModelForm):
    communication_method = forms.ChoiceField(
        choices=COMMUNICATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Способ связи"
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'communication_method', 'contact_data', 'description']
        labels = {
            'customer_name': 'Имя',
            'communication_method': 'Способ связи',
            'contact_data': 'Контактные данные',
            'description': 'Описание задачи',
        }