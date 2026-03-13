from django.shortcuts import render, redirect
from django.contrib import messages
from .Forms import RegistroClienteForm


def registro(request):

    if request.method == "POST":

        form = RegistroClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente")
            return redirect("registro")

    else:
        form = RegistroClienteForm()

    return render(request, "registro.html", {"form": form})