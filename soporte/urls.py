from django.urls import path
from . import views

urlpatterns = [
    path("Soporte/", views.mis_consultas, name="mis_temas"),
    path("Soporte/crear/",views.crear_consulta,name="crear_tema"),
    path("Soporte/<int:tema_id>/",views.ver_consulta,name="ver_tema"),
    path("Soporte/admin/",views.lista_consultas_admin,name="lista_temas_admin"),
    path("Soporte/cerrar/<int:tema_id>/",views.cerrar_consulta,name="cerrar_tema"),
]