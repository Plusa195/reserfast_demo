# 🤝 Contribuyendo a ReserFast

¡Gracias por tu interés en contribuir a ReserFast! Este documento te guiará sobre cómo puedes ayudar a mejorar este proyecto.

## 🚀 Formas de Contribuir

### 🐛 Reportar Bugs
- Busca primero en los [issues existentes](../../issues)
- Usa la plantilla de bug report
- Incluye información detallada sobre el problema
- Agrega capturas de pantalla si es relevante

### ✨ Sugerir Funcionalidades
- Revisa los [issues de funcionalidades](../../issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
- Usa la plantilla de feature request
- Explica claramente el caso de uso

### 💻 Contribuir Código
- Fork el repositorio
- Crea una rama descriptiva
- Sigue las convenciones de código
- Incluye tests si es aplicable
- Actualiza la documentación

## 🛠️ Configuración de Desarrollo

### Requisitos Previos
```bash
Python 3.11+
Git
VSCode (recomendado)
```

### Configuración Local
```bash
# 1. Fork y clonar
git clone https://github.com/tu-usuario/reserfast.git
cd reserfast

# 2. Entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Dependencias
pip install -r requirements.txt

# 4. Base de datos
python manage.py migrate

# 5. Servidor de desarrollo
python manage.py runserver
```

## 📝 Convenciones de Código

### Python/Django
- Sigue [PEP 8](https://pep8.org/)
- Usa nombres descriptivos para variables y funciones
- Documenta funciones complejas
- Máximo 79 caracteres por línea

### HTML/CSS
- Indentación de 4 espacios
- Nombres de clases en kebab-case
- Usa Bootstrap classes cuando sea posible

### JavaScript
- Usa ES6+ features
- CamelCase para variables y funciones
- Documenta funciones complejas
- Event delegation cuando sea apropiado

## 🔧 Standards de Commit

### Formato de Commit
```
<tipo>(<scope>): <descripción>

<cuerpo opcional>

<footer opcional>
```

### Tipos de Commit
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato, missing semi colons, etc
- `refactor`: Refactoring de código
- `test`: Agregando tests
- `chore`: Mantenimiento

### Ejemplos
```bash
feat(auth): add password reset functionality
fix(menu): resolve image upload validation
docs(readme): update installation instructions
style(dashboard): improve button spacing
```

## 🧪 Testing

### Ejecutar Tests
```bash
python manage.py test
```

### Escribir Tests
- Tests en `tests.py` de cada app
- Usa Django TestCase
- Nombres descriptivos para test methods
- Test tanto casos exitosos como de error

## 📋 Pull Request Process

### Antes de Crear el PR
- [ ] El código pasa todos los tests
- [ ] Se siguieron las convenciones de código
- [ ] Se actualizó la documentación si es necesario
- [ ] Se probó manualmente la funcionalidad

### Crear el Pull Request
1. Crea una descripción clara del cambio
2. Referencia issues relacionados
3. Incluye capturas si hay cambios visuales
4. Solicita review de mantenedores

### Plantilla de PR
```markdown
## 📝 Descripción
Breve descripción de los cambios realizados.

## 🔗 Issues Relacionados
Fixes #123

## 🧪 Cómo Probar
1. Paso uno
2. Paso dos
3. Resultado esperado

## 📸 Capturas (si aplica)
![Screenshot](url-to-image)

## ✅ Checklist
- [ ] Tests pasando
- [ ] Documentación actualizada
- [ ] Convenciones de código seguidas
```

## 🏷️ Labels y Issues

### Labels para Issues
- `bug` - Algo no funciona
- `enhancement` - Nueva funcionalidad
- `documentation` - Mejoras a documentación
- `help wanted` - Ayuda necesaria
- `good first issue` - Bueno para principiantes

### Prioridades
- `priority: high` - Crítico
- `priority: medium` - Importante
- `priority: low` - Puede esperar

## 🎯 Áreas de Contribución

### 🆕 Para Principiantes
- Mejorar documentación
- Corregir typos
- Agregar tests simples
- Mejorar mensajes de error

### 🔥 Funcionalidades Deseadas
- [ ] Sistema de notificaciones
- [ ] Dashboard con gráficos
- [ ] PWA capabilities
- [ ] Internacionalización (i18n)
- [ ] API REST completa
- [ ] Sistema de reviews

### 🧪 Testing
- [ ] Tests unitarios completos
- [ ] Tests de integración
- [ ] Tests de UI/E2E
- [ ] Performance testing

## 📞 Contacto

Si tienes preguntas sobre cómo contribuir:

- 💬 Abre una [discusión](../../discussions)
- 📧 Envía un email a: contribuciones@reserfast.com
- 🐦 Twitter: [@reserfast_dev](https://twitter.com/reserfast_dev)

## 🙏 Reconocimientos

Todos los contribuyentes serán reconocidos en:
- README.md principal
- Sección de contribuyentes
- Release notes

¡Gracias por hacer ReserFast mejor! 🎉
