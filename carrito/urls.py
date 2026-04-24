from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:libro_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('pagar/', views.pagar_carrito, name='pagar_carrito'),
    path('historial/', views.historial_compras, name='historial'),
]
