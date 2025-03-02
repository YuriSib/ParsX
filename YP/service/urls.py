from django.urls import path
from .views import CategoryList, get_service_list, profile_view, send_feedback


app_name = 'service'

urlpatterns = [
   path('', CategoryList.as_view(), name='category_list'),
   path('', get_service_list, name='service_list'),
   path('order/', profile_view, name='profile'),

   path("send-feedback/", send_feedback, name="send_feedback"),
   ]