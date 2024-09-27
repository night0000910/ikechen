from django.urls import path
from . import views

urlpatterns = [
    path('lp', views.view_lp),
    path('list_mentors', views.view_list_mentors)
]
