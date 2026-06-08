from django.db import models
from carrito.models import Carrito
from users.models import Usuario


class Devolucion(models.Model):

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]

    MOTIVOS = [
        ("DEFECTUOSO", "Libro defectuoso o dañado"),
        ("EQUIVOCADO", "Recibí un libro incorrecto"),
        ("INCOMPLETO", "Libro incompleto"),
        ("ARREPENTIMIENTO", "Ya no deseo el producto"),
        ("OTRO", "Otro motivo"),
    ]

    compra = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    motivo = models.CharField(max_length=30, choices=MOTIVOS)

    descripcion = models.TextField(blank=True, null=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")

    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Devolución #{self.id}"
    

class DevolucionItem(models.Model):

    devolucion = models.ForeignKey(
        Devolucion,
        on_delete=models.CASCADE,
        related_name="items"
    )

    item = models.ForeignKey(
        "carrito.ItemCarrito",
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.libro.titulo}"