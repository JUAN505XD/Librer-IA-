from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from libros.models import Genero, Autor
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField

# =========================
# MANAGER DE USUARIO
# =========================

class UsuarioManager(BaseUserManager):

    def create_user(self, username, password=None, rol="CLIENTE"):
        if not username:
            raise ValueError("El usuario es obligatorio")

        user = self.model(
            username=username,
            rol=rol
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, username, password=None):

        if self.model.objects.filter(rol="ROOT").exists():
            raise ValueError("Ya existe un usuario root")

        user = self.model(
            username=username,
            rol="ROOT",
            is_staff=True,
            is_superuser=True
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


# =========================
# MODELO PRINCIPAL USUARIO
# =========================

class Usuario(AbstractBaseUser):

    ROLES = [
        ("ROOT", "Root"),
        ("ADMIN", "Administrador"),
        ("CLIENTE", "Cliente"),
    ]

    username = models.CharField(max_length=150, unique=True)
    rol = models.CharField(max_length=10, choices=ROLES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


# =========================
# DATOS PERSONALES
# =========================

class Persona(models.Model):
    
    dni = models.IntegerField()
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField()

    lugar_nacimiento = CountryField()

    sexo = models.CharField(max_length=1)


# =========================
# ADMINISTRADOR
# =========================

class Administrador(models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    correo = models.EmailField()


# =========================
# CLIENTE
# =========================

class Cliente(models.Model):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    correo = models.EmailField()
    direccion_envio = models.CharField(max_length=200)
    latitud = models.DecimalField(max_length=20, decimal_places=16,max_digits=19)
    longitud = models.DecimalField(max_length=20, decimal_places=16,max_digits=19)


# =========================
# Preferencias
# =========================


class Preferencias(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    generos = models.ManyToManyField(Genero, blank=True)
    autores = models.ManyToManyField(Autor, blank=True)

    recibir_noticias = models.BooleanField(
        default=False,
        verbose_name="Recibir noticias y novedades"
    )

# =========================
# TARJETAS DE CRÉDITO
# =========================

class Tarjeta(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tarjetas"
    )

    numero = models.CharField(
        max_length=19,
        unique=True
    )

    titular = models.CharField(
        max_length=100
    )

    mes_vencimiento = models.PositiveSmallIntegerField()
    año_vencimiento = models.PositiveSmallIntegerField()

    cvv = models.CharField(
        max_length=3
    )

    saldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    activa = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.numero[-4:]}"

    def numero_mostrado(self):
        return f"**** **** **** {self.numero[-4:]}"
    


class CuponCumpleanos(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cupones_cumpleanos"
    )

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    descuento = models.PositiveIntegerField(
        default=10
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_expiracion = models.DateTimeField()

    usado = models.BooleanField(
        default=False
    )

    def anio_actual():
        return timezone.localdate().year

    anio_generado = models.PositiveIntegerField(
        default=anio_actual
    )

    def vigente(self):

        return (
            not self.usado
            and timezone.now() <= self.fecha_expiracion
        )

    def __str__(self):
        return self.codigo
