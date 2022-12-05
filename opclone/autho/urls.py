from django.urls import path
from . import views

urlpatterns = [
    path('search', views.index, name='index'),
    path('data', views.ritoAPI, name = 'ApiCode'),
    path('new', views.get_summoner, name ='test' )
]