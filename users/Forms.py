from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from .models import Usuario, Persona, Cliente, Preferencias, Administrador, Tarjeta
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
    latitud = forms.DecimalField(decimal_places=16, max_digits=19)
    longitud = forms.DecimalField(decimal_places=16,max_digits=19)
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
                direccion_envio=self.cleaned_data["direccion_envio"],
                latitud=self.cleaned_data["latitud"],
                longitud=self.cleaned_data["longitud"],
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
        fields = [
            "generos",
            "autores",
            "recibir_noticias"
        ]

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
    lugar_nacimiento = CountryField().formfield(disabled=True,blank_label="País de nacimiento", required=False)



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
class TarjetaForm(forms.ModelForm):

    class Meta:
        model = Tarjeta
        fields = [
            "numero",
            "titular",
            "mes_vencimiento",
            "año_vencimiento",
            "cvv",
            "saldo"
        ]

        widgets = {
            "numero": forms.TextInput(attrs={
                "placeholder": "1234567812345678",
                "maxlength": "16"
            }),
            "mes_vencimiento": forms.NumberInput(attrs={
                "placeholder": "MM"
            }),
            "año_vencimiento": forms.NumberInput(attrs={
                "min": date.today().year,
                "placeholder": "YYYY"
            }),

            "titular": forms.TextInput(attrs={
                "placeholder": "Nombre del titular"
            }),

            "cvv": forms.PasswordInput(attrs={
                "maxlength": "3"
            }),
            "saldo": forms.NumberInput(attrs={
                "placeholder": "0.00"
            })
        }

    def clean_numero(self):
        numero = self.cleaned_data["numero"]

        if not numero.isdigit():
            raise forms.ValidationError(
                "La tarjeta solo puede contener números"
            )

        if len(numero) != 16:
            raise forms.ValidationError(
                "La tarjeta debe tener 16 dígitos"
            )

        if Tarjeta.objects.filter(numero=numero).exists():
            raise forms.ValidationError(
                "Esta tarjeta ya está registrada"
            )

        return numero

    def clean_cvv(self):
        cvv = self.cleaned_data["cvv"]

        if not cvv.isdigit():
            raise forms.ValidationError(
                "CVV inválido"
            )

        if len(cvv) != 3:
            raise forms.ValidationError(
                "El CVV debe tener 3 dígitos"
            )

        return cvv

    from datetime import date

     # 🔥 MES
    def clean_mes_vencimiento(self):
        mes = self.cleaned_data.get("mes_vencimiento")

        if mes < 1 or mes > 12:
            raise forms.ValidationError("El mes debe estar entre 1 y 12")

        return mes

    # 🔥 AÑO
    def clean_año_vencimiento(self):
        año = self.cleaned_data.get("año_vencimiento")

        año_actual = date.today().year

        if año < año_actual:
            raise forms.ValidationError("La tarjeta está vencida")

        return año

    # 🔥 VALIDACIÓN COMPLETA (IMPORTANTE)
    def clean(self):
        cleaned_data = super().clean()

        mes = cleaned_data.get("mes_vencimiento")
        año = cleaned_data.get("año_vencimiento")

        if mes and año:
            hoy = date.today()

            if año == hoy.year and mes < hoy.month:
                raise forms.ValidationError("La tarjeta ya expiró")

        return cleaned_data

    def clean_titular(self):
        titular = self.cleaned_data["titular"].strip()

        if len(titular) < 5:
            raise forms.ValidationError(
                "Nombre del titular inválido"
            )

        return titular
    
    def clean_saldo(self):
        saldo = self.cleaned_data.get("saldo")

        if saldo is None:
            raise forms.ValidationError("El saldo es obligatorio")

        if saldo < 50000:
            raise forms.ValidationError("El saldo mínimo es 50.000")

        if saldo > 10_000_000:
            raise forms.ValidationError("El saldo máximo permitido es 10 millones")

        return saldo
    
class RecargarSaldoForm(forms.Form):
    monto = forms.DecimalField()

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")

        if monto is None:
            raise forms.ValidationError("El monto es obligatorio")

        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0")

        if monto < 50000:
            raise forms.ValidationError("El monto mínimo es 50.000")

        if monto % 1000 != 0:
            raise forms.ValidationError("Debe ser múltiplo de 1000")

        if monto > 10_000_000:
            raise forms.ValidationError("Monto demasiado alto")

        return monto
