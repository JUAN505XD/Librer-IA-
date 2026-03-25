from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Persona, Cliente, Preferencias, Administrador
from datetime import date


#hola esto en un ensayo para ver si funciona el commit en git hub
class RegistroClienteForm(UserCreationForm):

    dni = forms.IntegerField()
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().isoformat(),
            'min': f"{date.today().year - 100}-01-01",
            }))
    lugar_nacimiento = forms.CharField(max_length=100)

    genero = forms.ChoiceField(choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro')
    ])

    direccion_envio = forms.CharField(max_length=200)
    email = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ["username", "password1", "password2"]

    def save(self, commit=True):

        usuario = super().save(commit=False)
        usuario.rol = "CLIENTE"

        if commit:
            usuario.save()

            Persona.objects.create(
                dni=self.cleaned_data["dni"],
                usuario=usuario,
                nombre=self.cleaned_data["nombres"],
                apellido=self.cleaned_data["apellidos"],
                fecha_nacimiento=self.cleaned_data["fecha_nacimiento"],
                lugar_nacimiento=self.cleaned_data["lugar_nacimiento"],
                sexo=self.cleaned_data["genero"],
            )

            Cliente.objects.create(
                usuario=usuario,
                correo=self.cleaned_data["email"],
                direccion_envio=self.cleaned_data["direccion_envio"]
            )

        return usuario
class RegistroAdminForm(UserCreationForm):

    dni = forms.IntegerField()
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)

    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'max': date.today().isoformat(),
        'min': f"{date.today().year - 100}-01-01",
    }))

    lugar_nacimiento = forms.CharField(max_length=100)

    genero = forms.ChoiceField(choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro')
    ])

    email = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ["username", "password1", "password2"]

    def save(self, commit=True):

        usuario = super().save(commit=False)
        usuario.rol = "ADMIN"   # 🔥 clave

        if commit:
            usuario.save()

            Persona.objects.create(
                dni=self.cleaned_data["dni"],
                usuario=usuario,
                nombre=self.cleaned_data["nombres"],
                apellido=self.cleaned_data["apellidos"],
                fecha_nacimiento=self.cleaned_data["fecha_nacimiento"],
                lugar_nacimiento=self.cleaned_data["lugar_nacimiento"],
                sexo=self.cleaned_data["genero"],
            )

            Administrador.objects.create(  
                usuario=usuario,
                correo=self.cleaned_data["email"]
            )

        return usuario

    
class LoginForm(forms.Form):

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)



class PreferenciasForm(forms.ModelForm):
    class Meta:
        model = Preferencias
        fields = ["generos", "autores"]
        widgets = {
            "generos": forms.CheckboxSelectMultiple(),
            "autores": forms.CheckboxSelectMultiple(),
        }

class EditarclienteForm(forms.Form):

    dni = forms.IntegerField(required=False)
    username = forms.CharField(max_length=150, required=False)

    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().isoformat(),
            'min': f"{date.today().year - 100}-01-01",
        }),
        required=False
    )
    lugar_nacimiento = forms.CharField(max_length=100, required=False)

    genero = forms.ChoiceField(
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro')
        ],
        required=False
    )

    direccion_envio = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(required=False)

class EditarAdminForm(forms.Form):

    dni = forms.IntegerField(required=False)
    username = forms.CharField(max_length=150, required=False)

    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().isoformat(),
            'min': f"{date.today().year - 100}-01-01",
        }),
        required=False
    )
    lugar_nacimiento = forms.CharField(max_length=100, required=False)

    genero = forms.ChoiceField(
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro')
        ],
        required=False
    )

    email = forms.EmailField(required=False)
    
