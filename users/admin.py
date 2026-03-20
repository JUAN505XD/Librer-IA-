from django.contrib import admin
from .models import Usuario, Persona, Administrador, Cliente, Preferencias

admin.site.register(Usuario)
admin.site.register(Persona)
admin.site.register(Administrador)
admin.site.register(Cliente)
@admin.register(Preferencias)
class PreferenciasAdmin(admin.ModelAdmin):
    list_display = ("usuario",)
    filter_horizontal = ("generos", "autores")
# Register your models here.
