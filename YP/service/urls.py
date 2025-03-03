from django.urls import path
from .views import CategoryList, get_service_list, OrderAjaxView


urlpatterns = [
   path('', CategoryList.as_view(), name='category_list'),
   path('', get_service_list, name='service_list'),

   path("create_order/", OrderAjaxView.as_view(), name="create_order"),
   ]