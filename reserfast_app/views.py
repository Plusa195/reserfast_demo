from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from .models import *
from .forms import *
from .decorators import cliente_login_required, usuario_login_required, perfil_required, ajax_login_required
import bcrypt
import sqlite3
import logging
import json

logger = logging.getLogger(__name__)

# ===== Helpers =====
def _normalize(s: str) -> str:
    try:
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c)).lower().strip()
    except Exception:
        return (s or '').lower().strip()

def resolve_perfil(alias_key: str):
    """Resolve TblPerfil by friendly alias like 'admin'|'garzon'|'cocinero'.
    Tries multiple names and accent variants; falls back to existing users' perfiles.
    Raises TblPerfil.DoesNotExist if not found.
    """
    key = _normalize(alias_key)
    alias_map = {
        'admin': ['administrador', 'administradora', 'admin'],
        'garzon': ['garzon', 'garzón', 'encargado garzones', 'jefe garzon', 'jefe garzón', 'mesero', 'mozo'],
        'cocinero': ['cocinero', 'chef', 'cocina', 'jefe cocina'],
    }
    candidates = alias_map.get(key, [alias_key])
    for a in candidates:
        obj = TblPerfil.objects.filter(s_nombreperfil__iexact=a).first()
        if obj:
            return obj
    for a in candidates:
        obj = TblPerfil.objects.filter(s_nombreperfil__icontains=a).first()
        if obj:
            return obj
    for a in candidates:
        u = TblUsuario.objects.filter(fk_id_perfil__s_nombreperfil__icontains=a).select_related('fk_id_perfil').first()
        if u and u.fk_id_perfil:
            return u.fk_id_perfil
    try:
        for p in TblPerfil.objects.all():
            if _normalize(p.s_nombreperfil) in [_normalize(a) for a in candidates]:
                return p
    except Exception:
        pass
    raise TblPerfil.DoesNotExist(f'Perfil no encontrado para alias: {alias_key}')

def index(request):
    """Página de inicio pública; muestra si hay una sesión activa (cliente o empleado)."""
    session_type = 'none'
    nombre = None
    perfil = None
    panel_url = None
    logout_url = None

    # Detectar sesión de cliente
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        try:
            cliente = TblCliente.objects.get(id_cliente=cliente_id, b_activo=True)
            session_type = 'cliente'
            nombre = (cliente.s_primernombrecliente or '').strip() or 'Cliente'
            perfil = 'cliente'
            panel_url = 'reserfast:index_cliente'
            logout_url = 'reserfast:logout_cliente'
        except Exception:
            pass

    # Si no es cliente, detectar sesión de empleado
    if session_type == 'none' and request.session.get('id_usuario'):
        perfil = (request.session.get('perfil_usuario') or '').strip().lower() or 'admin'
        try:
            usuario = TblUsuario.objects.get(id_usuario=request.session.get('id_usuario'), b_activo=True)
            nombre = (usuario.s_nombreusuario or usuario.s_usuario or '').strip() or 'Usuario'
        except Exception:
            nombre = 'Usuario'
        session_type = 'empleado'
        if perfil == 'admin':
            panel_url = 'reserfast:index_admin'
        elif perfil == 'cocinero':
            panel_url = 'reserfast:gestion_cocina'
        else:
            panel_url = 'reserfast:panel_garzon'
        logout_url = 'reserfast:logout_empleado'

    context = {
        'session_type': session_type,
        'nombre_sesion': nombre,
        'perfil_sesion': perfil,
        'panel_url': panel_url,
        'logout_url': logout_url,
    }
    return render(request, 'reserfast/index.html', context)

