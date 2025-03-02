from django.shortcuts import render
from django.views.generic import ListView

from .models import Messages


class MainCategoryListView(ListView):
    model = Messages

    ordering = 'username'
    # template_name = 'service/service.html'
