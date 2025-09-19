# Sistema de Gestión de Quejas y Reclamos

## Descripción

Sistema web desarrollado en Django para la gestión de quejas y reclamos de clientes. Permite a los usuarios registrar tickets asociados a números de factura, adjuntar evidencias multimedia, y realizar seguimiento del estado de sus reclamaciones.

## Características Principales

### Roles de Usuario
- **Cliente**: Puede crear tickets, adjuntar evidencias, comentar en sus tickets y consultar el estado
- **Empleado**: Puede gestionar tickets asignados, cambiar estados, comentar y solicitar información adicional
- **Administrador**: Acceso completo al sistema, gestión de usuarios y configuración

### Funcionalidades
- ✅ Registro y autenticación de usuarios
- ✅ Creación de tickets con número de factura obligatorio
- ✅ Sistema de comentarios con visibilidad pública/privada
- ✅ Adjuntos multimedia (imágenes, videos, documentos PDF)
- ✅ Estados de ticket: Abierto → En revisión → En espera de cliente → Resuelto → Cerrado
- ✅ Sistema de auditoría y bitácora completa
- ✅ Categorización y priorización de tickets
- ✅ Panel de administración completo

## Estructura del Proyecto

```
core/
├── accounts/          # Gestión de usuarios extendidos
├── tickets/           # Modelos principales de tickets
├── attachments/       # Gestión de archivos adjuntos
├── audit/             # Sistema de auditoría y bitácora
├── User/              # Aplicación de usuarios (existente)
├── Home/              # Aplicación principal (existente)
├── core/              # Configuración del proyecto
├── templates/         # Plantillas HTML
└── media/             # Archivos subidos por usuarios
```

## Modelos de Datos

### Usuario (accounts.Usuario)
- Extiende AbstractUser de Django
- Campos adicionales: teléfono, fecha_nacimiento, dirección, rol, estado
- Roles: cliente, empleado, admin

### Ticket (tickets.Ticket)
- ID único UUID
- Número de factura (obligatorio)
- Asunto y descripción
- Categoría y prioridad
- Estados del ciclo de vida
- Relaciones con cliente y agente

### Comentario (tickets.Comentario)
- Comentarios en tickets
- Visibilidad pública/privada
- Autor y timestamp

### Adjunto (attachments.Adjunto)
- Archivos multimedia
- Relación genérica con tickets/comentarios
- Validación de tipos y tamaños
- Organización por carpetas

### Evento (audit.Evento)
- Bitácora de auditoría
- Registro de todas las acciones
- Datos JSON adicionales
- Trazabilidad completa

## Instalación y Configuración

### Requisitos
- Python 3.11+
- Django 5.2.5
- SQLite (por defecto)

### Instalación
1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install django crispy-forms crispy-bootstrap5
   ```
3. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
4. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```
5. Crear datos de ejemplo (opcional):
   ```bash
   python manage.py crear_datos_ejemplo
   ```
6. Ejecutar servidor:
   ```bash
   python manage.py runserver
   ```

## Configuración

### Settings Importantes
- `AUTH_USER_MODEL = 'accounts.Usuario'` - Modelo de usuario personalizado
- `MEDIA_URL` y `MEDIA_ROOT` - Configuración para archivos adjuntos
- `FILE_UPLOAD_MAX_MEMORY_SIZE = 25MB` - Límite de tamaño de archivos
- Zona horaria: `America/Guatemala`
- Idioma: Español

### Archivos Adjuntos
- Formatos permitidos: JPG, JPEG, PNG, WEBP, MP4, MOV, PDF
- Tamaño máximo: 25MB por archivo
- Organización: `/media/tickets/{ticket_id}/`
- Nombres únicos con UUID para evitar conflictos

## Flujo de Trabajo

### Ciclo de Vida del Ticket
1. **Abierto** - Cliente crea el ticket
2. **En Revisión** - Empleado toma el ticket
3. **En Espera de Cliente** - Se solicita información adicional
4. **Resuelto** - Se proporciona solución
5. **Cerrado** - Confirmación final
6. **Rechazado** - Ticket no procede (alternativo)

### Proceso de Auditoría
- Todos los eventos se registran automáticamente
- Signals de Django para captura automática
- Datos JSON para información adicional
- Trazabilidad por usuario y timestamp

## Comandos de Gestión

### Crear Datos de Ejemplo
```bash
python manage.py crear_datos_ejemplo --usuarios 5 --tickets 10
```

## Seguridad

- Control de acceso por roles
- Validación de archivos adjuntos
- Límites de tamaño y tipo de archivo
- Checksums para integridad de archivos
- Timestamps en UTC

## API y Extensibilidad

El sistema está preparado para:
- Implementación de API REST
- Notificaciones por email
- Integración con sistemas externos
- Escalabilidad horizontal

## Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **Base de Datos**: SQLite (configurable)
- **Frontend**: Bootstrap 5 + Crispy Forms
- **Archivos**: Sistema de archivos local
- **Auditoría**: Signals de Django

## Contribución

Para contribuir al proyecto:
1. Fork del repositorio
2. Crear rama feature
3. Implementar cambios
4. Ejecutar tests
5. Crear Pull Request

## Licencia

Proyecto desarrollado para sistema de gestión de quejas y reclamos.

---

**Desarrollado con Django 5.2.5 | Python 3.11+**