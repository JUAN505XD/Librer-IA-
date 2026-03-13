from django.core.management.base import BaseCommand
from users.models import Usuario

class Command(BaseCommand):
    help = 'Crea un superusuario por defecto si no existe'

    def handle(self, *args, **kwargs):
        if not Usuario.objects.filter(username='root').exists():
            Usuario.objects.create_superuser(
                username='root',
                password='root123',
                dni='0000',
                nombres='Administrador',
                apellidos='Sistema',
                fecha_nacimiento='2000-01-01',
                lugar_nacimiento='Sistema',
                direccion_envio='Sistema',
                genero='O',
                email='root@admin.com'
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado'))
        else:
            self.stdout.write('El superusuario ya existe')