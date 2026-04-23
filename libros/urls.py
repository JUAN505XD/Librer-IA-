from django.urls import path
from . import views

urlpatterns = [
    path("inicio/", views.inicio, name="inicio"),
    path("crear-libro/", views.crear_libro, name="crear_libro"),
]