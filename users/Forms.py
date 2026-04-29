from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from .models import Usuario, Persona, Cliente, Preferencias, Administrador
from django_countries.fields import CountryField
from datetime import date
from email_validator import validate_email, EmailNotValidError


class RegistroClienteForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden",
    }

    dni = forms.IntegerField()
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={
            'type': 'date',
            'max': f"{date.today().year - 12}-01-01",
            'min': f"{date.today().year - 100}-01-01",
            }))
    lugar_nacimiento = CountryField().formfield(blank_label="País de nacimiento")

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

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if Usuario.objects.filter(username=username).exists():
         raise forms.ValidationError("Este usuario ya existe")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            valid = validate_email(email, check_deliverability= True)

            email = valid.email

        except EmailNotValidError as e:
            raise forms.ValidationError("Dominio inexistente")

        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")

        if Persona.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado")

        return dni

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if password:
            if len(set(password)) < 4:
                raise forms.ValidationError(
                        "Contraseña demasiado predecible"
                        )

        return password

    def save(self, commit=True):

        usuario = super().save(commit=False)
        usuario.rol = "CLIENTE"

        if commit:
            usuario.save()

            codigo_pais=self.cleaned_data.get("lugar_nacimiento")

            Persona.objects.create(
                dni=self.cleaned_data["dni"],
                usuario=usuario,
                nombre=self.cleaned_data["nombres"],
                apellido=self.cleaned_data["apellidos"],
                fecha_nacimiento=self.cleaned_data["fecha_nacimiento"],
                lugar_nacimiento=self.cleaned_data.get("lugar_nacimiento"),
                sexo=self.cleaned_data["genero"],
            )

            Cliente.objects.create(
                usuario=usuario,
                correo=self.cleaned_data["email"],
                direccion_envio=self.cleaned_data["direccion_envio"]
            )

        return usuario
    
class RegistroAdminForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden",
    }

    dni = forms.IntegerField()
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)

    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
	'max': f"{date.today().year - 12}-01-01",
        'min': f"{date.today().year - 100}-01-01",
    }))

    lugar_nacimiento = CountryField().formfield(blank_label="País de nacimiento")


    genero = forms.ChoiceField(choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro')
    ])

    email = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ["username", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if Usuario.objects.filter(username=username).exists():
         raise forms.ValidationError("Este usuario ya existe")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            valid = validate_email(email, check_deliverability= True)

            email = valid.email

        except EmailNotValidError as e:
            raise forms.ValidationError("Dominio inexistente")

        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")

        if Persona.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado")

        return dni


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
                lugar_nacimiento=self.cleaned_data.get("lugar_nacimiento"),
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

    dni = forms.IntegerField(required=False, disabled = True)
    username = forms.CharField(max_length=150, required=False)

    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)
    fecha_nacimiento = forms.DateField(disabled = True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': f"{date.today().year - 12}-01-01",
            'min': f"{date.today().year - 100}-01-01",
        }),
        required=False
    )
    lugar_nacimiento = CountryField().formfield(disabled=True,blank_label="País de nacimiento")



    genero = forms.ChoiceField(disabled=True,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro')
        ],
        required=False
    )

    direccion_envio = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(disabled=True,required=False)

class EditarAdminForm(forms.Form):

    dni = forms.IntegerField(disabled=True,required=False)
    username = forms.CharField(max_length=150, required=False)

    nombres = forms.CharField(max_length=100, required=False)
    apellidos = forms.CharField(max_length=100, required=False)
    fecha_nacimiento = forms.DateField(disabled=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            
            'min': f"{date.today().year - 100}-01-01",
        }),
        required=False
    )
    lugar_nacimiento = CountryField().formfield(disabled=True,blank_label="País de nacimiento")


    genero = forms.ChoiceField(disabled=True,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro')
        ],
        required=False
    )

    email = forms.EmailField(disabled=True,required=False)
    
class CustomPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        'password_incorrect': "La contraseña actual es incorrecta",
    }

    def clean_new_password2(self):
        p1 = self.cleaned_data.get("new_password1")
        p2 = self.cleaned_data.get("new_password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")

        return p2
# esto es para el nuevo commit de juan
