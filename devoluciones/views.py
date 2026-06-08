from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from carrito.models import Carrito
from .models import Devolucion, DevolucionItem
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from carrito.models import ItemCarrito
from users.models import Tarjeta
from django.http import HttpResponseForbidden

def es_admin(usuario):
    return (
        usuario.is_authenticated
        and usuario.rol in ["ADMIN", "ROOT"]
    )


@login_required
def solicitar_devolucion(request, compra_id):

    compra = get_object_or_404(
        Carrito,
        id=compra_id,
        usuario=request.user,
        estado="PAGADO"
    )

    if Devolucion.objects.filter(compra=compra).exists():
        messages.error(
            request,
            "Ya existe una solicitud de devolución para esta compra."
        )
        return redirect("historial")

    if request.method == "POST":

        motivo = request.POST.get("motivo")
        descripcion = request.POST.get("descripcion")

        Devolucion.objects.create(
            compra=compra,
            usuario=request.user,
            motivo=motivo,
            descripcion=descripcion
        )

        messages.success(
            request,
            "Solicitud de devolución enviada correctamente."
        )

        return redirect("historial")

    return render(
        request,
        "solicitar_devolucion.html",
        {
            "compra": compra
        }
    )

@login_required
def lista_devoluciones(request):

    if not es_admin(request.user):
        return HttpResponseForbidden("No tienes permisos para acceder aquí")

    devoluciones = Devolucion.objects.all().order_by("-fecha_solicitud")

    return render(
        request,
        "admin_devoluciones.html",
        {
            "devoluciones": devoluciones
        }
    )

@login_required
def aprobar_devolucion(request, devolucion_id):

    devolucion = get_object_or_404(
        Devolucion,
        id=devolucion_id
    )

    if devolucion.estado != "PENDIENTE":
        messages.warning(
            request,
            "Esta devolución ya fue procesada."
        )
        return redirect("lista_devoluciones")

    with transaction.atomic():
        carrito = devolucion.compra

        tarjeta = carrito.tarjeta_pago

        # ==================================
        # DEVOLUCIÓN DE ITEM INDIVIDUAL
        # ==================================
        if devolucion.items.exists():

            total_devolver = 0

            for devolucion_item in devolucion.items.all():

                item = devolucion_item.item

                # dinero
                total_devolver += (
                    item.precio_unitario
                    * devolucion_item.cantidad
                )

                # stock
                libro = item.libro
                libro.stock += devolucion_item.cantidad
                libro.save()

            if tarjeta:
                tarjeta.saldo += total_devolver
                tarjeta.save()

        # ==================================
        # DEVOLUCIÓN DE COMPRA COMPLETA
        # ==================================
        else:


            if tarjeta:
                tarjeta.saldo += carrito.get_total()
                tarjeta.save()

            for item in carrito.items.all():

                libro = item.libro
                libro.stock += item.cantidad
                libro.save()

        devolucion.estado = "APROBADA"
        devolucion.fecha_respuesta = timezone.now()
        devolucion.save()

    messages.success(
        request,
        "Devolución aprobada correctamente."
    )

    return redirect("lista_devoluciones")

@login_required
def rechazar_devolucion(request, devolucion_id):

    devolucion = get_object_or_404(Devolucion, id=devolucion_id)

    if devolucion.estado != "PENDIENTE":
        messages.warning(request, "Esta devolución ya fue procesada.")
        return redirect("lista_devoluciones")

    devolucion.estado = "RECHAZADA"
    devolucion.fecha_respuesta = timezone.now()
    devolucion.save()

    messages.error(request, "Devolución rechazada.")
    return redirect("lista_devoluciones")

@login_required
def solicitar_devolucion_item(request, item_id):

    item = get_object_or_404(
        ItemCarrito,
        id=item_id,
        carrito__usuario=request.user
    )

    if request.method == "POST":

        motivo = request.POST.get("motivo")
        descripcion = request.POST.get("descripcion")

        try:
            cantidad = int(
                request.POST.get("cantidad")
            )
        except (TypeError, ValueError):

            messages.error(
                request,
                "Cantidad inválida."
            )

            return redirect(
                "solicitar_devolucion_item",
                item_id=item.id
            )

        if cantidad < 1 or cantidad > item.cantidad:

            messages.error(
                request,
                "La cantidad seleccionada no es válida."
            )

            return redirect(
                "solicitar_devolucion_item",
                item_id=item.id
            )

        devolucion = Devolucion.objects.create(
            compra=item.carrito,
            usuario=request.user,
            motivo=motivo,
            descripcion=descripcion
        )

        DevolucionItem.objects.create(
            devolucion=devolucion,
            item=item,
            cantidad=cantidad
        )

        messages.success(
            request,
            "Solicitud enviada correctamente."
        )

        return redirect("historial")

    return render(
        request,
        "solicitar_devolucion_item.html",
        {
            "item": item
        }
    )

@login_required
def mis_devoluciones(request):

    devoluciones = (
        Devolucion.objects
        .filter(usuario=request.user)
        .order_by("-fecha_solicitud")
    )

    return render(
        request,
        "mis_devoluciones.html",
        {
            "devoluciones": devoluciones
        }
    )
