from django.contrib import admin
from .models import Genero, Autor, Libro, Idioma
# Register your models here.


admin.site.register(Genero)
admin.site.register(Autor)
admin.site.register(Idioma)
admin.site.register(Libro)