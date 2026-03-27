from django.urls import path
from . import views

urlpatterns = [
    path("inicio/", views.inicio, name="inicio"),
    path('registro/', views.registro, name='registro'),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
    path("preferencias/", views.preferencias, name="preferencias"),
    path("editar-perfil-cliente/", views.editar_perfil_cliente, name="editar_perfil_cliente"),
    path("editar-perfil-admin/", views.editar_perfil_admin, name="editar_perfil_admin"),
    path("cambiar-password/", views.cambiar_password, name="cambiar_password"),
    path("cambiar-usuario/", views.cambiar_usuario, name="cambiar_usuario"),
    path("crear-admin/", views.crear_admin, name="crear_admin"),
    path("eliminar-admin/", views.eliminar_admin, name="eliminar_admin"),
    path("eliminar-cuenta/", views.eliminar_cuenta, name="eliminar_cuenta"),
]