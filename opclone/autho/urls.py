from django.urls import path
from . import views

urlpatterns = [
    path('search', views.index, name='index'),
    
    path('new', views.get_summoner, name ='test' )
]