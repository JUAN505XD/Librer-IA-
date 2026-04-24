from django.db import models
import requests
import os
from django.conf import settings

# Create your models here.
class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Idioma(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
    
class Libro(models.Model):
    titulo = models.CharField(max_length=200)

    stock = models.PositiveIntegerField(default=10)

    ESTADO_CHOICES = [
        ('NUEVO', 'Nuevo'),
        ('USADO', 'Usado'),
    ]

    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT
    )

    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT
    )

    numero_paginas = models.IntegerField()

    editorial = models.CharField(max_length=150)
    issn = models.CharField(max_length=50, unique=True)

    idioma = models.ForeignKey(
        Idioma,
        on_delete=models.PROTECT
    )

    fecha_publicacion = models.DateField()

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES
    )

    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.titulo

    # 🔥 NUEVO: descarga automática de portada
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.issn:
            try:
                url = f"https://covers.openlibrary.org/b/isbn/{self.issn}-L.jpg"

                ruta = os.path.join(settings.BASE_DIR, "static/assets/portadas/")
                os.makedirs(ruta, exist_ok=True)

                ruta_imagen = os.path.join(ruta, f"{self.issn}.jpg")

                # 🔒 evita descargar si ya existe
                if not os.path.exists(ruta_imagen):
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200 and response.content:
                        with open(ruta_imagen, "wb") as f:
                            f.write(response.content)

            except Exception as e:
                # ⚠️ nunca romper el guardado por esto
                print(f"Error descargando portada: {e}")
