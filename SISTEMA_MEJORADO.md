# Sistema de Gestión de Quejas y Reclamos - Versión Mejorada

## Descripción

Sistema web desarrollado en Django para la gestión integral de quejas, reclamos y garantías de clientes. Permite a los usuarios registrar tickets asociados a números de factura y serie, adjuntar evidencias multimedia, y realizar seguimiento completo del estado de sus reclamaciones con validación automática de garantías.

## Nuevas Características Implementadas

### Roles de Usuario Mejorados

#### **Cliente**
- Puede crear una nueva solicitud de reclamo/garantía (ticket) indicando:
  - Número de serie del producto
  - Número de factura
  - Fecha de compra
  - Descripción detallada del problema
  - Tipo de reclamo (garantía, reclamo, consulta, devolución)
- Puede añadir múltiples archivos en cada solicitud (imágenes, videos, documentos, facturas, etc.)
- Puede consultar el estado de sus reclamos en tiempo real
- Puede comentar dentro de su propia queja/ticket para dar seguimiento
- En los comentarios también puede añadir múltiples archivos
- Recibe notificaciones automáticas por email en cada actualización
- Dashboard personalizado con estadísticas de sus tickets

#### **Soporte (Agente de Atención)**
- Recibe solicitudes asignadas automáticamente (sistema balancea la carga entre agentes)
- Valida información inicial (documentos, facturas, vigencia de garantía)
- Se comunica con el cliente mediante comentarios dentro del ticket
- Puede derivar la solicitud a un Técnico si requiere reparación
- Cambia estados del reclamo: Abierto → En Revisión → Aceptado/Rechazado → En Reparación → Resuelto → Cerrado
- Puede subir archivos en comentarios internos y públicos
- Dashboard con métricas de carga de trabajo y tickets asignados
- Sistema de balanceo automático de carga

#### **Soporte Técnico**
- Recibe casos cuando un Agente de Atención los deriva
- Puede comentar y subir archivos (ej. fotos de reparación, reportes técnicos)
- Actualiza estado de la solicitud entre "En Reparación" y "Resuelto"
- Dashboard especializado para técnicos
- Sistema de asignación automática con balanceo de carga

#### **Administrador**
- Gestiona usuarios y roles
- Supervisa métricas y reportes completos
- Define reglas de validación (vigencia, políticas de garantía)
- Acceso completo al sistema de auditoría
- Dashboard con estadísticas generales del sistema

### Servicios Implementados

#### **Servicio de Autenticación y Roles**
- Maneja login y control de permisos granular
- Roles: Cliente, Soporte, Soporte Técnico, Administrador
- Sistema de permisos basado en roles
- Dashboards específicos por rol

#### **Servicio de Gestión de Tickets/Reclamos Mejorado**
- Creación y almacenamiento de solicitudes con múltiples archivos adjuntos
- Cada reclamo tiene historial completo de cambios de estado
- Validación automática de garantías basada en fecha de compra
- Campos adicionales: número de serie, fecha de compra, tipo de reclamo
- Sistema de prioridades automáticas

#### **Servicio de Balanceo Automático**
- Los reclamos se reparten automáticamente al agente menos cargado
- Técnicos también reciben asignaciones con balanceo de carga
- Límites configurables de tickets por agente
- Redistribución automática de tickets sin asignar

#### **Servicio de Archivos Mejorado**
- Permite subir múltiples archivos a la vez (en ticket inicial y en comentarios)
- Soporta distintos formatos: imágenes, videos, PDF, documentos, archivos comprimidos
- Cada archivo queda asociado al ticket o al comentario correspondiente
- Sistema de permisos para archivos públicos/privados
- Validación automática de tipos y tamaños de archivo

#### **Servicio de Comentarios Colaborativos**
- Espacio de comentarios tipo chat dentro de cada ticket
- Participación de clientes, soporte y técnicos
- Múltiples archivos adjuntos por comentario
- Comentarios públicos y privados
- Historial completo visible según permisos

#### **Servicio de Estados y Flujo Mejorado**
- Control de transición de estados con validaciones
- Estados: Abierto → En Revisión → Aceptado/Rechazado → En Reparación → En Espera Cliente → Resuelto → Cerrado
- Permisos específicos por rol para cambios de estado
- Motivos de rechazo obligatorios

#### **Servicio de Notificaciones Automáticas**
- Envío de emails automáticos en cada actualización de estado
- Notificaciones por nuevos comentarios
- Templates HTML y texto plano
- Configuración por usuario para recibir notificaciones

#### **Servicio de Reportes y Métricas Avanzado**
- Reportes por fecha, estado, cliente, agente
- Estadísticas de tiempos de resolución
- Métricas de carga de trabajo por agente
- Tickets vencidos y alertas de tiempo
- Dashboard con gráficos y estadísticas

#### **Servicio de Validaciones de Garantía**
- Revisa fechas de compra y políticas de garantía automáticamente
- Configuración de días de garantía por categoría
- Validación de documentos requeridos
- Alertas de garantías próximas a vencer

