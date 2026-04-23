from django.urls import path
from . import views

urlpatterns = [
    path("crear-libro/", views.crear_libro, name="crear_libro"),
]