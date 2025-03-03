from django.urls import path, include

from .views import LoginAjaxView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    # path('login_ajax/', LoginAjaxView.as_view(), name='login_ajax')
]