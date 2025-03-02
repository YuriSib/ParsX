from django.urls import path
from .views import MainCategoryListView


app_name = 'communication'

urlpatterns = [
   path('', MainCategoryListView.as_view()),
]
