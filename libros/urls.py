from django.urls import path
from . import views

urlpatterns = [
    path("inicio/", views.inicio, name="inicio"),
    path("crear-libro/", views.crear_libro, name="crear_libro"),
    path('buscar/', views.buscar_libros, name='buscar_libros'),
    path('libro/<int:libro_id>/', views.detalle_libro,name='detalle_libro'),
    path("crear-autor/", views.crear_autor, name="crear_autor"),
    path("crear-genero/", views.crear_genero, name="crear_genero"),
    path("crear-editorial/", views.crear_editorial, name="crear_editorial"),
    path("editar-libro/<int:libro_id>/",views.editar_libro,name="editar_libro"),
    path("eliminar-libro/<int:libro_id>/",views.eliminar_libro,name="eliminar_libro"),
]
