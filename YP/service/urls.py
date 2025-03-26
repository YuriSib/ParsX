from django.urls import path
from .views import MainPage, get_service_list, OrderAjaxView, CategoryCreate, ServiceCreate, ServiceDetail, ServiceEdit

app_name = 'service'

urlpatterns = [
   path('', MainPage.as_view(), name='main'),
   path("create_order/", OrderAjaxView.as_view(), name="create_order"),
   path("create_category/", CategoryCreate.as_view(), name="create_category"),
   path("create_service/", ServiceCreate.as_view(), name="create_service"),
   path("edit_service/<int:pk>", ServiceEdit.as_view(), name="edit_service"),
   path('service/<int:pk>', ServiceDetail.as_view(), name='service_detail'),
   ]