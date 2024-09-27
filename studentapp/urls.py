from django.urls import path
from . import views

urlpatterns = [
    path('lp', views.view_lp)
]
