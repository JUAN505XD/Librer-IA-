from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class Autor(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Editorial(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    ISSN = models.IntegerField()
    titulo = models.CharField(max_length=200)
    numero_paginas = models.IntegerField()
    fecha_publicacion = models.DateField()
    stock = models.IntegerField()
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    genero = models.ManyToManyField(Genero)
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class UsuarioManager(BaseUserManager):
    def create_user(self, dni, nombres, apellidos, fecha_nacimiento, lugar_nacimiento, direccion_envio, genero, email, username, password=None):
        if not email:
            raise ValueError('El email es obligatorio')
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        if not dni:
            raise ValueError('El DNI es obligatorio')

        user = self.model(
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            lugar_nacimiento=lugar_nacimiento,
            direccion_envio=direccion_envio,
            genero=genero,
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, dni, nombres, apellidos, fecha_nacimiento, lugar_nacimiento, direccion_envio, genero, email, username, password):
        user = self.create_user(
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            lugar_nacimiento=lugar_nacimiento,
            direccion_envio=direccion_envio,
            genero=genero,
            email=email,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    dni = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    lugar_nacimiento = models.CharField(max_length=100)
    direccion_envio = models.CharField(max_length=200)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['dni', 'nombres', 'apellidos', 'fecha_nacimiento', 'lugar_nacimiento', 'direccion_envio', 'genero', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

# Create your models here.
