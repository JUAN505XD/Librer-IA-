from datetime import timedelta
from django.utils import timezone
from .models import Carrito
from .views import MINUTOS_EXPIRACION, limpiar_items_expirados

def tiempo_carrito(request):
    """
    Este procesador inyecta de forma automática la variable 'segundos_restantes'
    en el contexto de absolutamente cualquier plantilla HTML del proyecto.
    """
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user, estado='ACTIVO').first()
        if carrito:
            # 🛡️ Aprovechamos para limpiar el stock de forma pasiva en cualquier clic
            limpiar_items_expirados(carrito)
            
            # Volvemos a verificar si el carrito sobrevivió a la limpieza
            if Carrito.objects.filter(id=carrito.id, estado='ACTIVO').exists():
                if carrito.items.exists():
                    ahora = timezone.now()
                    limite_tiempo = carrito.actualizado_en + timedelta(minutes=MINUTOS_EXPIRACION)
                    segundos = int((limite_tiempo - ahora).total_seconds())
                    return {'segundos_restantes_global': max(0, segundos)}
                    
    return {'segundos_restantes_global': 0}
