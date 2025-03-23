from django.urls import path
from .views import MainPage, get_service_list, OrderAjaxView, CategoryCreate, ServiceCreate


urlpatterns = [
   path('', MainPage.as_view(), name='main'),
   path("create_order/", OrderAjaxView.as_view(), name="create_order"),
   path("create_category/", CategoryCreate.as_view(), name="create_category"),
   path("service_category/", ServiceCreate.as_view(), name="create_service"),
   ]