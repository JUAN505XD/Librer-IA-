from django.db import models
import requests
import os
from pathlib import Path
from django.conf import settings
from django.core.validators import MaxValueValidator

# Create your models here.
class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

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
    
class Editorial(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Libro(models.Model):
    titulo = models.CharField(max_length=200)

    stock = models.PositiveIntegerField(default=50)

    ESTADO_CHOICES = [
        ('NUEVO', 'Nuevo'),
        ('USADO', 'Usado'),
    ]

    autores = models.ManyToManyField(Autor)

    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT
    )

    numero_paginas = models.PositiveIntegerField(validators=[MaxValueValidator(2000)])

    editorial = models.ForeignKey(
            Editorial,
            on_delete=models.PROTECT
    )

    issn = models.CharField(max_length=50, unique=True)

    idioma = models.ForeignKey(
        Idioma,
        on_delete=models.PROTECT
    )

    año_publicacion = models.IntegerField(validators=[MaxValueValidator(2026)])

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
