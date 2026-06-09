from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from devoluciones.models import Devolucion, DevolucionItem
from libros.models import Libro
from .models import Carrito, ItemCarrito
from users.models import Tarjeta
from users.models import CuponCumpleanos
from django.http import JsonResponse
from users.models import CuponCumpleanos
from decimal import Decimal

# ⏱️ CONFIGURACIÓN UNIVERSAL: Cambia a 1440 cuando pases a producción (24 horas)
SEGUNDOS_EXPIRACION = 30

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

    if carrito.estado != 'ACTIVO':
        carrito = Carrito.objects.create(
                usuario=request.user,
                estado='ACTIVO'
                )

    item, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        libro=libro,
        defaults={'precio_unitario': libro.precio, 'cantidad': 0}
    )

    libros_diferentes = carrito.items.count()

    if item_created and libros_diferentes  > 5:
        item.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'warning', 'message': "Máximo 5 libros diferentes"})
        return redirect('ver_carrito')

    if item.cantidad >= 3:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'warning', 'message': "No se pueden agregar más de 3 copias por libro"})
        return redirect('ver_carrito')

    with transaction.atomic():
        libro.stock -= 1
        libro.save()

        item.cantidad += 1
        item.save()
        
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

    if carrito:
        limpiar_items_expirados(carrito)

        carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()

    return render(request, 'ver_carrito.html', {
        'carrito': carrito,
    })

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
        
        codigo_cupon = request.POST.get(
            "codigo_cupon"
        )

        descuento = Decimal("0")

        if codigo_cupon:

            cupon = CuponCumpleanos.objects.filter(
                codigo=codigo_cupon,
                usuario=request.user,
                usado=False
            ).first()

            if cupon and cupon.vigente():

                descuento = (
                    total *
                    Decimal(cupon.descuento)
                    / Decimal("100")
                )

                total -= descuento

            else:

                messages.error(
                    request,
                    "Cupón inválido o vencido"
                )

                return redirect("pagar_carrito")

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

            # 🔥 guardar tarjeta utilizada
            carrito.tarjeta_pago = tarjeta

            carrito.save()

            if codigo_cupon and cupon:

                cupon.usado = True
                cupon.save()

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

    compras = Carrito.objects.filter(
        usuario=request.user,
        estado='PAGADO'
    ).order_by('-fecha_pago')

    # SOLO devoluciones completas
    carritos_con_devolucion_total = set(
        Devolucion.objects.filter(
            usuario=request.user,
            items__isnull=True
        ).values_list(
            'compra_id',
            flat=True
        )
    )

    # ITEMS con devolución parcial
    items_con_devolucion = set(
        DevolucionItem.objects.filter(
            item__carrito__usuario=request.user
        ).values_list(
            'item_id',
            flat=True
        )
    )

    # CARRITOS que tienen cualquier devolución
    # (total o parcial)
    carritos_con_cualquier_devolucion = set(
        Devolucion.objects.filter(
            usuario=request.user
        ).values_list(
            'compra_id',
            flat=True
        )
    )

    return render(
        request,
        'historial.html',
        {
            'compras': compras,
            'carritos_con_devolucion_total': carritos_con_devolucion_total,
            'items_con_devolucion': items_con_devolucion,
            'carritos_con_cualquier_devolucion': carritos_con_cualquier_devolucion,
        }
    )
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

    return redirect('ver_carrito')


def limpiar_items_expirados(carrito):
    if not carrito.items.exists():
        return

    ahora = timezone.now()

    # ⏱️ VALIDACIÓN UNIVERSAL: Compara el carrito completo
    if ahora > carrito.actualizado_en + timedelta(seconds=SEGUNDOS_EXPIRACION):
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
def restar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    limpiar_items_expirados(carrito)
    
    libro = item.libro

    if carrito.items.count() == 1 and item.cantidad == 1:
        return redirect('vaciar_carrito')

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

@login_required
def validar_cupon(request):

    codigo = request.GET.get("codigo", "").strip()

    carrito = Carrito.objects.filter(
        usuario=request.user,
        estado="ACTIVO"
    ).first()

    if not carrito:
        return JsonResponse({
            "valido": False,
            "mensaje": "No existe carrito activo"
        })

    cupon = CuponCumpleanos.objects.filter(
        codigo=codigo,
        usuario=request.user,
        usado=False
    ).first()

    if not cupon:
        return JsonResponse({
            "valido": False,
            "mensaje": "Cupón no encontrado"
        })

    if not cupon.vigente():
        return JsonResponse({
            "valido": False,
            "mensaje": "Cupón vencido"
        })

    total = Decimal(str(carrito.get_total()))

    descuento = (
        total *
        Decimal(cupon.descuento)
        / Decimal("100")
    )

    nuevo_total = total - descuento

    return JsonResponse({
        "valido": True,
        "descuento": float(descuento),
        "porcentaje": cupon.descuento,
        "nuevo_total": float(nuevo_total)
    })
