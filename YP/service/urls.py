from django.urls import path
from .views import OrderAjaxView, CategoryCreate, ServiceCreate, ServiceDetail
from . import views

app_name = 'service'

urlpatterns = [
   path("create_order/", OrderAjaxView.as_view(), name="create_order"),
   path("create_category/", CategoryCreate.as_view(), name="create_category"),
   path("create_service/", ServiceCreate.as_view(), name="create_service"),
   path('service/<int:pk>', ServiceDetail.as_view(), name='service_detail'),

   path('parsing_tovarov', views.parsing_tovarov, name='parsing_tovarov'),
   path('sbor_bazy_klientov', views.sbor_bazy_klientov, name='sbor_bazy_klientov'),
   path('parsing_konkurentov', views.parsing_konkurentov, name='parsing_konkurentov'),
   ]