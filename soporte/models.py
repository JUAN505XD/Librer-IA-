from django.db import models
from users.models import Usuario


class TemaSoporte(models.Model):

    ESTADOS = [
        ("ABIERTO", "Abierto"),
        ("CERRADO", "Cerrado"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="temas_soporte"
    )

    titulo = models.CharField(
        max_length=200
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="ABIERTO"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.titulo


class MensajeSoporte(models.Model):

    tema = models.ForeignKey(
        TemaSoporte,
        on_delete=models.CASCADE,
        related_name="mensajes"
    )

    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    mensaje = models.TextField()

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.autor} - {self.tema}"
