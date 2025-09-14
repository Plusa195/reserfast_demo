from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import TblCliente, TblUsuario
import logging

logger = logging.getLogger(__name__)

class SessionValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
    # Rutas públicas (no requieren autenticación)
        public_paths = [
            '/reserfast/',
            '/reserfast/login_admin/',
            '/reserfast/login_clientes/',
            '/reserfast/logout_empleado/',
            '/reserfast/logout_cliente/',
            '/reserfast/crear_cliente/',
            '/reserfast/crear_exito/',
            '/admin/',
            '/static/',
            '/media/',
            '/password_reset/',
            '/',  # Página principal
        ]
        
    # Rutas de cliente (requieren sesión de cliente)
        cliente_paths = [
            '/reserfast/index_cliente/',
            '/reserfast/crear_reserva/',
            '/reserfast/mis_reservas/',
            '/reserfast/editar_reserva/',
            '/reserfast/eliminar_reserva/',
            '/reserfast/perfil/',
            '/reserfast/editar_perfil/',
            '/reserfast/menu/',
            '/reserfast/mesas/',
            '/reserfast/crear_venta/',
            '/reserfast/verificar_disponibilidad_mesa/',
            '/reserfast/detalle_reserva_ajax/',
        ]
        
    # Rutas de empleado (requieren sesión de empleado)
        empleado_paths = [
            '/reserfast/index_admin/',
            '/reserfast/panel_garzon/',
            '/reserfast/cambiar_password/',
            '/reserfast/admin_garzones/',
            '/reserfast/crear_garzones/',
            '/reserfast/eliminar_garzones/',
            '/reserfast/actualizar_garzones/',
            '/reserfast/gestion_cocina/',
            '/reserfast/admin_cocina/',
            '/reserfast/crear_usuarios_cocina/',
            '/reserfast/eliminar_usuarios_cocina/',
            '/reserfast/actualizar_usuarios_cocina/',
            '/reserfast/editar_mesa/',
            '/reserfast/eliminar_mesa/',
        ]
        
        current_path = request.path
        
    # Permitir acceso si la ruta es pública
        if any(current_path.startswith(path) for path in public_paths):
            return None
        
    # Datos de sesión
        cliente_id = request.session.get('cliente_id')
        usuario_id = request.session.get('id_usuario')
        
    # ¿Ruta de cliente?
        is_cliente_path = any(current_path.startswith(path) for path in cliente_paths)
        
    # ¿Ruta de empleado?
        is_empleado_path = any(current_path.startswith(path) for path in empleado_paths)
        
        # Si tiene ambas sesiones activas (conflicto), limpiar y redirigir
        if cliente_id and usuario_id:
            request.session.flush()
            messages.warning(request, 'Se detectaron sesiones conflictivas. Por favor, inicia sesión nuevamente.')
            return redirect('reserfast:index')
        
        # Manejo de rutas de cliente
        if is_cliente_path:
            if not cliente_id:
                messages.info(request, 'Necesitas iniciar sesión como cliente para acceder a esta página.')
                return redirect('reserfast:login_clientes')
            
            # Validar que el cliente existe y está activo
            try:
                cliente = TblCliente.objects.get(id_cliente=cliente_id, b_activo=True)
                # Agregar información del cliente al request para uso en las vistas
                request.cliente = cliente
            except TblCliente.DoesNotExist:
                request.session.flush()
                messages.error(request, 'Su sesión de cliente ha expirado o el usuario no existe.')
                return redirect('reserfast:login_clientes')
            except Exception as e:
                logger.error(f"Error validando cliente: {e}")
                messages.error(request, 'Error interno del servidor.')
                return redirect('reserfast:login_clientes')
        
        # Manejo de rutas de empleado
        if is_empleado_path:
            if not usuario_id:
                messages.info(request, 'Necesitas iniciar sesión como empleado para acceder a esta página.')
                return redirect('reserfast:login_admin')
            
            # Validar que el usuario existe y está activo
            try:
                usuario = TblUsuario.objects.get(id_usuario=usuario_id, b_activo=True)
                # Agregar información del usuario al request para uso en las vistas
                request.usuario = usuario
            except TblUsuario.DoesNotExist:
                request.session.flush()
                messages.error(request, 'Su sesión de empleado ha expirado o el usuario no existe.')
                return redirect('reserfast:login_admin')
            except Exception as e:
                logger.error(f"Error validando usuario: {e}")
                messages.error(request, 'Error interno del servidor.')
                return redirect('reserfast:login_admin')
        
        return None
