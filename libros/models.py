from django.db import models
import requests
import os
from pathlib import Path
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

    def save(self, *args, **kwargs):
        # 1. Save the book data first
        super().save(*args, **kwargs)

        # 2. Check if we have an ISBN (Make sure this matches your model field name!)
        # If your field is called 'isbn', change 'issn' to 'isbn' below
        isbn_to_use = getattr(self, 'issn', None) or getattr(self, 'isbn', None)

        if isbn_to_use:
            try:
                # Clean ISBN (remove dashes/spaces)
                clean_isbn = str(isbn_to_use).replace("-", "").replace(" ", "")
                url = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"
                
                # Windows
                ruta = os.path.join(settings.BASE_DIR, "static", "assets", "portadas")
                os.makedirs(ruta, exist_ok=True)
                ruta_imagen = os.path.join(ruta, f"{isbn_to_use}.jpg")

                # Linux
                ruta = Path(settings.BASE_DIR) / "static" / "assets" / "portadas"
                ruta.mkdir(parents=True, exist_ok=True)

                ruta_imagenL = ruta / f"{isbn_to_use}.jpg"

    
                if not os.path.exists(ruta_imagen) or not ruta_imagen.exists():
                    response = requests.get(url, timeout=5)
                    
                    # OpenLibrary returns a tiny pixel if image isn't found. 
                    # We only save if it's larger than 1000 bytes (1KB).
                    if response.status_code == 200 and len(response.content) > 1000:
                        with open(ruta_imagen, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Portada descargada para: {isbn_to_use}")
                    else:
                        print(f"⚠️ OpenLibrary no tiene portada para ISBN: {isbn_to_use}")
    
            except Exception as e:
                print(f"❌ Error descargando portada: {e}")
