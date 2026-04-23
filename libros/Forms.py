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
            "anio_publicacion",
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

    # 🔹 IDIOMA
    def clean_idioma(self):
        idioma = self.cleaned_data.get("idioma")

        if not idioma or idioma.strip() == "":
            raise forms.ValidationError("El idioma no puede estar vacío")

        return idioma.strip()

    # 🔹 ISSN
    def clean_issn(self):
        issn = self.cleaned_data.get("issn")

        if not issn or issn.strip() == "":
            raise forms.ValidationError("El ISSN no puede estar vacío")

        if Libro.objects.filter(issn=issn).exists():
            raise forms.ValidationError("Este ISSN ya está registrado")

        return issn.strip()

    # 🔹 AÑO
    def clean_anio_publicacion(self):
        anio = self.cleaned_data.get("anio_publicacion")

        if anio is None:
            raise forms.ValidationError("El año es obligatorio")

        if anio > date.today().year:
            raise forms.ValidationError("El año no puede ser futuro")

        if anio < 1500:
            raise forms.ValidationError("Año demasiado antiguo")

        return anio

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

    # 🔹 VALIDACIÓN GENERAL (COHERENCIA)
    def clean(self):
        cleaned_data = super().clean()

        anio = cleaned_data.get("anio_publicacion")
        fecha = cleaned_data.get("fecha_publicacion")

        if anio and fecha:
            if fecha.year != anio:
                self.add_error("fecha_publicacion", "El año y la fecha no coinciden")

        return cleaned_data