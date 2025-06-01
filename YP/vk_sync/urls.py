from django.urls import path
from .views import VkAcceptCodeView, start_vk_login, login_page, IntegrationsListCreateAPIView
from django.views.generic import TemplateView


urlpatterns = [
    path('accept_requests/', VkAcceptCodeView.as_view(), name='accept_requests'),
    path('', login_page, name='login_page'),
    path('vk_login/', start_vk_login, name='vk_login'),
    path('api/articles/', IntegrationsListCreateAPIView.as_view(), name='integrations-list'),
   ]