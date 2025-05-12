from django.shortcuts import render, get_object_or_404
from .models import Articles


def page_detail(request, slug):
    page = get_object_or_404(Articles, slug=slug)
    return render(request, 'blog/blog_page.html', {'page': page})


def article_list(request):
    articles = Articles.objects.all()
    return render(request, 'flatpages/navbar.html', {'articles': articles})