from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from libros.models import Genero, Autor
from django.core.exceptions import ValidationError

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
    def validar_fecha_nacimiento(value):
        hoy = date.today()
        anio_limite = hoy.year - 100

        if value > hoy:
            raise ValidationError("La fecha no es actual")

        if value.year < anio_limite:
            raise ValidationError("La fecha no puede ser tan antigua")

    dni = models.IntegerField()
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField()

    lugar_nacimiento = models.CharField(max_length=100)

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

# =========================
# Preferencias
# =========================


class Preferencias(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    generos = models.ManyToManyField(Genero, blank=True)
    autores = models.ManyToManyField(Autor, blank=True)