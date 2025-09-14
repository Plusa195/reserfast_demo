# Deployment Guide - ReserFast

## 🚀 Desarrollo Local

### Configuración del Entorno Virtual

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/reserfast_demo.git
cd reserfast_demo

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración de la Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales (opcional)
python manage.py loaddata fixtures/initial_data.json
```

### Ejecutar el Servidor de Desarrollo

```bash
# Verificar configuración
python manage.py check

# Ejecutar servidor
python manage.py runserver
```

## 🌐 Acceso a la Aplicación

- **Aplicación principal**: http://localhost:8000/
- **Panel de administración**: http://localhost:8000/admin/
- **API endpoints**: http://localhost:8000/api/

## 📁 Estructura de URLs

```
/                   # Página principal
/admin/             # Panel administrativo Django
/login/             # Login de clientes
/logout/            # Logout
/registro/          # Registro de clientes
/perfil/            # Perfil de usuario
/menu/              # Menú público
/reservas/          # Sistema de reservas
/admin_panel/       # Panel de administración personalizado
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita las variables según tu entorno:
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: True para desarrollo, False para producción
- `DATABASE_URL`: URL de la base de datos (opcional)

### Configuración de Medios

Para desarrollo local, los archivos de medios se sirven automáticamente.
Para producción, configura un servidor de archivos estáticos.

## 🐳 Docker (Opcional)

```dockerfile
# Dockerfile de ejemplo
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📊 Base de Datos

### Modelos Principales

- **TblCliente**: Gestión de clientes
- **TblUsuario**: Sistema de usuarios
- **TblMesa**: Gestión de mesas
- **TblReserva**: Sistema de reservas
- **TblMenu**: Menú y productos

### Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Ver SQL de migraciones
python manage.py sqlmigrate reserfast_app 0001

# Resetear base de datos
python manage.py flush
```

## 🔍 Resolución de Problemas

### Error: "No module named 'django'"
```bash
# Verificar que el entorno virtual esté activado
which python  # Linux/macOS
where python   # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de migraciones
```bash
# Resetear migraciones
python manage.py migrate --fake-initial
```

### Problemas con archivos estáticos
```bash
# Recolectar archivos estáticos
python manage.py collectstatic
```

## 📈 Características Implementadas

- ✅ Sistema de autenticación personalizado
- ✅ Panel de administración completo
- ✅ Gestión de reservas
- ✅ Menú dinámico con imágenes
- ✅ Sistema de perfiles de usuario
- ✅ Responsive design con Bootstrap 5
- ✅ AJAX para operaciones dinámicas
- ⚠️ Funciones AJAX avanzadas (comentadas para demo)

## 🚀 Próximos Pasos

1. Implementar funciones AJAX comentadas en `urls.py`
2. Añadir sistema de notificaciones
3. Integrar pagos en línea
4. Implementar websockets para actualizaciones en tiempo real
5. Añadir tests unitarios y de integración

## 📝 Notas de Desarrollo

- Las URLs AJAX están comentadas para mantener la funcionalidad básica
- Para habilitar funcionalidades avanzadas, descomenta las URLs en `reserfast_app/urls.py`
- El proyecto está optimizado para demostración y portafolio
