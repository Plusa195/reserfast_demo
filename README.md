# 🍽️ ReserFast - Sistema de Gestión de Restaurantes

![Python](https://i### 🏗️ Configuración en 5 pasos

1. **📥 Clonar repositorio**
   ```bash
   git clone https://github.com/Plusa195/reserfast_demo.git
   cd reserfast_demo
   ```

2. **🐍 Crear entorno virtual**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```e/Python-3.13-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1.3-purple.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**ReserFast** es un sistema completo de gestión de restaurantes desarrollado en Django que permite administrar menús, reservas, personal y clientes de manera eficiente y moderna. Diseñado como proyecto de portafolio para demostrar habilidades en desarrollo web full-stack.

## 🚀 Características Principales

### 👥 Gestión Multi-Usuario
- **🔑 Administradores**: Control total del sistema con dashboard avanzado
- **�‍🍳 Cocineros**: Gestión de menús, activación/desactivación de platos
- **🤵 Garzones**: Gestión de mesas, atención de clientes
- **👤 Clientes**: Sistema de reservas, consulta de menús, gestión de perfil

### 🍽️ Gestión Inteligente de Menús
- ✅ **CRUD completo** con interfaz moderna
- 📸 **Subida y edición de imágenes** con preview en tiempo real
- 🏷️ **Categorización avanzada** por tipos de plato
- ⏱️ **Gestión de tiempos** de preparación
- 💰 **Control de precios** dinámico
- 🔄 **Estados activo/inactivo** para disponibilidad

### 📅 Sistema de Reservas Avanzado
- 📋 **Reservas en línea** para clientes registrados
- 🏪 **Gestión de mesas** con ubicaciones personalizables
- ⏰ **Control de horarios** y disponibilidad
- 📊 **Panel de seguimiento** en tiempo real
- ✅ **Validación de disponibilidad** automática

### 🎨 Interfaz Moderna y Responsive
- � **Diseño 100% responsive** (Bootstrap 5)
- 🎭 **Animaciones suaves** con AOS library
- �️ **Dashboard administrativo** con métricas en vivo
- 🌟 **UX/UI optimizada** para todos los dispositivos
- 🎯 **Event delegation** para mejor rendimiento

## �️ Stack Tecnológico

### Backend
- **🐍 Django 5.2.6** - Framework web principal con últimas características
- **🗄️ SQLite/MySQL** - Base de datos (SQLite para desarrollo, MySQL para producción)
- **🔌 Django REST Framework** - APIs RESTful
- **🐍 Python 3.13** - Lenguaje de programación
- **🔐 bcrypt** - Hash seguro de contraseñas

### Frontend
- **🎨 Bootstrap 5.1.3** - Framework CSS responsive
- **⚡ Font Awesome 6.0** - Biblioteca de iconos
- **🎬 AOS (Animate On Scroll)** - Animaciones suaves
- **📱 JavaScript ES6+** - Interactividad moderna
- **🔄 AJAX** - Operaciones asíncronas

### Características Técnicas Avanzadas
- 🛡️ **Middleware personalizado** de validación de sesiones
- 🎯 **Event delegation** para mejor rendimiento JavaScript
- 📁 **Gestión avanzada** de archivos multimedia
- 🔒 **Seguridad robusta** con CSRF y XSS protection
- 📊 **Dashboard con métricas** en tiempo real
- 🖼️ **Sistema de subida** de imágenes con preview

## 📦 Instalación Rápida

### Prerrequisitos
```bash
Python 3.11+ 
Git
pip (incluido con Python)
```

### Configuración en 5 pasos

1. **📥 Clonar repositorio**
   ```bash
   git clone https://github.com/tu-usuario/reserfast.git
   cd reserfast
   ```

2. **🐍 Crear entorno virtual**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **📚 Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **🗄️ Configurar base de datos**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Opcional
   ```

5. **🚀 Ejecutar servidor**
   ```bash
   python manage.py runserver
   ```

**¡Listo!** Accede a http://127.0.0.1:8000/

## 🎯 Acceso a la Aplicación

| Rol | URL | Descripción |
|-----|-----|-------------|
| 🏠 **Público** | http://127.0.0.1:8000/ | Página principal y registro |
| 👤 **Cliente** | http://127.0.0.1:8000/reserfast/index_cliente/ | Panel de cliente |
| 👨‍🍳 **Cocina** | http://127.0.0.1:8000/reserfast/gestion_cocina/ | Gestión de menús |
| 🤵 **Garzón** | http://127.0.0.1:8000/reserfast/panel_garzon/ | Panel de garzón |
| 🔧 **Admin** | http://127.0.0.1:8000/reserfast/index_admin/ | Dashboard administrativo |
| ⚙️ **Django Admin** | http://127.0.0.1:8000/admin/ | Panel de administración |

## 🏗️ Arquitectura del Proyecto

```
reserfast/
├── 📁 reserfast/                    # ⚙️ Configuración Django
│   ├── settings.py                 # 🔧 Configuración principal
│   ├── local_settings.py           # 🛠️ Config desarrollo
│   ├── urls.py                     # 🌐 URLs principales
│   └── wsgi.py                     # 🚀 Deploy WSGI
├── 📁 reserfast_app/               # 🎯 Aplicación principal
│   ├── 📄 models.py                # 🗄️ Modelos de datos
│   ├── 📄 views.py                 # 🎭 Vistas principales
│   ├── 📄 admin_views.py           # 👨‍💼 Vistas admin
│   ├── 📄 forms.py                 # 📝 Formularios
│   ├── 📄 decorators.py            # 🔒 Control de acceso
│   ├── 📄 middleware.py            # 🛡️ Middleware custom
│   ├── 📁 templates/               # 🎨 Plantillas HTML
│   │   ├── reserfast/admin/        # 👨‍💼 Templates admin
│   │   ├── reserfast/cocina/       # 👨‍🍳 Templates cocina
│   │   └── reserfast/cliente/      # 👤 Templates cliente
│   ├── 📁 static/                  # 🎨 Archivos estáticos
│   │   ├── css/                    # 🎨 Estilos CSS
│   │   ├── js/                     # ⚡ JavaScript
│   │   └── images/                 # 🖼️ Imágenes
│   ├── 📁 migrations/              # 🔄 Migraciones BD
│   └── 📁 management/commands/     # 🛠️ Comandos custom
├── 📁 media/                       # 📁 Archivos subidos
│   ├── perfil_img/                 # 👤 Fotos de perfil
│   └── menu_img/                   # 🍽️ Imágenes menús
├── 📄 requirements.txt             # 📚 Dependencias
├── 📄 manage.py                    # 🛠️ CLI Django
└── 📄 README.md                    # 📖 Documentación
```

## 🎮 Funcionalidades Destacadas

### 🖼️ Sistema de Gestión de Imágenes
- **📸 Subida con preview** en tiempo real
- **🖼️ Edición de imágenes** existentes
- **📱 Responsive images** para diferentes dispositivos
- **🔄 Lazy loading** para mejor rendimiento

### 🔐 Sistema de Autenticación Multi-Rol
- **🛡️ Middleware personalizado** de validación
- **🔑 Roles diferenciados** con permisos específicos
- **🔒 Sesiones seguras** con bcrypt
- **⏰ Timeout automático** de sesiones

### ⚡ AJAX y JavaScript Moderno
- **🎯 Event delegation** para mejor rendimiento
- **🔄 Operaciones asíncronas** sin recarga de página
- **📊 Updates en tiempo real** del dashboard
- **🎨 Animaciones fluidas** con AOS

## 🎯 Casos de Uso

### 🏪 Para Restaurantes Reales
- ✅ Gestión completa de menú digital
- ✅ Sistema de reservas automatizado  
- ✅ Control de personal por roles
- ✅ Dashboard con métricas importantes

### 👨‍💻 Para Desarrolladores (Portafolio)
- ✅ **Django avanzado** con múltiples apps
- ✅ **Frontend moderno** con Bootstrap 5
- ✅ **JavaScript ES6+** con AJAX
- ✅ **Gestión de archivos** multimedia
- ✅ **Seguridad web** implementada
- ✅ **Responsive design** completo
- ✅ **Clean code** y buenas prácticas

## 🔧 Comandos de Desarrollo

```bash
# 🗄️ Base de datos
python manage.py makemigrations    # Crear migraciones
python manage.py migrate           # Aplicar migraciones
python manage.py dbshell          # Acceso directo a BD

# 👨‍💼 Usuarios y permisos
python manage.py createsuperuser   # Crear admin
python manage.py changepassword    # Cambiar contraseña

# 🧪 Testing y debugging
python manage.py test              # Ejecutar tests
python manage.py shell             # Shell interactivo
python manage.py check             # Verificar proyecto

# 📊 Información del proyecto
python manage.py showmigrations    # Ver migraciones
python manage.py sqlmigrate        # Ver SQL de migración
```

## 🚀 Deploy y Producción

### Variables de Entorno Recomendadas
```env
# 🔑 Seguridad
DJANGO_SECRET_KEY=tu-clave-super-secreta-aqui
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# 🗄️ Base de datos (MySQL ejemplo)
DB_ENGINE=django.db.backends.mysql
DB_NAME=reserfast_prod
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306

# 📧 Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password
```

### Checklist de Producción
- [ ] 🔒 `DEBUG = False` en settings
- [ ] 🌐 Configurar `ALLOWED_HOSTS`
- [ ] 🗄️ Usar base de datos de producción
- [ ] 📁 Configurar servicio de archivos estáticos
- [ ] 🔐 Variables de entorno seguras
- [ ] 📊 Logging configurado
- [ ] 🚀 Servidor web (Nginx + Gunicorn)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres mejorar este proyecto:

1. 🍴 **Fork** el repositorio
2. 🌿 Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. ✅ Commit tus cambios: `git commit -m 'Add: nueva funcionalidad'`
4. 📤 Push a la rama: `git push origin feature/nueva-funcionalidad`
5. 🔄 Abre un **Pull Request**

### 📋 Áreas de Mejora
- [ ] 🧪 Implementar tests unitarios
- [ ] 📱 PWA (Progressive Web App)
- [ ] 🌐 Internacionalización (i18n)
- [ ] 📊 Dashboard con gráficos avanzados
- [ ] 🔔 Sistema de notificaciones
- [ ] 📧 Integración de email marketing

## 🏆 Características Técnicas Destacadas

### 🎯 Arquitectura y Patrones
- **🏗️ MVC Pattern** bien implementado
- **🎭 Template inheritance** con Django
- **🔄 AJAX calls** para UX fluida
- **📱 Mobile-first design** responsive
- **🎨 Component-based CSS** con Bootstrap

### 🔐 Seguridad Implementada
- **🛡️ CSRF Protection** en todos los formularios
- **🔒 XSS Prevention** con escape automático
- **🔑 Password hashing** con bcrypt
- **⏰ Session management** seguro
- **🚫 SQL Injection** prevención automática

### ⚡ Optimización y Rendimiento
- **🎯 Event delegation** en JavaScript
- **📁 Static files** optimizados
- **🖼️ Image optimization** automática
- **⚡ Lazy loading** para contenido
- **📊 Database queries** optimizadas

## 📊 Métricas del Proyecto

- **📝 Líneas de código**: ~3000+ líneas
- **📄 Templates**: 15+ plantillas HTML
- **🗄️ Modelos**: 8 modelos principales
- **🎭 Vistas**: 25+ vistas funcionales
- **🎨 Páginas**: 12+ páginas principales
- **🔧 Funcionalidades**: 20+ características

## 📄 Licencia

```
MIT License

Copyright (c) 2025 ReserFast Demo Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👨‍💻 Autor

**ReserFast Demo Project**

- 🐙 **GitHub**: [@Plusa195](https://github.com/Plusa195)
- 📧 **Repositorio**: [reserfast_demo](https://github.com/Plusa195/reserfast_demo)

### 💪 Habilidades Demostradas
- 🐍 **Python & Django** - Framework web avanzado
- 🎨 **Frontend Development** - HTML5, CSS3, JavaScript ES6+
- 🗄️ **Database Design** - Modelado y optimización
- 🔐 **Web Security** - Implementación de mejores prácticas
- 📱 **Responsive Design** - Mobile-first approach
- ⚡ **Performance Optimization** - UX/UI optimizada

## 🙏 Agradecimientos

- 🐍 **Django Team** - Por el increíble framework
- 🎨 **Bootstrap Team** - Por el framework CSS
- ⚡ **Font Awesome** - Por los iconos profesionales
- 🎬 **AOS Library** - Por las animaciones suaves
- 🌍 **Open Source Community** - Por todo el conocimiento compartido

---

<div align="center">

### ⭐ Si este proyecto te resultó útil, ¡considera darle una estrella! ⭐

**Desarrollado con ❤️ como proyecto de portafolio**

[⬆️ Volver arriba](#-reserfast---sistema-de-gestión-de-restaurantes)

</div>
