from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from functools import wraps
from .models import TblCliente, TblUsuario
import logging

logger = logging.getLogger(__name__)

def cliente_login_required(view_func):
    """
    Decorador que requiere que el usuario esté autenticado como cliente.
    Redirige a login_clientes si no está autenticado.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        cliente_id = request.session.get('cliente_id')
        
        if not cliente_id:
            messages.info(request, 'Necesitas iniciar sesión para acceder a esta página.')
            return redirect('reserfast:login_clientes')
        
        try:
            cliente = TblCliente.objects.get(id_cliente=cliente_id, b_activo=True)
            request.cliente = cliente
            return view_func(request, *args, **kwargs)
        except TblCliente.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.')
            return redirect('reserfast:login_clientes')
        except Exception as e:
            logger.error(f"Error en cliente_login_required: {e}")
            messages.error(request, 'Error interno del servidor.')
            return redirect('reserfast:login_clientes')
    
    return wrapper

def usuario_login_required(view_func):
    """
    Decorador que requiere que el usuario esté autenticado como empleado.
    Redirige a login_admin si no está autenticado.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('id_usuario')
        
        if not usuario_id:
            messages.info(request, 'Necesitas iniciar sesión como empleado para acceder a esta página.')
            return redirect('reserfast:login_admin')
        
        try:
            usuario = TblUsuario.objects.get(id_usuario=usuario_id, b_activo=True)
            request.usuario = usuario
            return view_func(request, *args, **kwargs)
        except TblUsuario.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.')
            return redirect('reserfast:login_admin')
        except Exception as e:
            logger.error(f"Error en usuario_login_required: {e}")
            messages.error(request, 'Error interno del servidor.')
            return redirect('reserfast:login_admin')
    
    return wrapper

def perfil_required(perfiles_permitidos):
    """
    Decorador que requiere que el usuario tenga un perfil específico.
    
    Args:
        perfiles_permitidos (list): Lista de perfiles permitidos (ej: ['admin', 'garzon'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            usuario_id = request.session.get('id_usuario')
            perfil_usuario = request.session.get('perfil_usuario')
            
            if not usuario_id or not perfil_usuario:
                messages.info(request, 'Necesitas iniciar sesión para acceder a esta página.')
                return redirect('reserfast:login_admin')
            
            if perfil_usuario not in perfiles_permitidos:
                messages.error(request, f'No tienes permisos para acceder a esta página. Se requiere perfil: {", ".join(perfiles_permitidos)}')
                return redirect('reserfast:index_admin')
            
            try:
                usuario = TblUsuario.objects.get(id_usuario=usuario_id, b_activo=True)
                request.usuario = usuario
                return view_func(request, *args, **kwargs)
            except TblUsuario.DoesNotExist:
                request.session.flush()
                messages.error(request, 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.')
                return redirect('reserfast:login_admin')
            except Exception as e:
                logger.error(f"Error en perfil_required: {e}")
                messages.error(request, 'Error interno del servidor.')
                return redirect('reserfast:login_admin')
        
        return wrapper
    return decorator

def ajax_login_required(user_type='cliente'):
    """
    Decorador para vistas AJAX que requieren autenticación.
    
    Args:
        user_type (str): 'cliente' o 'empleado'
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if user_type == 'cliente':
                cliente_id = request.session.get('cliente_id')
                if not cliente_id:
                    return HttpResponse('No autorizado', status=401)
                
                try:
                    cliente = TblCliente.objects.get(id_cliente=cliente_id, b_activo=True)
                    request.cliente = cliente
                except TblCliente.DoesNotExist:
                    request.session.flush()
                    return HttpResponse('Sesión expirada', status=401)
                    
            elif user_type == 'empleado':
                usuario_id = request.session.get('id_usuario')
                if not usuario_id:
                    return HttpResponse('No autorizado', status=401)
                
                try:
                    usuario = TblUsuario.objects.get(id_usuario=usuario_id, b_activo=True)
                    request.usuario = usuario
                except TblUsuario.DoesNotExist:
                    request.session.flush()
                    return HttpResponse('Sesión expirada', status=401)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
