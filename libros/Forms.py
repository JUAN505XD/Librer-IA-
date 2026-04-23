from django import forms
from .models import Libro
from datetime import date, timedelta

class LibroForm(forms.ModelForm):

    class Meta:
        model = Libro
        fields = [
            "titulo",
            "autor",
            "genero",
            "numero_paginas",
            "editorial",
            "issn",
            "idioma",
            "fecha_publicacion",
            "estado",
            "precio"
        ]

        widgets = {
            "fecha_publicacion": forms.DateInput(attrs={
                "type": "date",
                "max": (date.today() - timedelta(days=1)).isoformat()
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

        if Libro.objects.filter(issn=issn).exists():
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
    def clean_fecha_publicacion(self):
        fecha = self.cleaned_data.get("fecha_publicacion")

        if fecha and fecha > (date.today() - timedelta(days=1)):
            raise forms.ValidationError("La fecha no puede ser superior a ayer")

        return fecha
