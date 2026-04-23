from django.shortcuts import render, redirect
from .Forms import LibroForm

def crear_libro(request):

    if request.method == "POST":
        form = LibroForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("inicio")  # o a lista de libros

    else:
        form = LibroForm()

    return render(request, "crear_libro.html", {"form": form})
