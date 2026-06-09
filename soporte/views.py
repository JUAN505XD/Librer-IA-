from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import TemaSoporte, MensajeSoporte


def es_admin(usuario):
    return (
        usuario.is_authenticated
        and usuario.rol in ["ADMIN", "ROOT"]
    )


@login_required
def mis_consultas(request):

    temas = (
        TemaSoporte.objects
        .filter(usuario=request.user)
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "mis_consultas.html",
        {
            "temas": temas
        }
    )


@login_required
def crear_consulta(request):

    if request.method == "POST":

        titulo = request.POST.get("titulo")
        mensaje = request.POST.get("mensaje")

        tema = TemaSoporte.objects.create(
            usuario=request.user,
            titulo=titulo
        )

        MensajeSoporte.objects.create(
            tema=tema,
            autor=request.user,
            mensaje=mensaje
        )

        messages.success(
            request,
            "Consulta creada correctamente."
        )

        return redirect("mis_temas")

    return render(
        request,
        "crear_consulta.html"
    )


@login_required
def ver_consulta(request, tema_id):

    tema = get_object_or_404(
        TemaSoporte,
        id=tema_id
    )

    # Solo el dueño o administradores
    if (
        tema.usuario != request.user
        and request.user.rol not in ["ADMIN", "ROOT"]
    ):
        return HttpResponseForbidden(
            "No tienes permiso para ver esta consulta."
        )

    if request.method == "POST":

        if tema.estado == "CERRADO":
            messages.error(
                request,
                "Esta consulta ya fue cerrada."
            )
            return redirect(
                "ver_tema",
                tema_id=tema.id
            )

        texto = request.POST.get("mensaje")

        if texto:

            MensajeSoporte.objects.create(
                tema=tema,
                autor=request.user,
                mensaje=texto
            )

            messages.success(
                request,
                "Respuesta enviada."
            )

        return redirect(
            "ver_tema",
            tema_id=tema.id
        )

    return render(
        request,
        "ver_consulta.html",
        {
            "tema": tema
        }
    )


@login_required
def lista_consultas_admin(request):

    if not es_admin(request.user):
        return HttpResponseForbidden(
            "No tienes permiso para ver esta consulta."
        )

    temas = (
        TemaSoporte.objects
        .all()
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "admin_temas.html",
        {
            "temas": temas
        }
    )


@login_required
def cerrar_consulta(request, tema_id):

    if not es_admin(request.user):
        return redirect("inicio")

    tema = get_object_or_404(
        TemaSoporte,
        id=tema_id
    )

    tema.estado = "CERRADO"
    tema.save()

    messages.success(
        request,
        "Consulta cerrada."
    )

    return redirect("lista_temas_admin")
