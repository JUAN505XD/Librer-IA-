from django.db import models

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
        on_delete=models.PROTECT  # 🔥 evita borrar autor si tiene libros
    )

    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT  # 🔥 mismo para género
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
