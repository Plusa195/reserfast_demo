from .models import TblCliente, TblUsuario

def session_info(request):
    """Inyecta información de sesión (cliente/empleado) en todos los templates.

    Provides `current_session` with keys:
    - is_authenticated: bool
    - type: 'cliente' | 'empleado' | None
    - perfil: 'cliente' | 'admin' | 'cocinero' | 'garzon' | None
    - nombre: display name
    - panel_url_name: Django url name for panel
    - logout_url_name: Django url name for logout
    """
    data = {
        'is_authenticated': False,
        'type': None,
        'perfil': None,
        'nombre': None,
        'panel_url_name': None,
        'logout_url_name': None,
    }

    # Sesión de cliente primero
    try:
        cid = request.session.get('cliente_id')
        if cid:
            try:
                c = TblCliente.objects.get(id_cliente=cid, b_activo=True)
                data.update({
                    'is_authenticated': True,
                    'type': 'cliente',
                    'perfil': 'cliente',
                    'nombre': (c.s_primernombrecliente or '').strip() or 'Cliente',
                    'panel_url_name': 'reserfast:index_cliente',
                    'logout_url_name': 'reserfast:logout_cliente',
                })
                return {'current_session': data}
            except Exception:
                pass
    except Exception:
        pass

    # Sesión de empleado
    try:
        uid = request.session.get('id_usuario')
        if uid:
            perfil = (request.session.get('perfil_usuario') or '').strip().lower() or 'admin'
            try:
                u = TblUsuario.objects.get(id_usuario=uid, b_activo=True)
                nombre = (u.s_nombreusuario or u.s_usuario or '').strip() or 'Usuario'
            except Exception:
                nombre = 'Usuario'

            panel = 'reserfast:index_admin'
            if perfil == 'cocinero':
                panel = 'reserfast:gestion_cocina'
            elif perfil == 'garzon':
                panel = 'reserfast:panel_garzon'

            data.update({
                'is_authenticated': True,
                'type': 'empleado',
                'perfil': perfil or 'admin',
                'nombre': nombre,
                'panel_url_name': panel,
                'logout_url_name': 'reserfast:logout_empleado',
            })
    except Exception:
        pass

    return {'current_session': data}
