# Sistema de Gestión de Quejas y Reclamos

## Descripción

Sistema web desarrollado en Django para la gestión de quejas y reclamos de clientes. Permite a los usuarios registrar tickets asociados a números de factura, adjuntar evidencias multimedia, y realizar seguimiento del estado de sus reclamaciones.

## Características Principales

### Roles de Usuario
- **Cliente**: Puede crear tickets, adjuntar evidencias, comentar en sus tickets y consultar el estado
- **Empleado**: Puede gestionar tickets asignados, cambiar estados, comentar y solicitar información adicional
- **Superadministrador**: Acceso completo al sistema, gestión de usuarios y configuración

### Funcionalidades Implementadas
- Sistema de autenticación con roles específicos
- Creación de tickets con número de factura obligatorio
- Sistema de comentarios con visibilidad pública/privada
- Adjuntos multimedia (imágenes, videos, documentos PDF)
- Estados de ticket: Abierto → En revisión → En espera de cliente → Resuelto → Cerrado
- Sistema de auditoría y bitácora completa
- Categorización y priorización de tickets
- Panel de administración completo
- Dashboards específicos por rol
- Sistema de filtros y búsqueda
- Paginación de resultados

## Estructura del Proyecto

```
core/
├── accounts/          # Gestión de usuarios extendidos
│   ├── models.py      # Usuario con roles
│   ├── views.py       # Vistas de autenticación y dashboards
│   ├── forms.py       # Formularios de registro y perfil
│   └── urls.py        # URLs de la aplicación
├── tickets/           # Modelos principales de tickets
│   ├── models.py      # Ticket, Categoria, Comentario
│   ├── views.py       # Gestión completa de tickets
│   ├── forms.py       # Formularios de tickets y comentarios
│   └── management/    # Comandos personalizados
├── attachments/       # Gestión de archivos adjuntos
│   ├── models.py      # Adjunto con validaciones
│   ├── views.py       # Subida y descarga de archivos
│   └── forms.py       # Formulario de adjuntos
│   ├── models.py      # Evento de auditoría
│   ├── views.py       # Consulta de eventos
│   └── signals.py     # Captura automática de eventos
├── User/              # Aplicación de usuarios (existente)
├── Home/              # Aplicación principal (existente)
├── core/              # Configuración del proyecto
│   ├── settings.py    # Configuración principal
│   ├── urls.py        # URLs principales
│   └── utils.py       # Utilidades generales
├── templates/         # Plantillas HTML
│   ├── base.html      # Template base con navegación
│   ├── accounts/      # Templates de usuarios
│   ├── tickets/       # Templates de tickets
│   ├── attachments/   # Templates de adjuntos
└── media/             # Archivos subidos por usuarios
```

## Modelos de Datos

### Usuario (accounts.Usuario)
- Extiende AbstractUser de Django
- Campos adicionales: teléfono, fecha_nacimiento, dirección, rol, estado
- Roles: cliente, empleado, superadmin
- Managers personalizados para consultas específicas

### Ticket (tickets.Ticket)
- ID único UUID
- Número de factura (obligatorio)
- Asunto y descripción
- Categoría y prioridad
- Estados del ciclo de vida
- Relaciones con cliente y agente
- Timestamps y auditoría

### Comentario (tickets.Comentario)
- Comentarios en tickets
- Autor 
- Relación con ticket

### Adjunto (attachments.Adjunto)
- Archivos multimedia
- Relación genérica con tickets/comentarios
- Organización por carpetas



## Instalación y Configuración

### Requisitos
- Python 3.11+
- Django 5.2.5
- SQLite 

### Instalación Rápida
1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instalar dependencias básicas:
   ```bash
   pip install django django-crispy-forms crispy-bootstrap5
   ```
4. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
5. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```
6. Actualizar rol del superusuario:
   ```bash
   python manage.py shell
   >>> from accounts.models import Usuario
   >>> user = Usuario.objects.get(username='tu_usuario')
   >>> user.rol = 'superadmin'
   >>> user.save()
   >>> exit()
   ```
7. Crear datos de ejemplo:
   ```bash
   python manage.py crear_datos_ejemplo
   ```
8. Ejecutar servidor:
   ```bash
   python manage.py runserver
   ```

### Configuración para Producción (MariaDB)
1. Instalar mysqlclient:
   ```bash
   pip install mysqlclient
   ```
2. Crear base de datos en MariaDB:
   ```sql
   CREATE DATABASE sistema_quejas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Descomentar configuración de MariaDB en `settings.py`
4. Configurar credenciales de base de datos
5. Ejecutar migraciones

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

### Roles y Permisos
- **Cliente**: Crear tickets, comentar, ver sus propios tickets
- **Empleado**: Gestionar tickets asignados, cambiar estados, comentarios privados
- **Superadmin**: Acceso completo, gestión de usuarios, eliminación de archivos

## Comandos de Gestión

### Crear Datos de Ejemplo
```bash
python manage.py crear_datos_ejemplo --usuarios 5 --tickets 10
```

### Acceso al Sistema
- **URL**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Registro**: http://127.0.0.1:8000/accounts/registro/

### Usuarios de Ejemplo
Después de ejecutar `crear_datos_ejemplo`:
- **Clientes**: cliente1, cliente2 (password: password123)
- **Empleados**: empleado1, empleado2 (password: password123)
- **Superadmin**: superadmin (password: admin123456)



## Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **Base de Datos**: SQLite (desarrollo) / MariaDB (producción)
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Formularios**: Django Crispy Forms
- **Archivos**: Sistema de archivos local
- **Auditoría**: Django Signals

