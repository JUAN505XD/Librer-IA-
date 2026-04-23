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
        messages.error(request, f"El libro {libro.titulo} está agotado.")
        return redirect('inicio')

    carrito, created = Carrito.objects.get_or_create(usuario=request.user, estado='ACTIVO')

    if not created and carrito.es_antiguo():
        carrito.estado = 'CANCELADO'
        carrito.save()
        carrito = Carrito.objects.create(usuario=request.user, estado='ACTIVO')

    total_en_carrito = sum(item.cantidad for item in carrito.items.all())
    if total_en_carrito >= 5:
        messages.warning(request, "Máximo 5 libros por carrito.")
        return redirect('ver_carrito')

    item, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        libro=libro,
        defaults={'precio_unitario': libro.precio, 'cantidad': 0}
    )

    if item.cantidad >= 3:
        messages.warning(request, "Máximo 3 copias del mismo libro.")
        return redirect('ver_carrito')

    # 🔥 CLAVE: operación atómica
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
    
    # Cleanup if they just open an old cart
    if carrito and carrito.es_antiguo():
        carrito.estado = 'CANCELADO'
        carrito.save()
        carrito = None
        messages.info(request, "Tu carrito anterior expiró (24h de inactividad).")

    return render(request, 'ver_carrito.html', {'carrito': carrito})

@login_required
def pagar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if not carrito or not carrito.items.exists():
        return redirect('ver_carrito')

    carrito.estado = 'PAGADO'
    carrito.save()

    messages.success(request, "¡Compra exitosa!")
    return redirect('historial_compras')

@login_required
def historial_compras(request):
    compras = Carrito.objects.filter(usuario=request.user, estado='PAGADO').order_by('-actualizado_en')
    return render(request, 'carrito/historial.html', {'compras': compras})

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
        messages.error(request, "No hay carrito activo.")

    return redirect('inicio')
