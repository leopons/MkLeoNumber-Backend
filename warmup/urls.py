from django.urls import path

from . import views

urlpatterns = [
    path('', views.appengine_warmup, name='appengine_warmup'),
]
