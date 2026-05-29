from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from carrito.models import Carrito
from carrito.views import limpiar_items_expirados
from .Forms import LibroForm
from libros.models import Libro, Autor, Genero, Idioma

def crear_libro(request):

    if request.method == "POST":
        form = LibroForm(request.POST)

        if form.is_valid():
            libro=form.save(commit=False)
            libro.save()
            form.save_m2m()
            return redirect("inicio")  # o a lista de libros

    else:
        form = LibroForm()

    return render(request, "crear_libro.html", {"form": form})


def inicio(request):
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()
        if carrito:
            limpiar_items_expirados(carrito)

    libros = Libro.objects.all().order_by('-id')


    paginator = Paginator(libros,12)
    numero_pagina= request.GET.get('page')
    libros_paginados=paginator.get_page(numero_pagina)

    rango_paginas = paginator.get_elided_page_range(
            number=libros_paginados.number,
            on_each_side=2,
            on_ends=1
            )

    return render(request, "inicio.html", {
        "libros": libros_paginados,
        "rango_paginas": rango_paginas
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
