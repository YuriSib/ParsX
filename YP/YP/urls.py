"""
URL configuration for YP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('communication', include('communication.urls')),
    # path('content', include('content.urls')),
    path('service/', include('service.urls')),
    path('', include('core.urls')),
    path('vk_login/', include('vk_sync.urls')),

    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('blog/', include('content.urls')),
    path('accept_requests/', TemplateView.as_view(template_name='flatpages/accept_requests.html'), name='accept_requests'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)