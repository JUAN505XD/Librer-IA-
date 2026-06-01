from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from carrito.models import Carrito
from carrito.views import limpiar_items_expirados
from .Forms import LibroForm
from libros.models import Libro, Autor, Genero, Idioma
from users.models import Preferencias
from django.db.models import Q

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

    mostrar_noticias = False

    nuevos_lanzamientos = []
    libros_autores = []
    libros_generos = []

    if request.user.is_authenticated:

        carrito = Carrito.objects.filter(
            usuario=request.user,
            estado='ACTIVO'
        ).first()

        if carrito:
            limpiar_items_expirados(carrito)

        preferencias = Preferencias.objects.filter(
            usuario=request.user
        ).first()

        if preferencias:

            mostrar_noticias = preferencias.recibir_noticias

            # 📚 Últimos libros registrados
            nuevos_lanzamientos = Libro.objects.order_by('-id')[:3]

            # ✍️ Libros de autores favoritos
            autores = preferencias.autores.all()

            if autores.exists():
                libros_autores = (
                    Libro.objects
                    .filter(autores__in=autores)
                    .distinct()
                    .order_by('-id')[:3]
                )

            # 📖 Libros de géneros favoritos
            generos = preferencias.generos.all()

            if generos.exists():
                libros_generos = (
                    Libro.objects
                    .filter(genero__in=generos)
                    .distinct()
                    .order_by('-id')[:3]
                )

    libros = Libro.objects.all().order_by('-id')

    paginator = Paginator(libros, 12)
    numero_pagina = request.GET.get('page')
    libros_paginados = paginator.get_page(numero_pagina)

    rango_paginas = paginator.get_elided_page_range(
            number=libros_paginados.number,
            on_each_side=2,
            on_ends=1
            )

    rango_paginas = paginator.get_elided_page_range(
            number=libros_paginados.number,
            on_each_side=2,
            on_ends=1
            )

    return render(request, "inicio.html", {
        "libros": libros_paginados,
        "mostrar_noticias": mostrar_noticias,

        "nuevos_lanzamientos": nuevos_lanzamientos,
        "libros_autores": libros_autores,
        "libros_generos": libros_generos,
    })


def buscar_libros(request):

    libros = Libro.objects.all().order_by('-id')

    # 🔎 BÚSQUEDA POR TEXTO
    query = request.GET.get("q",'').strip()
    if query:
        libros = libros.filter(autores__id=autor)

    # 🎯 FILTROS
    autor = request.GET.get("autor")
    if autor:
        libros = libros.filter(autores_es__id=autor)

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

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    filtros_url = query_params.urlencode()

    paginator = Paginator(libros, 12)
    page_number = request.GET.get('page')
    libros_paginados = paginator.get_page(page_number)

    rango_paginas = paginator.get_elided_page_range(
            number = libros_paginados.number,
            on_each_side=2,
            on_ends=1
            )

    return render(request, "buscar.html", {
        "libros": libros_paginados,
        "autores": Autor.objects.all(),
        "generos": Genero.objects.all(),
        "idiomas": Idioma.objects.all(),
        "rango_paginas": rango_paginas,
        "filtros_url": filtros_url,
        "query": query
    })

def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro,id=libro_id)

    return render(request, "detalle_libro.html", {
        "libro": libro
        })
