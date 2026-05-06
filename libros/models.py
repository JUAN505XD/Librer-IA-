from django.db import models
import requests
import os
from pathlib import Path
from django.conf import settings
from django.core.validators import MaxValueValidator

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

    numero_paginas = models.IntegerField(validators=[MaxValueValidator(2000)])

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

    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.titulo

    @property
    def portada_url(self):
        if self.issn:
            clean_issn = str(self.issn).replace("-","").replace(" ", "")
            return f"https://covers.openlibrary.org/b/isbn/{clean_issn}-M.jpg"
