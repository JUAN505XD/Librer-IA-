from django.urls import path
from . import views

urlpatterns = [
    path("inicio/", views.inicio, name="inicio"),
    path('registro/', views.registro, name='registro'),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
     path("preferencias/", views.preferencias, name="preferencias"),
     path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
     path("cambiar-password/", views.cambiar_password, name="cambiar_password"),
]