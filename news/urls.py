from django.urls import path
from . import views

urlpatterns = [
    path('', views.all),
    path('detail/<int:news_id>/', views.detail, name='detail'),
    path('search/', views.search, name='search'),
]