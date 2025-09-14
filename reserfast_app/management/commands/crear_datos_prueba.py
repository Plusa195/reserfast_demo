from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from reserfast_app.models import (
    TblCliente, TblMesa, TblMenu, TblGenero, 
    TblReserva, TblReservamesa, TblReservamenu
)
from datetime import date, timedelta
import bcrypt

class Command(BaseCommand):
    help = 'Crear datos de prueba para el sistema de reservas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando datos de prueba...'))
        
        # Crear un género si no existe
        genero, created = TblGenero.objects.get_or_create(
            s_nombregenero='No especificado',
            defaults={'b_activo': True}
        )
        
        # Crear cliente de prueba
        password = 'test123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cliente, created = TblCliente.objects.get_or_create(
            s_email='cliente@test.com',
            defaults={
                's_primernombrecliente': 'Cliente',
                's_segundonombre': 'De',
                's_apellidopaternocli': 'Prueba',
                's_apellidomaternocliente': 'Test',
                's_rut': '12345678-9',
                's_contrasena': hashed_password,
                'd_fechanacimiento': date(1990, 1, 1),
                'fk_id_genero': genero,
                's_telefono': '+56912345678',
                's_direccion': 'Calle Falsa 123',
                'b_activo': True
            }
        )
        
        if created:
            self.stdout.write(f'Cliente creado: {cliente.s_email}')
        else:
            self.stdout.write(f'Cliente ya existe: {cliente.s_email}')
        
        # Verificar mesas
        mesas_count = TblMesa.objects.filter(b_activo=True).count()
        self.stdout.write(f'Mesas activas encontradas: {mesas_count}')
        
        if mesas_count == 0:
            # Crear mesas de prueba
            mesas_datos = [
                {'nombre': 'Mesa 1', 'descripcion': 'Mesa para 2 personas', 'ubicacion': 'Ventana'},
                {'nombre': 'Mesa 2', 'descripcion': 'Mesa para 4 personas', 'ubicacion': 'Centro'},
                {'nombre': 'Mesa 3', 'descripcion': 'Mesa para 6 personas', 'ubicacion': 'Terraza'},
                {'nombre': 'Mesa VIP', 'descripcion': 'Mesa VIP para 8 personas', 'ubicacion': 'Privado'},
            ]
            
            for mesa_data in mesas_datos:
                mesa = TblMesa.objects.create(
                    s_nombremesa=mesa_data['nombre'],
                    s_descripcionmesa=mesa_data['descripcion'],
                    s_ubicacion=mesa_data['ubicacion'],
                    d_fechacreacion=date.today(),
                    b_ocupado=0,
                    b_activo=True
                )
                self.stdout.write(f'Mesa creada: {mesa.s_nombremesa}')
        
        # Verificar menús
        menus_count = TblMenu.objects.filter(b_activo=True).count()
        self.stdout.write(f'Menús activos encontrados: {menus_count}')
        
        if menus_count == 0:
            # Crear menús de prueba
            menus_datos = [
                {'titulo': 'Pizza Margherita', 'descripcion': 'Pizza clásica con tomate y mozzarella', 'precio': 12000, 'categoria': 'Plato Principal'},
                {'titulo': 'Hamburguesa Clásica', 'descripcion': 'Hamburguesa con carne, lechuga y tomate', 'precio': 8000, 'categoria': 'Plato Principal'},
                {'titulo': 'Ensalada César', 'descripcion': 'Ensalada fresca con pollo y aderezo César', 'precio': 6000, 'categoria': 'Ensalada'},
                {'titulo': 'Tiramisu', 'descripcion': 'Postre italiano clásico', 'precio': 4000, 'categoria': 'Postre'},
                {'titulo': 'Coca Cola', 'descripcion': 'Bebida gaseosa 350ml', 'precio': 2000, 'categoria': 'Bebida'},
            ]
            
            for menu_data in menus_datos:
                menu = TblMenu.objects.create(
                    s_titulomenu=menu_data['titulo'],
                    s_descripcionmenu=menu_data['descripcion'],
                    i_precio=menu_data['precio'],
                    s_categoria=menu_data['categoria'],
                    s_tiempopreparacion='15-20 min',
                    d_fechacreacion=date.today(),
                    b_activo=True
                )
                self.stdout.write(f'Menú creado: {menu.s_titulomenu}')
        
        # Crear una reserva de ejemplo
        mesas = TblMesa.objects.filter(b_activo=True)[:1]
        menus = TblMenu.objects.filter(b_activo=True)[:2]
        
        if mesas and menus:
            # Verificar si ya existe una reserva para este cliente
            reserva_existente = TblReserva.objects.filter(
                fk_id_cliente=cliente,
                d_fechainicio=date.today() + timedelta(days=1)
            ).first()
            
            if not reserva_existente:
                # Crear reserva
                total = sum(menu.i_precio for menu in menus)
                reserva = TblReserva.objects.create(
                    fk_id_cliente=cliente,
                    d_fechainicio=date.today() + timedelta(days=1),
                    i_totalreserva=total,
                    b_activo=True
                )
                
                # Asociar mesa
                TblReservamesa.objects.create(
                    fk_id_reserva=reserva,
                    fk_id_mesa=mesas[0],
                    b_activo=True
                )
                
                # Asociar menús
                for menu in menus:
                    TblReservamenu.objects.create(
                        fk_id_reserva=reserva,
                        fk_id_menu=menu,
                        b_activo=True
                    )
                
                self.stdout.write(f'Reserva de ejemplo creada para mañana')
            else:
                self.stdout.write('Ya existe una reserva de ejemplo')
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de prueba creados exitosamente'))
        self.stdout.write('📋 Credenciales de prueba:')
        self.stdout.write(f'   Email: cliente@test.com')
        self.stdout.write(f'   Contraseña: test123')
