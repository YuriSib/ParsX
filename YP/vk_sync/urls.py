from django.urls import path
from .views import VkAcceptCodeView, start_vk_login, login_page, CheckAuthorizationCodeAPIView, VkUpdaterAPIView
from django.views.generic import TemplateView


urlpatterns = [
    path('accept_requests/', VkAcceptCodeView.as_view(), name='accept_requests'),
    path('', login_page, name='login_page'),
    path('vk_login/', start_vk_login, name='vk_login'),
    path('api/integrations/', CheckAuthorizationCodeAPIView.as_view(), name='integrations-list'),
    path('api/update_products/', VkUpdaterAPIView.as_view(), name='updater'),
   ]