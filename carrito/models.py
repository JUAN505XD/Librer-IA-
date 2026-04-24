from django.db import models
from django.conf import settings
from libros.models import Libro
from django.utils import timezone
from datetime import timedelta

class Carrito(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True) # <--- Tracks the 24h action window
    fecha_pago = models.DateTimeField(null=True, blank=True)

    def es_antiguo(self):
        # Checks if 24 hours have passed since the last update
        return timezone.now() > self.actualizado_en + timedelta(hours=24)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    creado_en = models.DateTimeField(auto_now_add=True)  # 🔥 CLAVE

    def get_subtotal(self):
        return self.cantidad * self.precio_unitario
