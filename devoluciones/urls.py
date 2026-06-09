from django.urls import path
from . import views

urlpatterns = [

    path("solicitar/<int:compra_id>/",views.solicitar_devolucion,name="solicitar_devolucion"),
    path("devoluciones/", views.lista_devoluciones, name="lista_devoluciones"),
    path("devoluciones/aprobar/<int:devolucion_id>/", views.aprobar_devolucion, name="aprobar_devolucion"),
    path("devoluciones/rechazar/<int:devolucion_id>/", views.rechazar_devolucion, name="rechazar_devolucion"),
    path('devolucion/item/<int:item_id>/',views.solicitar_devolucion_item,name='solicitar_devolucion_item'),
    path("mis-devoluciones/",views.mis_devoluciones, name="mis_devoluciones"),

]