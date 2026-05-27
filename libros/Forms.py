from django import forms
from .models import Libro
from django_select2 import forms as s2forms
from datetime import date

class LibroForm(forms.ModelForm):

    class Meta:
        model = Libro
        fields = [
            "titulo",
            "autores",
            "genero",
            "numero_paginas",
            "editorial",
            "issn",
            "idioma",
            "año_publicacion",
            "estado",
            "precio"
        ]

        widgets = {
            "año_publicacion": forms.NumberInput(attrs={
                "min": 0,
                "max": date.today().year,
                "placeholder": "Ej: 2026"}),
            "autores": s2forms.Select2MultipleWidget(attrs={
                "style": "width: 100%",
                "data-placeholder": "Selecciona uno o mas autores.."
                }),
            }

    # 🔹 TITULO
    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo")

        if not titulo or titulo.strip() == "":
            raise forms.ValidationError("El título no puede estar vacío")

        return titulo.strip()

    # 🔹 EDITORIAL
    def clean_editorial(self):
        editorial = self.cleaned_data.get("editorial")

        if not editorial or editorial.strip() == "":
            raise forms.ValidationError("La editorial no puede estar vacía")

        return editorial.strip()


    # 🔹 ISSN
    def clean_issn(self):
        issn = self.cleaned_data.get("issn")

        if not issn or issn.strip() == "":
            raise forms.ValidationError("El ISSN no puede estar vacío")

        if Libro.objects.filter(issn=issn).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este ISSN ya está registrado")

        return issn.strip()


    # 🔹 PÁGINAS
    def clean_numero_paginas(self):
        paginas = self.cleaned_data.get("numero_paginas")

        if paginas is None or paginas <= 0:
            raise forms.ValidationError("Debe tener al menos 1 página")

        return paginas

    # 🔹 PRECIO
    def clean_precio(self):
        precio = self.cleaned_data.get("precio")

        if precio is None or precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0")

        return precio

    # 🔹 FECHA
    def clean_año_publicacion(self):
        año = self.cleaned_data.get("año_publicacion")

        if año and año > (date.today().year):
            raise forms.ValidationError("El año no debe ser mayor al actual")

        return año
