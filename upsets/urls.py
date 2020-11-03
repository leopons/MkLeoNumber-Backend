from django.urls import path
from upsets import views

urlpatterns = [
    path('playerpath/<str:id>/', views.UpsetPath.as_view()),
]