@usuario_login_required
def index_admin(request):
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta pgina.')
        return redirect('reserfast:index')
    
    total_clientes = TblCliente.objects.filter(b_activo=True).count()
    total_garzones = TblUsuario.objects.filter(fk_id_perfil__s_nombreperfil__icontains='garz', b_activo=True).count()
    total_cocineros = TblUsuario.objects.filter(fk_id_perfil__s_nombreperfil__icontains='cocin', b_activo=True).count()
    total_mesas = TblMesa.objects.filter(b_activo=True).count()
    total_menus = TblMenu.objects.filter(b_activo=True).count()
    total_reservas = TblReserva.objects.filter(b_activo=True).count() if 'TblReserva' in globals() else 0

    garzones = TblUsuario.objects.filter(fk_id_perfil__s_nombreperfil__icontains='garz').order_by('s_nombreusuario')
    cocineros = TblUsuario.objects.filter(fk_id_perfil__s_nombreperfil__icontains='cocin').order_by('s_nombreusuario')
    mesas = TblMesa.objects.all().order_by('s_nombremesa')
    menus = TblMenu.objects.all().order_by('s_titulomenu')
    reservas = TblReserva.objects.all().order_by('-d_fechainicio') if 'TblReserva' in globals() else []
    usuarios_all = TblUsuario.objects.all().select_related('fk_id_perfil').order_by('s_nombreusuario')

    usuario = None
    try:
        usuario = TblUsuario.objects.get(id_usuario=request.session.get('id_usuario'))
    except Exception:
        pass
    fecha = timezone.now()

    ultimos_clientes = TblCliente.objects.filter(b_activo=True).order_by('-id_cliente')[:5]
    ultimos_menus = TblMenu.objects.filter(b_activo=True).order_by('-id_menu')[:5]
    perfiles = list(TblPerfil.objects.all())

    # Cargar estado de servicio desde tabla auxiliar
    service_status = {}
    try:
        db_path = settings.DATABASES['default']['NAME']
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tbl_estado_empleado (
                    id_usuario INTEGER PRIMARY KEY,
                    rol TEXT NOT NULL,
                    en_servicio INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute("SELECT id_usuario, en_servicio FROM tbl_estado_empleado")
            for uid, es in cur.fetchall():
                service_status[int(uid)] = bool(es)
    except Exception as e:
        logger.error(f"Error leyendo estado de servicio en admin: {e}")

    # Anotar estado en objetos para facilitar en template
    for g in garzones:
        try:
            setattr(g, 'en_servicio', service_status.get(g.id_usuario, False))
        except Exception:
            setattr(g, 'en_servicio', False)
    for c in cocineros:
        try:
            setattr(c, 'en_servicio', service_status.get(c.id_usuario, False))
        except Exception:
            setattr(c, 'en_servicio', False)

    # Contadores de "en servicio"
    try:
        garzones_en_servicio = sum(1 for g in garzones if getattr(g, 'en_servicio', False))
    except Exception:
        garzones_en_servicio = 0
    try:
        cocineros_en_servicio = sum(1 for c in cocineros if getattr(c, 'en_servicio', False))
    except Exception:
        cocineros_en_servicio = 0

    context = {
        'total_clientes': total_clientes,
        'total_garzones': total_garzones,
        'total_cocineros': total_cocineros,
        'total_mesas': total_mesas,
        'total_menus': total_menus,
        'total_reservas': total_reservas,
        'garzones': garzones,
        'cocineros': cocineros,
        'mesas': mesas,
        'menus': menus,
        'reservas': reservas,
        'usuario': usuario,
        'fecha': fecha,
        'ultimos_clientes': ultimos_clientes,
        'ultimos_menus': ultimos_menus,
    'service_status': service_status,
    'usuarios_all': usuarios_all,
    'perfiles': perfiles,
    'garzones_en_servicio': garzones_en_servicio,
    'cocineros_en_servicio': cocineros_en_servicio,
    }

    return render(request, 'reserfast/admin/index_admin.html', context)

@usuario_login_required
def panel_garzon(request):
    if request.session.get('perfil_usuario') != 'garzon':
        messages.error(request, 'No tienes permisos para acceder a esta pgina.')
        return redirect('reserfast:index')
    
    user_id = request.session.get('id_usuario')
    usuario = None
    try:
        usuario = TblUsuario.objects.get(id_usuario=user_id)
    except Exception:
        usuario = None
    
    db_path = settings.DATABASES['default']['NAME']
    en_servicio = False
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tbl_estado_empleado (
                    id_usuario INTEGER PRIMARY KEY,
                    rol TEXT NOT NULL,
                    en_servicio INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute("SELECT en_servicio FROM tbl_estado_empleado WHERE id_usuario = ?", (user_id,))
            row = cur.fetchone()
            if row:
                en_servicio = bool(row[0])
    except Exception as e:
        logger.error(f"Error al obtener estado de servicio: {e}")
    
    # Reservas de hoy con detalles
    hoy = timezone.now().date()
    reservas_hoy = []
    try:
        reservas = TblReserva.objects.filter(b_activo=True, d_fechainicio=hoy).select_related('fk_id_cliente')
        for r in reservas:
            mesa_rm = TblReservamesa.objects.filter(fk_id_reserva=r, b_activo=True).select_related('fk_id_mesa').first()
            menus_rm = TblReservamenu.objects.filter(fk_id_reserva=r, b_activo=True).select_related('fk_id_menu')
            reservas_hoy.append({
                'reserva': r,
                'cliente': r.fk_id_cliente,
                'mesa': mesa_rm.fk_id_mesa if (mesa_rm and mesa_rm.fk_id_mesa) else None,
                'menus': [rm.fk_id_menu for rm in menus_rm if rm.fk_id_menu],
            })
    except Exception as e:
        logger.error(f"Error construyendo reservas_hoy: {e}")
    
    context = {
        'en_servicio': en_servicio,
        'reservas_hoy': reservas_hoy,
        'usuario': usuario,
        'fecha': timezone.now(),
        'total_reservas': len(reservas_hoy),
    }
    
    return render(request, 'reserfast/garzon/panel_garzon.html', context)

@usuario_login_required
def gestion_cocina(request):
    if request.session.get('perfil_usuario') != 'cocinero':
        messages.error(request, 'No tienes permisos para acceder a esta pgina.')
        return redirect('reserfast:index')
    
    usuario = None
    try:
        usuario = TblUsuario.objects.get(id_usuario=request.session.get('id_usuario'))
    except Exception:
        pass
    fecha = timezone.now()

    menus_activos = TblMenu.objects.filter(b_activo=True).order_by('s_tipomenu', 's_titulomenu')
    menus_inactivos = TblMenu.objects.filter(b_activo=False).order_by('s_tipomenu', 's_titulomenu')
    total_menus = menus_activos.count()
    total_inactivos = menus_inactivos.count()

    categorias = {}
    for m in TblMenu.objects.all().order_by('s_tipomenu', 's_titulomenu'):
        cat = m.s_tipomenu or 'Sin tipo'
        categorias.setdefault(cat, []).append(m)

    # Estado de servicio del cocinero (reutilizar tabla auxiliar)
    en_servicio = False
    try:
        db_path = settings.DATABASES['default']['NAME']
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tbl_estado_empleado (
                    id_usuario INTEGER PRIMARY KEY,
                    rol TEXT NOT NULL,
                    en_servicio INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute("SELECT en_servicio FROM tbl_estado_empleado WHERE id_usuario = ?", (request.session.get('id_usuario'),))
            row = cur.fetchone()
            if row:
                en_servicio = bool(row[0])
    except Exception as e:
        logger.error(f"Error leyendo estado cocinero: {e}")

    context = {
        'usuario': usuario,
        'fecha': fecha,
        'menus_activos': menus_activos,
        'menus_inactivos': menus_inactivos,
        'total_menus': total_menus,
        'total_inactivos': total_inactivos,
        'categorias': categorias,
        'en_servicio': en_servicio,
    }
    
    return render(request, 'reserfast/cocina/menu_cocina.html', context)

@usuario_login_required
def toggle_menu_cocina(request, menu_id):
    """Activar/desactivar un men."""
    if request.session.get('perfil_usuario') != 'cocinero':
        messages.error(request, 'No tienes permisos para realizar esta accin.')
        return redirect('reserfast:index')
    
    try:
        menu = TblMenu.objects.get(id_menu=menu_id)
        menu.b_activo = not menu.b_activo
        menu.save()
        
        estado = "activado" if menu.b_activo else "desactivado"
        messages.success(request, f'Men "{menu.s_titulomenu}" {estado} exitosamente.')
    except TblMenu.DoesNotExist:
        messages.error(request, 'Men no encontrado.')
    
    return redirect('reserfast:gestion_cocina')

def login_admin(request):
    """Vista de login para administradores y empleados."""
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        password = request.POST.get('contrasena', '').strip()
        
        if not usuario or not password:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return render(request, 'reserfast/admin/login_admin.html')
        
        try:
            usuario_obj = TblUsuario.objects.get(s_usuario=usuario, b_activo=True)
            
            if bcrypt.checkpw(password.encode('utf-8'), usuario_obj.s_contrasenausuario.encode('utf-8')):
                request.session['id_usuario'] = usuario_obj.id_usuario
                raw_perfil = (usuario_obj.fk_id_perfil.s_nombreperfil if usuario_obj.fk_id_perfil else 'admin') or 'admin'
                perfil_norm = raw_perfil.strip().lower()
                mapping = {
                    'administrador': 'admin',
                    'admin': 'admin',
                    'garzon': 'garzon',
                    'garz�n': 'garzon',
                    'cocinero': 'cocinero',
                }
                request.session['perfil_usuario'] = mapping.get(perfil_norm, perfil_norm)
                
                messages.success(request, f'Bienvenido, {usuario_obj.s_nombreusuario}!')
                
                perfil = request.session.get('perfil_usuario')
                if perfil == 'admin':
                    return redirect('reserfast:index_admin')
                elif perfil == 'cocinero':
                    return redirect('reserfast:gestion_cocina')
                elif perfil == 'garzon':
                    return redirect('reserfast:panel_garzon')
                else:
                    return redirect('reserfast:index')
            else:
                messages.error(request, 'Usuario o contrasea incorrectos.')
        except TblUsuario.DoesNotExist:
            messages.error(request, 'Usuario o contrasea incorrectos.')
        except Exception as e:
            logger.error(f"Error en login_admin: {e}")
            messages.error(request, 'Error interno del servidor.')
    
    return render(request, 'reserfast/admin/login_admin.html')

def login_clientes(request):
    """Vista de login para clientes."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('contrasena', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email y contrasea son obligatorios.')
            return render(request, 'reserfast/clientes/login_clientes.html')
        
        try:
            cliente = TblCliente.objects.get(s_email=email, b_activo=True)
            
            if bcrypt.checkpw(password.encode('utf-8'), cliente.s_contrasena.encode('utf-8')):
                request.session['cliente_id'] = cliente.id_cliente
                
                messages.success(request, f'Bienvenido, {cliente.s_primernombrecliente}!')
                return redirect('reserfast:index_cliente')
            else:
                messages.error(request, 'Email o contrasea incorrectos.')
        except TblCliente.DoesNotExist:
            messages.error(request, 'Email o contrasea incorrectos.')
        except Exception as e:
            logger.error(f"Error en login_clientes: {e}")
            messages.error(request, 'Error interno del servidor.')
    
    return render(request, 'reserfast/clientes/login_clientes.html')

def logout_empleado(request):
    """Cerrar sesi�n de empleados."""
    request.session.flush()
    messages.success(request, 'Sesi�n cerrada exitosamente.')
    return redirect('reserfast:index')

def logout_cliente(request):
    """Cerrar sesi�n de clientes."""
    request.session.flush()
    messages.success(request, 'Sesi�n cerrada exitosamente.')
    return redirect('reserfast:index')

@usuario_login_required
def cambiar_password_empleado(request):
    """Cambiar contrasea de empleado."""
    user_id = request.session.get('id_usuario')
    if not user_id:
        return redirect('reserfast:login_admin')
    
    try:
        usuario = TblUsuario.objects.get(id_usuario=user_id)
    except TblUsuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('reserfast:login_admin')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'reserfast/cambiar_password.html')
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), usuario.s_contrasenausuario.encode('utf-8')):
            messages.error(request, 'La contrasea actual es incorrecta.')
            return render(request, 'reserfast/cambiar_password.html')
        
        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseas no coinciden.')
            return render(request, 'reserfast/cambiar_password.html')
        
        if len(new_password) < 6:
            messages.error(request, 'La nueva contrasea debe tener al menos 6 caracteres.')
            return render(request, 'reserfast/cambiar_password.html')
        
        try:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            usuario.s_contrasenausuario = hashed_password.decode('utf-8')
            usuario.save()
            
            messages.success(request, 'Contrasea cambiada exitosamente.')
            
            perfil = request.session.get('perfil_usuario')
            if perfil == 'admin':
                return redirect('reserfast:index_admin')
            elif perfil == 'cocinero':
                return redirect('reserfast:gestion_cocina')
            elif perfil == 'garzon':
                return redirect('reserfast:panel_garzon')
            else:
                return redirect('reserfast:index')
        except Exception as e:
            logger.error(f"Error al cambiar contrasea: {e}")
            messages.error(request, 'Error al cambiar la contrasea.')
    
    return render(request, 'reserfast/cambiar_password.html')

@cliente_login_required
def index_cliente(request):
    """Vista principal del cliente."""
    cliente = request.cliente  # Disponible a trav�s del decorador
    context = {'cliente': cliente}
    return render(request, 'reserfast/clientes/index_cliente.html', context)

@cliente_login_required
def menu_cliente(request):
    """Vista del men� para clientes."""
    menus = TblMenu.objects.filter(b_activo=True).order_by('s_titulomenu')
    # Agrupar en categorías esperadas por el template
    frio, caliente, almuerzos, bebidas = [], [], [], []
    for m in menus:
        tipo = (m.s_tipomenu or '').strip().lower()
        if 'entrada' in tipo:
            frio.append(m)
        elif 'rapida' in tipo or 'rápida' in tipo or 'rapido' in tipo or 'rápido' in tipo:
            caliente.append(m)
        elif 'almuerzo' in tipo:
            almuerzos.append(m)
        elif 'bebida' in tipo:
            bebidas.append(m)
        else:
            # Si no calza, se podría mostrar en "caliente" como fallback
            caliente.append(m)
    context = {
        'frio': frio,
        'caliente': caliente,
        'almuerzos': almuerzos,
        'bebidas': bebidas,
    }
    return render(request, 'reserfast/clientes/menu.html', context)

@cliente_login_required
def mesa_cliente(request):
    """Vista de mesas para clientes."""
    mesas = TblMesa.objects.filter(b_activo=True).order_by('s_nombremesa')
    return render(request, 'reserfast/clientes/mesas.html', {'mesas': mesas})

def create_clientes(request):
    """Crear nuevo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                cliente = form.save()
                messages.success(request, 'Cliente registrado exitosamente.')
                return redirect('reserfast:crear_exito')
            except Exception as e:
                logger.error(f"Error al crear cliente: {e}")
                messages.error(request, 'Error al registrar cliente.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ClienteForm()
    
    return render(request, 'reserfast/clientes/crear_cliente.html', {'form': form})

def crear_exito(request):
    """Vista de xito tras crear cliente."""
    return render(request, 'reserfast/clientes/crear_exito.html')

# Solo requiere sesión de cliente
@cliente_login_required
def perfil_cliente(request):
    """Ver perfil del cliente."""
    cliente = request.cliente  # Inyectado por el decorador
    # Datos adicionales para el perfil
    try:
        total_reservas = TblReserva.objects.filter(fk_id_cliente_id=cliente.id_cliente).count()
    except Exception:
        total_reservas = 0

    # Calcular edad si hay fecha de nacimiento
    edad = None
    try:
        if getattr(cliente, 'd_fecha_nacimiento', None):
            today = timezone.now().date()
            nacimiento = cliente.d_fecha_nacimiento
            edad = today.year - nacimiento.year - ((today.month, today.day) < (nacimiento.month, nacimiento.day))
    except Exception:
        edad = None

    context = {
        'cliente': cliente,
        'total_reservas': total_reservas,
        'edad': edad,
    }
    return render(request, 'reserfast/clientes/perfil_cliente.html', context)

@cliente_login_required
def editar_perfil_cliente(request):
    """Editar perfil del cliente."""
    cliente = request.cliente  # Disponible a trav�s del decorador
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=cliente, user=cliente)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('reserfast:perfil_cliente')
            except Exception as e:
                logger.error(f"Error al editar perfil: {e}")
                messages.error(request, 'Error al actualizar perfil.')
    else:
        form = EditarPerfilForm(instance=cliente, user=cliente)
    
    context = {'form': form, 'cliente': cliente}
    return render(request, 'reserfast/clientes/editar_perfil.html', context)

@usuario_login_required
def editar_perfil_empleado(request):
    """Permitir a garzón/cocinero/admin editar su propio perfil básico y contraseña."""
    user_id = request.session.get('id_usuario')
    try:
        usuario = TblUsuario.objects.get(id_usuario=user_id)
    except TblUsuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('reserfast:index')

    if request.method == 'POST':
        form = EditarPerfilEmpleadoForm(request.POST, instance=usuario, usuario_obj=usuario)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                perfil = request.session.get('perfil_usuario')
                if perfil == 'garzon':
                    return redirect('reserfast:panel_garzon')
                if perfil == 'cocinero':
                    return redirect('reserfast:gestion_cocina')
                return redirect('reserfast:index_admin')
            except Exception as e:
                logger.error(f"Error al actualizar perfil empleado: {e}")
                messages.error(request, 'Error al actualizar perfil.')
    else:
        form = EditarPerfilEmpleadoForm(instance=usuario, usuario_obj=usuario)

    return render(request, 'reserfast/empleados/editar_perfil.html', {'form': form, 'usuario': usuario})

# Funciones administrativas - Garzones
@usuario_login_required
def listar_garzones(request):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('reserfast:index')
    messages.info(request, 'La gestión de garzones ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

@usuario_login_required
def crear_garzones(request):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('reserfast:index')
    messages.info(request, 'Crear garzones ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

@usuario_login_required
def eliminar_garzones(request, id_usuario):
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta accin.')
        return redirect('reserfast:index')
    try:
        usuario = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil='garzon')
        usuario.b_activo = False
        usuario.save()
        messages.success(request, f'Garzn {usuario.s_nombreusuario} eliminado exitosamente.')
    except TblUsuario.DoesNotExist:
        messages.error(request, 'Garzn no encontrado.')
    except Exception as e:
        logger.error(f"Error al eliminar garzn: {e}")
        messages.error(request, 'Error al eliminar garzn.')
    return redirect('reserfast:admin_garzones')

@usuario_login_required
def actualizar_garzones(request, id_usuario):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('reserfast:index')
    messages.info(request, 'Actualizar garzones ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

# Funciones administrativas - Cocina
@usuario_login_required
def listar_usuarios_cocina(request):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('reserfast:index')
    messages.info(request, 'La gestión de cocineros ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

@usuario_login_required
def crear_usuarios_cocina(request):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('reserfast:index')
    messages.info(request, 'Crear usuarios de cocina ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

@usuario_login_required
def eliminar_usuarios_cocina(request, id_usuario):
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta accin.')
        return redirect('reserfast:index')
    try:
        usuario = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil='cocinero')
        usuario.b_activo = False
        usuario.save()
        messages.success(request, f'Usuario de cocina {usuario.s_nombreusuario} eliminado exitosamente.')
    except TblUsuario.DoesNotExist:
        messages.error(request, 'Usuario de cocina no encontrado.')
    except Exception as e:
        logger.error(f"Error al eliminar usuario de cocina: {e}")
        messages.error(request, 'Error al eliminar usuario de cocina.')
    return redirect('reserfast:admin_cocina')

@usuario_login_required
def actualizar_usuarios_cocina(request, id_usuario):
    """Deprecated: Redirect to consolidated admin dashboard."""
    if request.session.get('perfil_usuario') != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('reserfast:index')
    messages.info(request, 'Actualizar usuarios de cocina ahora se realiza en el Panel de Administración.')
    return redirect('reserfast:index_admin')

# Funciones de ventas y reservas
@cliente_login_required
def crear_venta(request):
    if request.method == 'POST':
        messages.success(request, 'Venta creada exitosamente.')
        return redirect('reserfast:index_cliente')
    return render(request, 'reserfast/clientes/crear_venta.html')

@cliente_login_required
def crear_reserva(request):
    """Crear una nueva reserva."""
    mesas_disponibles = TblMesa.objects.filter(b_activo=True).order_by('s_nombremesa')
    menus_disponibles = TblMenu.objects.filter(b_activo=True).order_by('s_titulomenu')
    
    if request.method == 'POST':
        form = CrearReservaForm(request.POST, mesas=mesas_disponibles, menus=menus_disponibles)
        
        if form.is_valid():
            try:
                from datetime import datetime
                
                fecha_reserva = form.cleaned_data['fecha_reserva']
                mesa = form.cleaned_data['mesa']
                menus_seleccionados = form.cleaned_data['menus']
                
                total_reserva = sum(menu.i_precio for menu in menus_seleccionados)
                
                reserva = TblReserva.objects.create(
                    fk_id_cliente_id=request.session.get('cliente_id'),
                    d_fechainicio=fecha_reserva,
                    i_totalreserva=total_reserva,
                    b_activo=True
                )
                
                TblReservamesa.objects.create(
                    fk_id_reserva=reserva,
                    fk_id_mesa=mesa,
                    b_activo=True
                )
                
                for menu in menus_seleccionados:
                    TblReservamenu.objects.create(
                        fk_id_reserva=reserva,
                        fk_id_menu=menu,
                        b_activo=True
                    )
                
                messages.success(request, f'Reserva creada exitosamente para la mesa {mesa.s_nombremesa}. Total: ${total_reserva:,}')
                return redirect('reserfast:mis_reservas')
                
            except Exception as e:
                logger.error(f"Error al crear reserva: {e}")
                messages.error(request, f'Error al crear la reserva: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CrearReservaForm(mesas=mesas_disponibles, menus=menus_disponibles)
    
    try:
        context = {
            'form': form,
            'mesas_disponibles': bool(mesas_disponibles),
            'mesas_list': mesas_disponibles,
            'mesas_count': mesas_disponibles.count(),
            'menus_disponibles': bool(menus_disponibles),
            'menus_list': menus_disponibles,
            'menus_count': menus_disponibles.count(),
            'debug_info': settings.DEBUG,
        }
        
        return render(request, 'reserfast/clientes/crear_reserva.html', context)
        
    except Exception as e:
        logger.error(f"Error al cargar datos para crear_reserva: {e}")
        messages.error(request, 'Error al cargar la p�gina de reservas.')
        return redirect('reserfast:index_cliente')

@cliente_login_required
def mis_reservas(request):
    """Ver todas las reservas del cliente."""
    cliente_id = request.session.get('cliente_id')
    
    try:
        reservas = TblReserva.objects.filter(
            fk_id_cliente_id=cliente_id
        ).order_by('-d_fechainicio')

        hoy = timezone.now().date()
        reservas_futuras, reservas_pasadas = [], []

        for reserva in reservas:
            mesa_rm = TblReservamesa.objects.filter(
                fk_id_reserva=reserva, b_activo=True
            ).select_related('fk_id_mesa').first()
            mesa = mesa_rm.fk_id_mesa if mesa_rm and mesa_rm.fk_id_mesa else None

            menus_rm = TblReservamenu.objects.filter(
                fk_id_reserva=reserva, b_activo=True
            ).select_related('fk_id_menu')
            menus = [rm.fk_id_menu for rm in menus_rm if rm.fk_id_menu]

            if not reserva.b_activo:
                estado = 'Cancelada'
            elif reserva.d_fechainicio and reserva.d_fechainicio < hoy:
                estado = 'Pasada'
            else:
                estado = 'Activa'

            detalle = {
                'reserva': reserva,
                'mesa': mesa,
                'menus': menus,
                'estado': estado,
            }

            if reserva.d_fechainicio and reserva.d_fechainicio >= hoy and reserva.b_activo:
                reservas_futuras.append(detalle)
            else:
                reservas_pasadas.append(detalle)

        context = {
            'tiene_reservas': bool(reservas_futuras or reservas_pasadas),
            'reservas_futuras': reservas_futuras,
            'reservas_pasadas': reservas_pasadas,
        }

        try:
            total_reservas_sistema = TblReserva.objects.count()
        except Exception:
            total_reservas_sistema = 0
        context['debug_info'] = {
            'cliente_id': cliente_id,
            'total_reservas_cliente': len(reservas),
            'total_reservas_sistema': total_reservas_sistema,
        } if settings.DEBUG else None

        return render(request, 'reserfast/clientes/mis_reservas.html', context)
        
    except Exception as e:
        logger.error(f"Error al cargar reservas: {e}")
        messages.error(request, 'Error al cargar las reservas.')
        return redirect('reserfast:index_cliente')

@cliente_login_required
def editar_reserva(request, reserva_id):
    """Editar una reserva existente con fecha, mesa y menús."""
    cliente_id = request.session.get('cliente_id')
    try:
        reserva = TblReserva.objects.get(id_reserva=reserva_id, fk_id_cliente_id=cliente_id, b_activo=True)
    except TblReserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
        return redirect('reserfast:mis_reservas')

    mesas_disponibles = TblMesa.objects.filter(b_activo=True).order_by('s_nombremesa')
    menus_disponibles = TblMenu.objects.filter(b_activo=True).order_by('s_titulomenu')

    # Valores actuales
    reserva_mesa = TblReservamesa.objects.filter(fk_id_reserva=reserva, b_activo=True).select_related('fk_id_mesa').first()
    menu_ids_actuales = list(TblReservamenu.objects.filter(fk_id_reserva=reserva, b_activo=True).values_list('fk_id_menu_id', flat=True))
    menu_ids_actuales_str = [str(mid) for mid in menu_ids_actuales]

    if request.method == 'POST':
        form = EditarReservaForm(request.POST, mesas=mesas_disponibles, menus=menus_disponibles, reserva=reserva)
        if form.is_valid():
            try:
                with transaction.atomic():
                    fecha_reserva = form.cleaned_data['fecha_reserva']
                    mesa = form.cleaned_data['mesa']
                    menus_seleccionados = list(form.cleaned_data['menus'])

                    # Actualizar cabecera
                    reserva.d_fechainicio = fecha_reserva
                    reserva.i_totalreserva = sum(int(m.i_precio or 0) for m in menus_seleccionados)
                    reserva.save()

                    # Actualizar mesa (desactivar anterior y crear/actualizar vínculo)
                    if reserva_mesa and reserva_mesa.fk_id_mesa_id != mesa.id_mesa:
                        reserva_mesa.b_activo = False
                        reserva_mesa.save()
                        TblReservamesa.objects.create(fk_id_reserva=reserva, fk_id_mesa=mesa, b_activo=True)
                    elif not reserva_mesa:
                        TblReservamesa.objects.create(fk_id_reserva=reserva, fk_id_mesa=mesa, b_activo=True)

                    # Actualizar menús
                    actuales_set = set(menu_ids_actuales)
                    nuevos_set = set(m.id_menu for m in menus_seleccionados)

                    # Desactivar menús removidos
                    for mid in actuales_set - nuevos_set:
                        TblReservamenu.objects.filter(fk_id_reserva=reserva, fk_id_menu_id=mid, b_activo=True).update(b_activo=False)

                    # Agregar nuevos
                    for mid in nuevos_set - actuales_set:
                        TblReservamenu.objects.create(fk_id_reserva=reserva, fk_id_menu_id=mid, b_activo=True)

                messages.success(request, 'Reserva actualizada exitosamente.')
                return redirect('reserfast:mis_reservas')
            except Exception as e:
                logger.error(f"Error al editar reserva: {e}")
                messages.error(request, 'Error al editar reserva.')
    else:
        initial = {
            'fecha_reserva': reserva.d_fechainicio,
            'mesa': reserva_mesa.fk_id_mesa if reserva_mesa and reserva_mesa.fk_id_mesa else None,
            'menus': menu_ids_actuales,
        }
        form = EditarReservaForm(initial=initial, mesas=mesas_disponibles, menus=menus_disponibles, reserva=reserva)

    context = {
        'form': form,
        'reserva': reserva,
        'reserva_mesa': reserva_mesa,
    'menu_ids_actuales_str': menu_ids_actuales_str,
    }
    return render(request, 'reserfast/clientes/editar_reserva.html', context)

@require_POST
@usuario_login_required
def ajax_toggle_empleado_servicio(request):
    """Alternar el estado de servicio del empleado actual (garzón/cocinero)."""
    try:
        user_id = request.session.get('id_usuario')
        rol = request.session.get('perfil_usuario')
        if not user_id or rol not in ('garzon', 'cocinero'):
            return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'})

        db_path = settings.DATABASES['default']['NAME']
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tbl_estado_empleado (
                    id_usuario INTEGER PRIMARY KEY,
                    rol TEXT NOT NULL,
                    en_servicio INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Leer estado actual
            cur.execute("SELECT en_servicio FROM tbl_estado_empleado WHERE id_usuario = ?", (user_id,))
            row = cur.fetchone()
            nuevo = 1
            if row:
                nuevo = 0 if row[0] == 1 else 1
                cur.execute("UPDATE tbl_estado_empleado SET en_servicio = ?, rol = ?, updated_at = CURRENT_TIMESTAMP WHERE id_usuario = ?", (nuevo, rol, user_id))
            else:
                cur.execute("INSERT INTO tbl_estado_empleado (id_usuario, rol, en_servicio) VALUES (?, ?, ?)", (user_id, rol, 1))
                nuevo = 1
            conn.commit()

        return JsonResponse({'success': True, 'en_servicio': bool(nuevo)})
    except Exception as e:
        logger.error(f"Error al alternar estado servicio: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

# =================== AJAX ADMIN: GARZONES / COCINEROS / MESAS ===================

def _require_admin(request):
    """Pequeña ayuda para verificar sesión y rol admin."""
    if not request.session.get('id_usuario'):
        return False
    return (request.session.get('perfil_usuario') or '').lower() == 'admin'

def _parse_json(request):
    try:
        if request.META.get('CONTENT_TYPE', '').startswith('application/json') and request.body:
            return json.loads(request.body.decode('utf-8'))
    except Exception:
        pass
    return {}

@require_POST
@usuario_login_required
def ajax_crear_garzon(request):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    nombre = (data.get('s_nombreusuario') or '').strip()
    p_ap = (data.get('s_primerapellidousuario') or '').strip()
    s_ap = (data.get('s_segundoapellidousuario') or '').strip()
    usuario_login = (data.get('s_usuario') or '').strip()
    password = (data.get('s_contrasenausuario') or '').strip()
    if not (nombre and p_ap and usuario_login and password):
        return JsonResponse({'success': False, 'mensaje': 'Campos requeridos faltantes.'})
    try:
        if TblUsuario.objects.filter(s_usuario=usuario_login).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya existe.'})
        perfil = resolve_perfil('garzon')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u = TblUsuario(
            s_nombreusuario=nombre,
            s_primerapellidousuario=p_ap,
            s_segundoapellidousuario=s_ap,
            s_usuario=usuario_login,
            s_contrasenausuario=hashed,
            b_activo=True,
            fk_id_perfil=perfil,
        )
        u.save()
        return JsonResponse({'success': True, 'mensaje': f'Garzón {nombre} creado.'})
    except TblPerfil.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Perfil garzón no configurado.'})
    except Exception as e:
        logger.error(f"ajax_crear_garzon error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_editar_garzon(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil__iexact='garzon')
        nombre = (data.get('s_nombreusuario') or u.s_nombreusuario or '').strip()
        p_ap = (data.get('s_primerapellidousuario') or u.s_primerapellidousuario or '').strip()
        s_ap = (data.get('s_segundoapellidousuario') or u.s_segundoapellidousuario or '').strip()
        usuario_login = (data.get('s_usuario') or u.s_usuario or '').strip()
        new_pass = (data.get('s_contrasenausuario') or '').strip()

        if not (nombre and p_ap and usuario_login):
            return JsonResponse({'success': False, 'mensaje': 'Nombre, primer apellido y usuario son obligatorios.'})

        if TblUsuario.objects.filter(s_usuario=usuario_login).exclude(id_usuario=u.id_usuario).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya está en uso.'})

        u.s_nombreusuario = nombre
        u.s_primerapellidousuario = p_ap
        u.s_segundoapellidousuario = s_ap
        u.s_usuario = usuario_login
        if new_pass:
            u.s_contrasenausuario = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Garzón actualizado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Garzón no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_editar_garzon error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_eliminar_garzon(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil__iexact='garzon')
        u.b_activo = False
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Garzón eliminado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Garzón no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_eliminar_garzon error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_crear_cocinero(request):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    nombre = (data.get('s_nombreusuario') or '').strip()
    p_ap = (data.get('s_primerapellidousuario') or '').strip()
    s_ap = (data.get('s_segundoapellidousuario') or '').strip()
    usuario_login = (data.get('s_usuario') or '').strip()
    password = (data.get('s_contrasenausuario') or '').strip()
    if not (nombre and p_ap and usuario_login and password):
        return JsonResponse({'success': False, 'mensaje': 'Campos requeridos faltantes.'})
    try:
        if TblUsuario.objects.filter(s_usuario=usuario_login).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya existe.'})
        perfil = resolve_perfil('cocinero')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u = TblUsuario(
            s_nombreusuario=nombre,
            s_primerapellidousuario=p_ap,
            s_segundoapellidousuario=s_ap,
            s_usuario=usuario_login,
            s_contrasenausuario=hashed,
            b_activo=True,
            fk_id_perfil=perfil,
        )
        u.save()
        return JsonResponse({'success': True, 'mensaje': f'Cocinero {nombre} creado.'})
    except TblPerfil.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Perfil cocinero no configurado.'})
    except Exception as e:
        logger.error(f"ajax_crear_cocinero error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_editar_cocinero(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil__iexact='cocinero')
        nombre = (data.get('s_nombreusuario') or u.s_nombreusuario or '').strip()
        p_ap = (data.get('s_primerapellidousuario') or u.s_primerapellidousuario or '').strip()
        s_ap = (data.get('s_segundoapellidousuario') or u.s_segundoapellidousuario or '').strip()
        usuario_login = (data.get('s_usuario') or u.s_usuario or '').strip()
        new_pass = (data.get('s_contrasenausuario') or '').strip()

        if not (nombre and p_ap and usuario_login):
            return JsonResponse({'success': False, 'mensaje': 'Nombre, primer apellido y usuario son obligatorios.'})

        if TblUsuario.objects.filter(s_usuario=usuario_login).exclude(id_usuario=u.id_usuario).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya está en uso.'})

        u.s_nombreusuario = nombre
        u.s_primerapellidousuario = p_ap
        u.s_segundoapellidousuario = s_ap
        u.s_usuario = usuario_login
        if new_pass:
            u.s_contrasenausuario = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Cocinero actualizado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Cocinero no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_editar_cocinero error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_eliminar_cocinero(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario, fk_id_perfil__s_nombreperfil__iexact='cocinero')
        u.b_activo = False
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Cocinero eliminado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Cocinero no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_eliminar_cocinero error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_crear_mesa(request):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    nombre = (data.get('s_nombremesa') or '').strip()
    ubicacion = (data.get('s_ubicacion') or '').strip()
    descripcion = (data.get('s_descripcionmesa') or '').strip()
    if not nombre:
        return JsonResponse({'success': False, 'mensaje': 'El nombre de la mesa es obligatorio.'})
    try:
        mesa = TblMesa(s_nombremesa=nombre, s_ubicacion=ubicacion or None, s_descripcionmesa=descripcion or None, b_activo=True)
        mesa.save()
        return JsonResponse({'success': True, 'mensaje': f'Mesa "{nombre}" creada.'})
    except Exception as e:
        logger.error(f"ajax_crear_mesa error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_editar_mesa(request, mesa_id):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    try:
        mesa = TblMesa.objects.get(id_mesa=mesa_id)
        nombre = (data.get('s_nombremesa') or mesa.s_nombremesa or '').strip()
        if not nombre:
            return JsonResponse({'success': False, 'mensaje': 'El nombre de la mesa es obligatorio.'})
        mesa.s_nombremesa = nombre
        mesa.s_descripcionmesa = (data.get('s_descripcionmesa') or '').strip() or None
        mesa.s_ubicacion = (data.get('s_ubicacion') or '').strip() or None
        mesa.save()
        return JsonResponse({'success': True, 'mensaje': 'Mesa actualizada.'})
    except TblMesa.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Mesa no encontrada.'})
    except Exception as e:
        logger.error(f"ajax_editar_mesa error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_eliminar_mesa(request, mesa_id):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    try:
        mesa = TblMesa.objects.get(id_mesa=mesa_id)
        mesa.b_activo = False
        mesa.save()
        return JsonResponse({'success': True, 'mensaje': 'Mesa eliminada.'})
    except TblMesa.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Mesa no encontrada.'})
    except Exception as e:
        logger.error(f"ajax_eliminar_mesa error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@cliente_login_required
def eliminar_reserva(request, reserva_id):
    """Eliminar una reserva."""
    cliente_id = request.session.get('cliente_id')
    try:
        reserva = TblReserva.objects.get(id_reserva=reserva_id, fk_id_cliente_id=cliente_id, b_activo=True)
        reserva.b_activo = False
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
    except TblReserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
    except Exception as e:
        logger.error(f"Error al eliminar reserva: {e}")
        messages.error(request, 'Error al cancelar reserva.')
    return redirect('reserfast:mis_reservas')

def verificar_disponibilidad_mesa(request, mesa_id):
    """Verificar si una mesa est� disponible en una fecha espec�fica."""
    if request.method == 'GET':
        fecha = request.GET.get('fecha')
        # Permitir excluir una reserva (al editar) para no contarla como conflicto
        exclude_reserva_id = request.GET.get('exclude_reserva_id')
        if not fecha:
            return JsonResponse({'disponible': False, 'mensaje': 'Fecha requerida.'})
        
        try:
            from datetime import datetime
            
            mesa = TblMesa.objects.get(id_mesa=mesa_id, b_activo=True)
            
            fecha_reserva = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            reservas_qs = TblReservamesa.objects.filter(
                fk_id_mesa=mesa,
                fk_id_reserva__d_fechainicio=fecha_reserva,
                fk_id_reserva__b_activo=True,
                b_activo=True
            )
            if exclude_reserva_id:
                try:
                    exclude_id_int = int(exclude_reserva_id)
                    reservas_qs = reservas_qs.exclude(fk_id_reserva_id=exclude_id_int)
                except Exception:
                    pass
            reservas_existentes = reservas_qs.exists()
            
            if reservas_existentes:
                return JsonResponse({
                    'disponible': False, 
                    'mensaje': f'La mesa {mesa.s_nombremesa} ya est� reservada para el {fecha}.',
                    'mesa': mesa.s_nombremesa
                })
            else:
                return JsonResponse({
                    'disponible': True, 
                    'mensaje': f'La mesa {mesa.s_nombremesa} est� disponible para el {fecha}.',
                    'mesa': mesa.s_nombremesa
                })
                
        except TblMesa.DoesNotExist:
            return JsonResponse({'disponible': False, 'mensaje': 'Mesa no encontrada.'})
        except ValueError:
            return JsonResponse({'disponible': False, 'mensaje': 'Formato de fecha inv�lido.'})
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {e}")
            return JsonResponse({'disponible': False, 'mensaje': 'Error al verificar disponibilidad.'})
    
    return JsonResponse({'disponible': False, 'mensaje': 'M�todo no permitido.'})

def detalle_reserva_ajax(request):
    if request.method == 'GET':
        reserva_id = request.GET.get('reserva_id')
        if not reserva_id:
            return JsonResponse({'success': False, 'mensaje': 'ID de reserva requerido.'})
        try:
            reserva = TblReserva.objects.get(id_reserva=reserva_id, b_activo=True)
            cliente = reserva.fk_id_cliente
            mesa_rm = TblReservamesa.objects.filter(
                fk_id_reserva=reserva, b_activo=True
            ).select_related('fk_id_mesa').first()
            mesa_nombre = mesa_rm.fk_id_mesa.s_nombremesa if mesa_rm and mesa_rm.fk_id_mesa else ''

            menus_rm = TblReservamenu.objects.filter(
                fk_id_reserva=reserva, b_activo=True
            ).select_related('fk_id_menu')
            menus_json = []
            for rm in menus_rm:
                m = rm.fk_id_menu
                if m:
                    menus_json.append({'nombre': m.s_titulomenu or '', 'precio': int(m.i_precio or 0)})
            data = {
                'success': True,
                'reserva': {
                    'id': reserva.id_reserva,
                    'fecha': reserva.d_fechainicio.strftime('%Y-%m-%d') if reserva.d_fechainicio else '',
                    'mesa': mesa_nombre,
                    'total': reserva.i_totalreserva or 0,
                    'menus': menus_json,
                    'cliente': {
                        'nombre': cliente.s_primernombrecliente or '',
                        'apellido': cliente.s_primerapellidocliente or '',
                        'telefono': cliente.s_telefono or '',
                        'email': cliente.s_email or '',
                    }
                }
            }
            return JsonResponse(data)
        except TblReserva.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Reserva no encontrada.'})
        except Exception as e:
            logger.error(f"Error al obtener detalle de reserva: {e}")
            return JsonResponse({'success': False, 'mensaje': 'Error al obtener detalles.'})
    return JsonResponse({'success': False, 'mensaje': 'Mtodo no permitido.'})

@usuario_login_required
def editar_mesa(request, mesa_id):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('reserfast:login_clientes')
    mesa = get_object_or_404(TblMesa, id_mesa=mesa_id)
    if request.method == 'POST':
        form = EditarMesaForm(request.POST, instance=mesa)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Mesa actualizada exitosamente!')
                return redirect('reserfast:mesas')
            except Exception as e:
                logger.error(f"Error al editar mesa: {e}")
                messages.error(request, 'Error al actualizar mesa.')
    else:
        form = EditarMesaForm(instance=mesa)
    return render(request, 'reserfast/clientes/editar_mesa.html', {'form': form, 'mesa': mesa})

@usuario_login_required
def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(TblMesa, id_mesa=mesa_id)
    if request.method == 'POST':
        mesa.b_activo = False
        mesa.save()
        messages.success(request, 'Mesa eliminada exitosamente!')
        return redirect('reserfast:mesas')
    return render(request, 'reserfast/clientes/eliminar_mesa.html', {'mesa': mesa})

# =================== FUNCIONES PARA GESTIN DE MENS ===================

@usuario_login_required
def crear_menu_cocina(request):
    """Crear un nuevo men desde la interfaz de cocina."""
    if request.session.get('perfil_usuario') not in ('cocinero', 'admin'):
        return JsonResponse({'success': False, 'mensaje': 'No tienes permisos para realizar esta accin.'})
    
    if request.method == 'POST':
        try:
            # Datos esperados desde el front
            titulo = request.POST.get('s_titulomenu', '').strip()
            descripcion = request.POST.get('s_descripcionmenu', '').strip()
            precio = request.POST.get('i_precio', '').strip()
            tipo = request.POST.get('s_tipomenu', '').strip()

            if not all([titulo, descripcion, precio, tipo]):
                return JsonResponse({'success': False, 'mensaje': 'Todos los campos son obligatorios.'})

            try:
                precio_int = int(precio)
                if precio_int <= 0:
                    return JsonResponse({'success': False, 'mensaje': 'El precio debe ser mayor a 0.'})
            except ValueError:
                return JsonResponse({'success': False, 'mensaje': 'Precio invlido.'})

            # Unicidad b�sica por t�tulo
            if TblMenu.objects.filter(s_titulomenu=titulo).exists():
                return JsonResponse({'success': False, 'mensaje': 'Ya existe un men con ese ttulo.'})

            nuevo_menu = TblMenu(
                s_titulomenu=titulo,
                s_descripcionmenu=descripcion,
                s_tipomenu=tipo,
                i_precio=precio_int,
                b_activo=True
            )

            # Asignar usuario creador si disponible
            try:
                usuario = TblUsuario.objects.get(id_usuario=request.session.get('id_usuario'))
                nuevo_menu.fk_id_usuario = usuario
            except Exception:
                pass

            # Manejar imagen si se proporciona
            if 's_imagen' in request.FILES:
                imagen = request.FILES['s_imagen']
                # Validar tama�o de archivo (m�ximo 5MB)
                if imagen.size > 5 * 1024 * 1024:
                    return JsonResponse({'success': False, 'mensaje': 'La imagen no puede ser mayor a 5MB.'})
                tipos_permitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                if imagen.content_type not in tipos_permitidos:
                    return JsonResponse({'success': False, 'mensaje': 'Tipo de archivo no permitido. Use JPG, PNG, GIF o WebP.'})
                nuevo_menu.s_imagen = imagen

            nuevo_menu.save()

            return JsonResponse({'success': True, 'mensaje': f'Men "{titulo}" creado exitosamente.'})
            
        except Exception as e:
            logger.error(f"Error al crear men: {e}")
            return JsonResponse({'success': False, 'mensaje': 'Error interno del servidor.'})
    
    return JsonResponse({'success': False, 'mensaje': 'Mtodo no permitido.'})


# =================== AJAX ADMIN: USUARIOS GENERALES ===================

@require_POST
@usuario_login_required
def ajax_crear_usuario(request):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    nombre = (data.get('s_nombreusuario') or '').strip()
    p_ap = (data.get('s_primerapellidousuario') or '').strip()
    s_ap = (data.get('s_segundoapellidousuario') or '').strip()
    usuario_login = (data.get('s_usuario') or '').strip()
    password = (data.get('s_contrasenausuario') or '').strip()
    perfil_alias = (data.get('perfil') or '').strip()  # 'admin'|'garzon'|'cocinero' u otro nombre existente
    if not (nombre and p_ap and usuario_login and password and perfil_alias):
        return JsonResponse({'success': False, 'mensaje': 'Campos requeridos faltantes.'})
    try:
        if TblUsuario.objects.filter(s_usuario=usuario_login).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya existe.'})
        try:
            perfil = resolve_perfil(perfil_alias)
        except TblPerfil.DoesNotExist:
            # probar por id numérico
            try:
                perfil = TblPerfil.objects.get(id_perfil=int(perfil_alias))
            except Exception:
                return JsonResponse({'success': False, 'mensaje': 'Perfil no encontrado.'})
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u = TblUsuario(
            s_nombreusuario=nombre,
            s_primerapellidousuario=p_ap,
            s_segundoapellidousuario=s_ap,
            s_usuario=usuario_login,
            s_contrasenausuario=hashed,
            b_activo=True,
            fk_id_perfil=perfil,
        )
        u.save()
        return JsonResponse({'success': True, 'mensaje': f'Usuario {nombre} creado.'})
    except Exception as e:
        logger.error(f"ajax_crear_usuario error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_editar_usuario(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    data = _parse_json(request)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario)
        nombre = (data.get('s_nombreusuario') or u.s_nombreusuario or '').strip()
        p_ap = (data.get('s_primerapellidousuario') or u.s_primerapellidousuario or '').strip()
        s_ap = (data.get('s_segundoapellidousuario') or u.s_segundoapellidousuario or '').strip()
        usuario_login = (data.get('s_usuario') or u.s_usuario or '').strip()
        new_pass = (data.get('s_contrasenausuario') or '').strip()
        perfil_alias = (data.get('perfil') or '').strip()

        if not (nombre and p_ap and usuario_login):
            return JsonResponse({'success': False, 'mensaje': 'Nombre, primer apellido y usuario son obligatorios.'})

        if TblUsuario.objects.filter(s_usuario=usuario_login).exclude(id_usuario=u.id_usuario).exists():
            return JsonResponse({'success': False, 'mensaje': 'El usuario ya está en uso.'})

        u.s_nombreusuario = nombre
        u.s_primerapellidousuario = p_ap
        u.s_segundoapellidousuario = s_ap
        u.s_usuario = usuario_login
        if perfil_alias:
            try:
                perfil = resolve_perfil(perfil_alias)
            except TblPerfil.DoesNotExist:
                try:
                    perfil = TblPerfil.objects.get(id_perfil=int(perfil_alias))
                except Exception:
                    perfil = None
            if perfil:
                u.fk_id_perfil = perfil
        if new_pass:
            u.s_contrasenausuario = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Usuario actualizado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Usuario no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_editar_usuario error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})

@require_POST
@usuario_login_required
def ajax_eliminar_usuario(request, id_usuario):
    if not _require_admin(request):
        return JsonResponse({'success': False, 'mensaje': 'Permisos insuficientes.'}, status=403)
    try:
        u = TblUsuario.objects.get(id_usuario=id_usuario)
        u.b_activo = False
        u.save()
        return JsonResponse({'success': True, 'mensaje': 'Usuario eliminado.'})
    except TblUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Usuario no encontrado.'})
    except Exception as e:
        logger.error(f"ajax_eliminar_usuario error: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno.'})
@usuario_login_required
def editar_menu_cocina(request, menu_id):
    """Editar un men existente desde la interfaz de cocina."""
    if request.session.get('perfil_usuario') not in ('cocinero', 'admin'):
        return JsonResponse({'success': False, 'mensaje': 'No tienes permisos para realizar esta accin.'})
    
    try:
        menu = TblMenu.objects.get(id_menu=menu_id)
    except TblMenu.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Men no encontrado.'})
    
    if request.method == 'GET':
        # Devolver datos del men� para edici�n (solo si se usa modo cargar)
        return JsonResponse({
            'success': True,
            'menu': {
                'id': menu.id_menu,
                's_titulomenu': menu.s_titulomenu,
                's_descripcionmenu': menu.s_descripcionmenu,
                'i_precio': menu.i_precio or 0,
                's_tipomenu': menu.s_tipomenu,
                'activo': menu.b_activo,
                'imagen_url': menu.s_imagen.url if menu.s_imagen else '/static/index_img/default-menu.jpg'
            }
        })
    
    elif request.method == 'POST':
        try:
            # Datos esperados desde el front
            titulo = request.POST.get('s_titulomenu', '').strip()
            descripcion = request.POST.get('s_descripcionmenu', '').strip()
            precio = request.POST.get('i_precio', '').strip()
            tipo = request.POST.get('s_tipomenu', '').strip()

            if not all([titulo, descripcion, precio, tipo]):
                return JsonResponse({'success': False, 'mensaje': 'Todos los campos son obligatorios.'})

            try:
                precio_int = int(precio)
                if precio_int <= 0:
                    return JsonResponse({'success': False, 'mensaje': 'El precio debe ser mayor a 0.'})
            except ValueError:
                return JsonResponse({'success': False, 'mensaje': 'Precio invlido.'})

            # Validar que el t�tulo no exista en otro men�
            if TblMenu.objects.filter(s_titulomenu=titulo).exclude(id_menu=menu_id).exists():
                return JsonResponse({'success': False, 'mensaje': 'Ya existe otro men con ese ttulo.'})

            # Actualizar campos
            menu.s_titulomenu = titulo
            menu.s_descripcionmenu = descripcion
            menu.s_tipomenu = tipo
            menu.i_precio = precio_int

            # Manejar nueva imagen si se proporciona
            if 's_imagen' in request.FILES:
                imagen = request.FILES['s_imagen']
                # Validar tama�o de archivo (m�ximo 5MB)
                if imagen.size > 5 * 1024 * 1024:
                    return JsonResponse({'success': False, 'mensaje': 'La imagen no puede ser mayor a 5MB.'})
                tipos_permitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                if imagen.content_type not in tipos_permitidos:
                    return JsonResponse({'success': False, 'mensaje': 'Tipo de archivo no permitido. Use JPG, PNG, GIF o WebP.'})
                menu.s_imagen = imagen

            menu.save()

            return JsonResponse({'success': True, 'mensaje': f'Men "{titulo}" actualizado exitosamente.'})
            
        except Exception as e:
            logger.error(f"Error al editar men: {e}")
            return JsonResponse({'success': False, 'mensaje': 'Error interno del servidor.'})
    
    return JsonResponse({'success': False, 'mensaje': 'Mtodo no permitido.'})

@usuario_login_required
def eliminar_menu_cocina(request, menu_id):
    """Eliminar (desactivar) un men desde la interfaz de cocina."""
    if request.session.get('perfil_usuario') not in ('cocinero', 'admin'):
        return JsonResponse({'success': False, 'mensaje': 'No tienes permisos para realizar esta accin.'})
    
    if request.method == 'POST':
        try:
            menu = TblMenu.objects.get(id_menu=menu_id)
            titulo_menu = menu.s_titulomenu
            
            # Desactivar el men en lugar de eliminarlo fsicamente
            menu.b_activo = False
            menu.save()
            
            return JsonResponse({
                'success': True, 
                'mensaje': f'Men "{titulo_menu}" eliminado exitosamente.'
            })
            
        except TblMenu.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Men no encontrado.'})
        except Exception as e:
            logger.error(f"Error al eliminar men: {e}")
            return JsonResponse({'success': False, 'mensaje': 'Error interno del servidor.'})
    
    return JsonResponse({'success': False, 'mensaje': 'Mtodo no permitido.'})

@usuario_login_required
def ajax_toggle_menu_cocina(request, menu_id):
    """Activar o desactivar un men� v�a AJAX."""
    if request.session.get('perfil_usuario') not in ('cocinero', 'admin'):
        return JsonResponse({'success': False, 'mensaje': 'No tienes permisos para realizar esta accin.'})

    if request.method != 'POST':
        return JsonResponse({'success': False, 'mensaje': 'Mtodo no permitido.'})

    try:
        menu = TblMenu.objects.get(id_menu=menu_id)
        menu.b_activo = not menu.b_activo
        menu.save()
        estado = 'activado' if menu.b_activo else 'desactivado'
        return JsonResponse({'success': True, 'mensaje': f'Men "{menu.s_titulomenu}" {estado} exitosamente.'})
    except TblMenu.DoesNotExist:
        return JsonResponse({'success': False, 'mensaje': 'Men no encontrado.'})
    except Exception as e:
        logger.error(f"Error al cambiar estado del men: {e}")
        return JsonResponse({'success': False, 'mensaje': 'Error interno del servidor.'})

    




