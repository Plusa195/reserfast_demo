from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import bcrypt
from reserfast_app.models import TblUsuario, TblCliente, TblPerfil, TblGenero

class Command(BaseCommand):
    help = 'Configura datos iniciales para hacer ReserFast autodidáctico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Configurando ReserFast para ser autodidáctico...'))
        
        perfiles = {
            'Administrador': 'Control total del sistema',
            'Garzon': 'Gestión de reservas y mesas',
            'Cocina': 'Gestión de menús y pedidos'
        }
        
        for nombre, descripcion in perfiles.items():
            perfil, created = TblPerfil.objects.get_or_create(
                s_nombreperfil=nombre,
                defaults={'b_activo': True}
            )
            if created:
                self.stdout.write(f'✅ Perfil creado: {nombre}')
            else:
                self.stdout.write(f'ℹ️  Perfil ya existe: {nombre}')
        
        generos = ['Masculino', 'Femenino', 'Otro']
        
        for nombre in generos:
            genero, created = TblGenero.objects.get_or_create(
                s_nombregenero=nombre,
                defaults={'b_activo': True}
            )
            if created:
                self.stdout.write(f'✅ Género creado: {nombre}')
            else:
                self.stdout.write(f'ℹ️  Género ya existe: {nombre}')
        
        usuarios_ejemplo = [
            {
                'usuario': 'garzon1',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'perfil': 'Garzon',
                'password': 'garzon123'
            },
            {
                'usuario': 'cocina1',
                'nombre': 'María',
                'apellido': 'González',
                'perfil': 'Cocina',
                'password': 'cocina123'
            }
        ]
        
        for usuario_data in usuarios_ejemplo:
            if not TblUsuario.objects.filter(s_usuario=usuario_data['usuario']).exists():
                perfil = TblPerfil.objects.get(s_nombreperfil=usuario_data['perfil'])
                password_hash = bcrypt.hashpw(usuario_data['password'].encode('utf-8'), bcrypt.gensalt())
                
                TblUsuario.objects.create(
                    s_usuario=usuario_data['usuario'],
                    s_nombreusuario=usuario_data['nombre'],
                    s_primerapellidousuario=usuario_data['apellido'],
                    s_contrasenausuario=password_hash.decode('utf-8'),
                    fk_id_perfil=perfil,
                    b_activo=True
                )
                self.stdout.write(f'✅ Usuario creado: {usuario_data["usuario"]} (contraseña: {usuario_data["password"]})')
            else:
                self.stdout.write(f'ℹ️  Usuario ya existe: {usuario_data["usuario"]}')
        
        if not TblCliente.objects.filter(s_email='cliente@ejemplo.com').exists():
            genero = TblGenero.objects.get(s_nombregenero='Masculino')
            password_hash = bcrypt.hashpw('cliente123'.encode('utf-8'), bcrypt.gensalt())
            
            TblCliente.objects.create(
                s_primernombrecliente='Carlos',
                s_primerapellidocliente='Rodríguez',
                s_email='cliente@ejemplo.com',
                s_rut='12345678-9',
                s_contrasena=password_hash.decode('utf-8'),
                fk_id_genero=genero,
                s_telefono='+56912345678',
                b_activo=True
            )
            self.stdout.write('✅ Cliente de ejemplo creado: cliente@ejemplo.com (contraseña: cliente123)')
        else:
            self.stdout.write('ℹ️  Cliente de ejemplo ya existe')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡ReserFast configurado exitosamente!'))
        self.stdout.write('\n📋 CREDENCIALES DE ACCESO:')
        self.stdout.write('=' * 50)
        self.stdout.write('🔧 ADMIN DJANGO: http://127.0.0.1:8000/admin/')
        self.stdout.write('   Usuario: admin')
        self.stdout.write('   (usa tu contraseña de superusuario)')
        self.stdout.write('')
        self.stdout.write('👥 USUARIOS DEL SISTEMA:')
        self.stdout.write('   • garzon1 / garzon123 (Perfil: Garzón)')
        self.stdout.write('   • cocina1 / cocina123 (Perfil: Cocina)')
        self.stdout.write('')
        self.stdout.write('👤 CLIENTE DE EJEMPLO:')
        self.stdout.write('   • cliente@ejemplo.com / cliente123')
        self.stdout.write('')
        self.stdout.write('🚀 FUNCIONALIDADES DISPONIBLES:')
        self.stdout.write('   ✅ Gestión completa de usuarios desde admin')
        self.stdout.write('   ✅ Cambio de contraseñas desde admin')
        self.stdout.write('   ✅ Gestión de clientes con perfiles')
        self.stdout.write('   ✅ Roles y permisos diferenciados')
        self.stdout.write('   ✅ Interfaz de cliente funcional')
        self.stdout.write('')
        self.stdout.write('💡 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Accede al admin en /admin/')
        self.stdout.write('   2. Explora la gestión de usuarios y clientes')
        self.stdout.write('   3. Prueba cambiar contraseñas')
        self.stdout.write('   4. Crea nuevos usuarios según necesidades')
        self.stdout.write('')
