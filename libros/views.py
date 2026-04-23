from django.shortcuts import render, redirect
from .Forms import LibroForm
from libros.models import Libro, Autor, Genero, Idioma

def crear_libro(request):

    if request.method == "POST":
        form = LibroForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("inicio")  # o a lista de libros

    else:
        form = LibroForm()

    return render(request, "crear_libro.html", {"form": form})


def inicio(request):

    libros = Libro.objects.all()  # 🔥 últimos 6

    return render(request, "inicio.html", {
        "libros": libros
    })



def buscar_libros(request):

    libros = Libro.objects.all()

    # 🔎 BÚSQUEDA POR TEXTO
    query = request.GET.get("q")
    if query:
        libros = libros.filter(titulo__icontains=query)

    # 🎯 FILTROS
    autor = request.GET.get("autor")
    if autor:
        libros = libros.filter(autor_id=autor)

    genero = request.GET.get("genero")
    if genero:
        libros = libros.filter(genero_id=genero)

    estado = request.GET.get("estado")
    if estado:
        libros = libros.filter(estado=estado)

    idioma = request.GET.get("idioma")
    if idioma:
        libros = libros.filter(idioma_id=idioma)

    # 💰 PRECIO
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")

    if precio_min:
        libros = libros.filter(precio__gte=precio_min)
    if precio_max:
        libros = libros.filter(precio__lte=precio_max)

    # 📅 AÑO (desde fecha_publicacion)
    anio = request.GET.get("anio")
    if anio:
        libros = libros.filter(fecha_publicacion__year=anio)

    # 📄 PÁGINAS
    paginas_min = request.GET.get("paginas_min")
    paginas_max = request.GET.get("paginas_max")

    if paginas_min:
        libros = libros.filter(numero_paginas__gte=paginas_min)
    if paginas_max:
        libros = libros.filter(numero_paginas__lte=paginas_max)

    return render(request, "buscar.html", {
        "libros": libros,
        "autores": Autor.objects.all(),
        "generos": Genero.objects.all(),
        "idiomas": Idioma.objects.all(),
    })