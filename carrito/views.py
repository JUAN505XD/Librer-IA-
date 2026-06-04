from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from libros.models import Libro
from .models import Carrito, ItemCarrito

# ⏱️ CONFIGURACIÓN UNIVERSAL: Cambia a 1440 cuando pases a producción (24 horas)
MINUTOS_EXPIRACION = 1  

@login_required
def agregar_al_carrito(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if libro.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': f"El libro '{libro.titulo}' está agotado."})
        return redirect('inicio')

    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        estado='ACTIVO'
    )

    # 🛡️ Ejecutar limpieza previa antes de validar topes
    limpiar_items_expirados(carrito)
   
    total_en_carrito = sum(item.cantidad for item in carrito.items.all())
    if total_en_carrito >= 5:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'warning', 'message': "Máximo 5 libros en total por carrito."})
        return redirect('ver_carrito')

    item, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        libro=libro,
        defaults={'precio_unitario': libro.precio, 'cantidad': 0}
    )

    if item.cantidad >= 3:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'warning', 'message': "Máximo 3 copias del mismo libro."})
        return redirect('ver_carrito')

    with transaction.atomic():
        libro.stock -= 1
        libro.save()

        item.cantidad += 1
        item.save()
        
        # 🔥 RENOVAR EL TEMPORIZADOR UNIVERSAL:
        # Cada vez que agregamos un libro, actualizamos la fecha del carrito a "ahora mismo"
        # Esto le regala al usuario tiempo extra para TODO su carrito.
        carrito.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        nuevo_total = sum(i.cantidad for i in carrito.items.all())
        return JsonResponse({
            'status': 'success',
            'message': f"Agregado: {libro.titulo}",
            'nuevo_total': nuevo_total
            })

    messages.success(request, f"Agregado: {libro.titulo}")
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()
    segundos_restantes_global = 0

    if carrito:
        limpiar_items_expirados(carrito)
        
        # Volvemos a verificar si sobrevivió a la limpieza
        carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()
        
        if carrito and carrito.items.exists():
            # 🔄 Si no tiene una fecha base de interacción inicial, se la asignamos
            if not carrito.actualizado_en:
                carrito.actualizado_en = carrito.items.first().creado_en
                carrito.save()

            ahora = timezone.now()
            # El tiempo límite universal se calcula desde la última interacción general del carrito
            limite_tiempo = carrito.actualizado_en + timedelta(minutes=MINUTOS_EXPIRACION)
            segundos_restantes_global = int((limite_tiempo - ahora).total_seconds())
            
            if segundos_restantes_global < 0:
                segundos_restantes_global = 0
        else:
            carrito = None

    return render(request, 'ver_carrito.html', {
        'carrito': carrito,
        'segundos_restantes_global': segundos_restantes_global
    })

@login_required
def pagar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if not carrito:
        messages.error(request, "No tienes un carrito activo.")
        return redirect('ver_carrito')

    limpiar_items_expirados(carrito)

    if not carrito.items.exists():
        messages.error(request, "Tu tiempo de reserva universal expiró. El carrito fue liberado.")
        return redirect('ver_carrito')

    with transaction.atomic():
        carrito.estado = 'PAGADO'
        carrito.fecha_pago = timezone.now() # Fecha definitiva de compra
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

        messages.info(request, "Carrito vaciado correctamente.")
    else:
        messages.error(request, "No hay carrito activo para vaciar.")

    return redirect('inicio')


def limpiar_items_expirados(carrito):
    if not carrito.items.exists():
        return

    ahora = timezone.now()

    # ⏱️ VALIDACIÓN UNIVERSAL: Compara el carrito completo
    if ahora > carrito.actualizado_en + timedelta(minutes=MINUTOS_EXPIRACION):
        with transaction.atomic():
            for item in carrito.items.all():
                libro = item.libro
                libro.stock += item.cantidad
                libro.save()
                item.delete()
            
            # Cambiamos el estado para romper el ciclo activo
            carrito.estado = 'CANCELADO'
            carrito.save()

@login_required
def sumar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    limpiar_items_expirados(carrito)
    
    if not ItemCarrito.objects.filter(id=item_id).exists():
        messages.error(request, "La reserva de este artículo caducó.")
        return redirect('ver_carrito')

    libro = item.libro
    if libro.stock <= 0:
        messages.error(request, "No hay más stock disponible.")
        return redirect('ver_carrito')

    with transaction.atomic():
        libro.stock -= 1
        libro.save()

        item.cantidad += 1
        item.save()
        
        # 🔄 Renovación del tiempo al modificar cantidades
        carrito.save()

    return redirect('ver_carrito')


@login_required
def restar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    limpiar_items_expirados(carrito)
    
    if not ItemCarrito.objects.filter(id=item_id).exists():
        messages.error(request, "La reserva caducó.")
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
            
        # 🔄 Renovación del tiempo al modificar cantidades
        carrito.save()

    return redirect('ver_carrito')
