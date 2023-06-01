from django.urls import path
from . import views

urlpatterns = [
    path('', views.endpoints),
    path('api/login', views.login),
    path('api/models', views.getAllModels),
    path('api/register', views.register),
    path('api/model_generate', views.Model_generator),
    path('api/user_models', views.user_models),
    path('api/update_model', views.update_model),
    path('api/delete_model', views.delete_model),
    path('api/get_model', views.getModelById)
]
