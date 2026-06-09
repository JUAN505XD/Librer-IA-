from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from users.models import (
    Persona,
    Cliente,
    CuponCumpleanos
)
import uuid

class Command(BaseCommand):

    help = "Enviar cupones de cumpleaños"

    def handle(self, *args, **kwargs):

        hoy = timezone.localdate()

        personas = Persona.objects.filter(
            fecha_nacimiento__month=hoy.month,
            fecha_nacimiento__day=hoy.day
        )

        for persona in personas:

            usuario = persona.usuario

            ya_existe = CuponCumpleanos.objects.filter(
                usuario=usuario,
                anio_generado=timezone.localdate().year
            ).exists()

            if ya_existe:
                continue

            codigo = (
                f"CUMPLE-{uuid.uuid4().hex[:8].upper()}"
            )

            cupon = CuponCumpleanos.objects.create(
            usuario=usuario,
            codigo=codigo,
            descuento=15,
            fecha_expiracion=timezone.now() + timedelta(hours=24),
            anio_generado=timezone.localdate().year
            )

            cliente = Cliente.objects.get(usuario=usuario)

            send_mail(
                subject="🎂 Feliz cumpleaños",
                message=(
                    f"Hola {persona.nombre}\n\n"
                    f"Te regalamos un cupón del "
                    f"{cupon.descuento}% de descuento.\n\n"
                    f"Código: {cupon.codigo}\n\n"
                    f"Válido durante 24 horas."
                ),
                from_email="juan505xd.gamertag@gmail.com",
                recipient_list=[cliente.correo],
                fail_silently=False
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Proceso finalizado"
            )
        )