### Flujo de Trabajo Mejorado

1. **Cliente crea ticket** con información completa y adjunta archivos
2. **Sistema valida garantía** automáticamente basado en fecha de compra
3. **Asignación automática** a Agente de Atención con menos carga
4. **Agente revisa, valida y comunica** con el cliente
5. **Derivación a Técnico** si requiere reparación (automática con balanceo)
6. **Técnico atiende y documenta** el proceso de reparación
7. **Cliente participa** en comentarios y agrega información adicional
8. **Notificaciones automáticas** en cada cambio de estado
9. **Cierre del ticket** → pasa a histórico para reportes y métricas

### Nuevos Campos en Modelos

#### **Usuario**
- `especialidad`: Para técnicos
- `max_tickets_simultaneos`: Límite de tickets activos
- `recibir_notificaciones`: Configuración de emails
- Nuevos roles: `soporte`, `soporte_tecnico`

#### **Ticket**
- `numero_serie`: Número de serie del producto
- `fecha_compra`: Fecha de compra para validar garantía
- `tipo_reclamo`: Garantía, reclamo, consulta, devolución
- `tecnico`: Técnico asignado
- `garantia_vigente`: Validación automática
- `fecha_vencimiento_garantia`: Calculada automáticamente
- `motivo_rechazo`: Requerido al rechazar
- Campos de métricas: tiempos de respuesta y resolución

#### **Comentario**
- `es_respuesta_inicial`: Marca la primera respuesta del agente
- `resuelve_ticket`: Indica si el comentario resuelve el ticket

#### **Adjunto**
- `subido_por`: Usuario que subió el archivo
- `es_publico`: Visibilidad del archivo
- `descripcion`: Descripción opcional
- `etiquetas`: Para organización
- Soporte para múltiples archivos por comentario

### Configuraciones Nuevas

```python
TICKET_SETTINGS = {
    'AUTO_ASSIGN_TICKETS': True,
    'MAX_TICKETS_PER_AGENT': 10,
    'NOTIFICATION_ENABLED': True,
    'GUARANTEE_VALIDATION': True,
    'ALLOWED_FILE_EXTENSIONS': [...],
    'MAX_FILE_SIZE_MB': 25,
    'MAX_FILES_PER_UPLOAD': 10,
    'TICKET_RESPONSE_TIME_HOURS': {...},
    'DEFAULT_GUARANTEE_DAYS': 365,
}
```

### URLs Nuevas

#### Accounts
- `/accounts/dashboard/soporte/` - Dashboard para agentes
- `/accounts/dashboard/tecnico/` - Dashboard para técnicos
- `/accounts/usuarios/estadisticas/` - Estadísticas de usuarios

#### Tickets
- Todas las URLs existentes mantienen compatibilidad
- Nuevas funcionalidades integradas en URLs existentes

### Templates de Email

- `templates/emails/ticket_creado.html` - Notificación de ticket creado
- `templates/emails/ticket_asignado.html` - Notificación de asignación
- `templates/emails/cambio_estado.html` - Notificación de cambio de estado
- `templates/emails/nuevo_comentario.html` - Notificación de comentario
- Versiones en texto plano (.txt) para cada template

### Servicios Principales

#### `tickets/services.py`
- `BalanceadorCarga`: Asignación automática y balanceo
- `NotificacionService`: Envío de emails automáticos
- `ValidadorGarantia`: Validación automática de garantías
- `MetricasService`: Generación de reportes y métricas

### Comandos de Gestión

Los comandos existentes se mantienen y se pueden extender para los nuevos roles:

```bash
python manage.py crear_datos_ejemplo --usuarios 50 --tickets 200
```

### Instalación y Migración

1. **Aplicar migraciones**:
```bash
python manage.py makemigrations
python manage.py migrate
```

2. **Crear superusuario**:
```bash
python manage.py createsuperuser
```

3. **Configurar email** (opcional para desarrollo):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

4. **Configurar archivos estáticos**:
```bash
python manage.py collectstatic
```

### Compatibilidad

- **Backward Compatible**: Todos los roles y funcionalidades existentes se mantienen
- **Migración Gradual**: Los usuarios con rol 'empleado' pueden migrar a 'soporte'
- **Datos Existentes**: Se preservan todos los tickets y usuarios existentes

### Seguridad

- Validación de permisos por rol en cada vista
- Archivos adjuntos con validación de tipo y tamaño
- Comentarios privados solo visibles para personal autorizado
- Auditoría completa de todas las acciones

### Performance

- Índices optimizados en campos de búsqueda frecuente
- Paginación en todas las listas
- Cache configurado para consultas frecuentes
- Balanceo de carga para distribución eficiente

### Monitoreo

- Logging configurado para servicios críticos
- Métricas de tiempo de respuesta y resolución
- Alertas para tickets vencidos
- Dashboard con estadísticas en tiempo real

Este sistema mejorado proporciona una solución completa y escalable para la gestión de quejas, reclamos y garantías, con automatización inteligente y una experiencia de usuario optimizada para todos los roles involucrados.