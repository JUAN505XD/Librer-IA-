from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .Forms import RegistroClienteForm, LoginForm, PreferenciasForm, EditarPerfilForm
from .models import Preferencias, Persona, Cliente
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def registro(request):

    if request.method == "POST":

        form = RegistroClienteForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            # ✅ LOGIN AUTOMÁTICO
            login(request, usuario)

            return redirect("preferencias")

    else:
        form = RegistroClienteForm()

    return render(request, "registro.html", {"form": form})


def iniciar_sesion(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("inicio")  # página después de login

            else:
                form.add_error(None, "Usuario o contraseña incorrectos")

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})

def cerrar_sesion(request):
    logout(request)
    return redirect("inicio")


@login_required
def preferencias(request):

    if Preferencias.objects.filter(usuario=request.user).exists():
        return redirect("inicio")

    if request.method == "POST":

        print("POST:", request.POST)   # ✅ AQUÍ
        form = PreferenciasForm(request.POST)

        print("VALID:", form.is_valid())  # ✅ AQUÍ
        print("ERRORES:", form.errors)    # ✅ AQUÍ

        if "saltar" in request.POST:
            return redirect("inicio")

        if form.is_valid():
            preferencias = form.save(commit=False)
            preferencias.usuario = request.user
            preferencias.save()

            form.save_m2m()

            return redirect("inicio")

    else:
        form = PreferenciasForm()

    return render(request, "preferencias.html", {"form": form})

def inicio(request):
    return render(request, "inicio.html")

@login_required
def editar_perfil(request):

    usuario = request.user
    persona = Persona.objects.get(usuario=usuario)
    cliente = Cliente.objects.get(usuario=usuario)

    if request.method == "POST":
        form = EditarPerfilForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            #dni
            if data["dni"]:
                persona.dni = data["dni"]

            # Usuario
            if data["username"]:
                usuario.username = data["username"]
                usuario.save()

            # Persona
            if data["nombres"]:
                persona.nombre = data["nombres"]

            if data["apellidos"]:
                persona.apellido = data["apellidos"]

            if data["fecha_nacimiento"]:
                persona.fecha_nacimiento = data["fecha_nacimiento"]

            if data["lugar_nacimiento"]:
                persona.lugar_nacimiento = data["lugar_nacimiento"]

            if data["genero"]:
                persona.sexo = data["genero"]

            persona.save()

            # Cliente
            if data["email"]:
                cliente.correo = data["email"]

            if data["direccion_envio"]:
                cliente.direccion_envio = data["direccion_envio"]

            cliente.save()

            return redirect("inicio")

    else:
        form = EditarPerfilForm({
        "dni": persona.dni,
        "username": usuario.username,

        "nombres": persona.nombre,
        "apellidos": persona.apellido,
        "fecha_nacimiento": persona.fecha_nacimiento,
        "lugar_nacimiento": persona.lugar_nacimiento,
        "genero": persona.sexo,

        "email": cliente.correo,
        "direccion_envio": cliente.direccion_envio
    })

    return render(request, "editar_perfil.html", {"form": form})

@login_required
def cambiar_password(request):

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 🔥 mantiene sesión activa
            return redirect("inicio")

    else:
        form = PasswordChangeForm(request.user)

    return render(request, "cambiar_password.html", {"form": form})