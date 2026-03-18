from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .Forms import RegistroClienteForm, LoginForm, PreferenciasForm
from .models import Usuario, Preferencias
from django.contrib.auth.decorators import login_required


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

    # 👉 evitar que vuelva a entrar si ya tiene preferencias
    if Preferencias.objects.filter(usuario=request.user).exists():
        return redirect("inicio")

    if request.method == "POST":

        if "saltar" in request.POST:
            return redirect("inicio")

        form = PreferenciasForm(request.POST)

        if form.is_valid():
            preferencias = form.save(commit=False)
            preferencias.usuario = request.user
            preferencias.save()

            form.save_m2m()  # 🔥 ESTO ES CLAVE (ManyToMany)

            return redirect("inicio")

    else:
        form = PreferenciasForm()

    return render(request, "preferencias.html", {"form": form})

def inicio(request):
    return render(request, "inicio.html")

