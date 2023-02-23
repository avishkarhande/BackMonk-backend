from django.urls import path
from . import views

urlpatterns = [
    path('', views.endpoints),
    path('api/login', views.login),
    path('api/models', views.getAllModels),
    path('api/register', views.register)
]