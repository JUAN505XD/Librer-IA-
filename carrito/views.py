from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from libros.models import Libro
from .models import Carrito, ItemCarrito

@login_required
def agregar_al_carrito(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if libro.stock <= 0:
        messages.error(request, f"El libro '{libro.titulo}' está agotado.")
        return redirect('inicio')

    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        estado='ACTIVO'
    )

    # 🛡️ Limpiar expirados antes de evaluar totales
    limpiar_items_expirados(carrito)

    total_en_carrito = sum(item.cantidad for item in carrito.items.all())
    if total_en_carrito >= 5:
        messages.warning(request, "Máximo 5 libros en total por carrito.")
        return redirect('ver_carrito')

    item, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        libro=libro,
        defaults={'precio_unitario': libro.precio, 'cantidad': 0}
    )

    if item.cantidad >= 3:
        messages.warning(request, "Máximo 3 copias del mismo libro.")
        return redirect('ver_carrito')

    with transaction.atomic():
        libro.stock -= 1
        libro.save()

        item.cantidad += 1
        item.save()

    messages.success(request, f"Agregado: {libro.titulo}")
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if carrito:
        # 🛡️ Limpiar items expirados
        limpiar_items_expirados(carrito)

        # Si después de limpiar ya no quedan elementos
        if not carrito.items.exists():
            carrito = None
            messages.info(request, "Tu tiempo de reserva expiró y el carrito está vacío.")

    return render(request, 'ver_carrito.html', {'carrito': carrito})

@login_required
def pagar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if not carrito:
        messages.error(request, "No tienes un carrito activo.")
        return redirect('ver_carrito')

    # 🛡️ ¡EL FILTRO DE SEGURIDAD CLAVE!
    # Corremos la limpieza JUSTO ANTES de procesar el pago por si el tiempo venció en pantalla
    limpiar_items_expirados(carrito)

    # Si tras la limpieza el carrito se quedó sin productos, detenemos la transacción
    if not carrito.items.exists():
        messages.error(request, "Tu reserva expiró por inactividad. No se pudo procesar el pago.")
        return redirect('ver_carrito')

    with transaction.atomic():
        carrito.estado = 'PAGADO'
        carrito.fecha_pago = timezone.now()
        carrito.save()
        
    messages.success(request, "¡Compra exitosa! Gracias por tu confianza.")
    return redirect('historial')

@login_required
def historial_compras(request):
    compras = Carrito.objects.filter(usuario=request.user, estado='PAGADO').order_by('-fecha_pago')
    return render(request, 'historial.html', {'compras': compras})

@login_required
def vaciar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if carrito:
        with transaction.atomic():
            for item in carrito.items.all():
                libro = item.libro
                libro.stock += item.cantidad
                libro.save()

            carrito.estado = 'CANCELADO'
            carrito.save()

        messages.info(request, "Carrito vaciado correctamente. Los libros volvieron al inventario.")
    else:
        messages.error(request, "No hay carrito activo para vaciar.")

    return redirect('inicio')


def limpiar_items_expirados(carrito):
    ahora = timezone.now()

    with transaction.atomic():
        for item in carrito.items.all():
            # ⏱️ Mantengo 1 minuto para tus pruebas actuales
            if ahora > item.creado_en + timedelta(minutes=1):
                
                libro = item.libro
                libro.stock += item.cantidad
                libro.save()

                item.delete()

@login_required
def sumar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    # 🛡️ Validar que el ítem que intenta alterar no haya expirado justo antes del clic
    limpiar_items_expirados(carrito)
    
    # Si el ítem ya no existe en la base de datos tras la limpieza:
    if not ItemCarrito.objects.filter(id=item_id).exists():
        messages.error(request, "El tiempo de reserva de este artículo caducó.")
        return redirect('ver_carrito')

    libro = item.libro
    if libro.stock <= 0:
        messages.error(request, "No hay más stock disponible en bodega.")
        return redirect('ver_carrito')

    with transaction.atomic():
        libro.stock -= 1
        libro.save()

        item.cantidad += 1
        item.save()

    return redirect('ver_carrito')


@login_required
def restar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    # 🛡️ Limpieza previa por consistencia de tiempos
    limpiar_items_expirados(carrito)
    
    if not ItemCarrito.objects.filter(id=item_id).exists():
        messages.error(request, "El tiempo de reserva caducó.")
        return redirect('ver_carrito')

    libro = item.libro

    with transaction.atomic():
        libro.stock += 1
        libro.save()

        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()

    return redirect('ver_carrito')
