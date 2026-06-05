from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from libros.models import Libro
from .models import Carrito, ItemCarrito
from users.models import Tarjeta

@login_required
def agregar_al_carrito(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if libro.stock <= 0:
        messages.error(request, f"El libro {libro.titulo} está agotado.")
        return redirect('inicio')

    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        estado='ACTIVO'
    )

    # 🔥 limpiar items expirados antes de todo
    limpiar_items_expirados(carrito)

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
        # 🔥 limpiar SOLO items expirados
        limpiar_items_expirados(carrito)

        # 🔥 si después de limpiar ya no hay items
        if not carrito.items.exists():
            carrito = None
            messages.info(request, "Tu carrito está vacío.")

    return render(request, 'ver_carrito.html', {'carrito': carrito})

@login_required
def pagar_carrito(request):

    carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    if not carrito or not carrito.items.exists():
        messages.error(request, "No tienes productos en el carrito.")
        return redirect('ver_carrito')

    tarjetas = Tarjeta.objects.filter(usuario=request.user, activa=True)

    if request.method == "POST":

        tarjeta_id = request.POST.get("tarjeta_id")
        tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id, usuario=request.user)

        # 🔥 asegurar tipo Decimal
        total = Decimal(str(carrito.get_total()))

        # 🔥 VALIDACIÓN DE SALDO
        if tarjeta.saldo < total:
            messages.error(request, "Saldo insuficiente en la tarjeta.")
            return redirect('ver_carrito')

        with transaction.atomic():
            if tarjeta.saldo - total < 0:
                raise ValueError("Saldo negativo no permitido")

            # 🔥 DESCONTAR SALDO
            tarjeta.saldo = tarjeta.saldo - total
            tarjeta.save()

            # marcar carrito como pagado
            carrito.estado = 'PAGADO'
            carrito.fecha_pago = timezone.now()
            carrito.save()

        messages.success(request, "¡Compra realizada con éxito!")

        return redirect(
            'seguimiento_pedido',
            carrito_id=carrito.id
        )

    return render(request, "pagar_carrito.html", {
        "carrito": carrito,
        "tarjetas": tarjetas
    })

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
        messages.error(request, "No hay carrito activo.")

    return redirect('inicio')


def limpiar_items_expirados(carrito):
    ahora = timezone.now()

    with transaction.atomic():
        for item in carrito.items.all():
            if ahora > item.creado_en + timedelta(minutes=10):

                # 🔥 devolver stock
                libro = item.libro
                libro.stock += item.cantidad
                libro.save()

                # 🔥 eliminar item
                item.delete()

@login_required
def sumar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    libro = item.libro

    if libro.stock <= 0:
        messages.error(request, "No hay más stock disponible.")
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
    libro = item.libro

    with transaction.atomic():
        libro.stock += 1
        libro.save()

        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()  # 🔥 si queda en 1 → se elimina

    return redirect('ver_carrito')

@login_required
def seguimiento_pedido(request, carrito_id):

    compra = get_object_or_404(
        Carrito,
        id=carrito_id,
        usuario=request.user,
        estado="PAGADO"
    )

    minutos = (
        timezone.now() - compra.fecha_pago
    ).total_seconds() / 60

    if minutos < 1:
        estado = "📦 Preparando pedido"
        progreso = 25
        paso = 1

    elif minutos < 2:
        estado = "🚚 Pedido despachado"
        progreso = 50
        paso = 2

    elif minutos < 3:
        estado = "🛣️ En camino"
        progreso = 75
        paso = 3

    else:
        estado = "✅ Entregado"
        progreso = 100
        paso = 4

    fecha_entrega = compra.fecha_pago + timedelta(minutes=3)

    return render(
        request,
        "seguimiento_pedido.html",
        {
            "compra": compra,
            "estado": estado,
            "progreso": progreso,
            "paso": paso,
            "fecha_entrega": fecha_entrega,
        }
    )