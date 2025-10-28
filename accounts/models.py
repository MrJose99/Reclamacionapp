import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')

        # Establecer valores por defecto para usuarios regulares
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('estado', 'activo')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'superadmin')
        extra_fields.setdefault('estado', 'activo')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def clientes(self):
        """Retorna solo los usuarios con rol de cliente"""
        return self.filter(rol='cliente', estado='activo')

    def empleados(self):
        """Retorna solo los usuarios con rol de empleado (legacy)"""
        return self.filter(rol='empleado', estado='activo')

    def soporte(self):
        """Retorna solo los usuarios con rol de soporte (agentes de atención)"""
        return self.filter(rol='soporte', estado='activo')

    def soporte_tecnico(self):
        """Retorna solo los usuarios con rol de soporte técnico"""
        return self.filter(rol='soporte_tecnico', estado='activo')

    def superadministradores(self):
        """Retorna solo los usuarios con rol de superadmin"""
        return self.filter(rol='superadmin', estado='activo')

    def activos(self):
        """Retorna solo los usuarios activos"""
        return self.filter(estado='activo')

    def agentes_disponibles(self):
        """Retorna agentes de soporte ordenados por carga de trabajo (menos tickets activos primero)"""
        from django.db.models import Count
        return self.filter(
            rol='soporte',
            estado='activo'
        ).annotate(
            tickets_activos=Count('tickets_asignados', filter=models.Q(tickets_asignados__estado__in=['abierto', 'en_revision', 'en_espera_cliente']))
        ).order_by('tickets_activos')

    def tecnicos_disponibles(self):
        """Retorna técnicos ordenados por carga de trabajo"""
        from django.db.models import Count
        return self.filter(
            rol='soporte_tecnico',
            estado='activo'
        ).annotate(
            tickets_activos=Count('tickets_asignados', filter=models.Q(tickets_asignados__estado='en_reparacion'))
        ).order_by('tickets_activos')


class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""

    ROLES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),  # Mantenido por compatibilidad
        ('soporte', 'Soporte (Agente de Atención)'),
        ('soporte_tecnico', 'Soporte Técnico'),
        ('superadmin', 'Superadministrador'),
    ]

    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente', verbose_name='Rol')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo', verbose_name='Estado')

    # Campos adicionales para el sistema mejorado
    especialidad = models.CharField(max_length=100, blank=True, null=True, verbose_name='Especialidad',
                                  help_text='Para técnicos: área de especialización')
    max_tickets_simultaneos = models.PositiveIntegerField(default=10, verbose_name='Máximo tickets simultáneos',
                                                        help_text='Límite de tickets activos que puede manejar')
    recibir_notificaciones = models.BooleanField(default=True, verbose_name='Recibir notificaciones por email')

    # Campos adicionales para gestión de clientes (Administrador)
    es_vip = models.BooleanField(default=False, verbose_name='Cliente VIP',
                                 help_text='Marca al cliente como VIP para atención prioritaria')
    tiene_restricciones = models.BooleanField(default=False, verbose_name='Tiene restricciones',
                                              help_text='Marca al cliente con restricciones por fraude o abuso')
    notas_internas = models.TextField(blank=True, null=True, verbose_name='Notas internas',
                                      help_text='Notas visibles solo para empleados y administradores')
    motivo_restriccion = models.TextField(blank=True, null=True, verbose_name='Motivo de restricción',
                                           help_text='Razón por la cual el cliente tiene restricciones')
    fecha_restriccion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de restricción')

    # Campos de auditoría adicionales
    ultima_actividad = models.DateTimeField(blank=True, null=True, verbose_name='Última actividad')
    motivo_desactivacion = models.TextField(blank=True, null=True, verbose_name='Motivo de desactivación')
    fecha_desactivacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de desactivación')
    desactivado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='usuarios_desactivados', verbose_name='Desactivado por')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    objects = UsuarioManager()

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def es_cliente(self):
        """Verifica si el usuario es cliente"""
        return self.rol == 'cliente'

    def es_empleado(self):
        """Verifica si el usuario es empleado (legacy)"""
        return self.rol == 'empleado'

    def es_soporte(self):
        """Verifica si el usuario es agente de soporte"""
        return self.rol == 'soporte'

    def es_soporte_tecnico(self):
        """Verifica si el usuario es soporte técnico"""
        return self.rol == 'soporte_tecnico'

    def es_superadmin(self):
        """Verifica si el usuario es superadministrador"""
        return self.rol == 'superadmin'

    def puede_gestionar_tickets(self):
        """Verifica si el usuario puede gestionar tickets"""
        return self.rol in ['empleado', 'soporte', 'soporte_tecnico', 'superadmin']

    def puede_eliminar(self):
        """Verifica si el usuario puede eliminar elementos"""
        return self.rol == 'superadmin'

    def puede_asignar_tickets(self):
        """Verifica si el usuario puede asignar tickets"""
        return self.rol in ['soporte', 'superadmin']

    def puede_derivar_a_tecnico(self):
        """Verifica si el usuario puede derivar tickets a técnicos"""
        return self.rol in ['soporte', 'superadmin']

    def puede_reasignar_libremente(self):
        """Verifica si el usuario puede reasignar tickets sin restricciones (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_acceder_todos_tickets(self):
        """Verifica si el usuario tiene acceso a todos los tickets del sistema (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_gestionar_usuarios(self):
        """Verifica si el usuario puede crear, editar y desactivar usuarios (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_crear_empleados(self):
        """Verifica si el usuario puede crear usuarios tipo Empleado y Administrador (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_editar_cualquier_usuario(self):
        """Verifica si el usuario puede editar cualquier usuario del sistema (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_desactivar_usuarios(self):
        """Verifica si el usuario puede desactivar/activar usuarios (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_eliminar_usuarios(self):
        """Verifica si el usuario puede eliminar usuarios (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_ver_auditoria_completa(self):
        """Verifica si el usuario puede ver la auditoría completa del sistema (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_configurar_sistema(self):
        """Verifica si el usuario puede modificar configuraciones del sistema (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_generar_reportes(self):
        """Verifica si el usuario puede generar reportes y analítica (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_ver_metricas_globales(self):
        """Verifica si el usuario puede ver métricas globales del sistema (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_forzar_cambios_estado(self):
        """Verifica si el usuario puede forzar cambios de estado sin validaciones (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_editar_datos_ticket(self):
        """Verifica si el usuario puede editar datos del ticket, producto o cliente (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_gestionar_clientes(self):
        """Verifica si el usuario puede gestionar clientes (marcar VIP, restricciones, etc.)"""
        return self.rol == 'superadmin'

    def puede_marcar_cliente_vip(self):
        """Verifica si el usuario puede marcar clientes como VIP (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_aplicar_restricciones_cliente(self):
        """Verifica si el usuario puede aplicar restricciones a clientes (exclusivo Administrador)"""
        return self.rol == 'superadmin'

    def puede_ver_notas_internas(self):
        """Verifica si el usuario puede ver notas internas de clientes"""
        return self.rol in ['soporte', 'soporte_tecnico', 'superadmin']

    def puede_editar_notas_internas(self):
        """Verifica si el usuario puede editar notas internas de clientes"""
        return self.rol in ['soporte', 'superadmin']

    def puede_cambiar_estado_ticket(self, estado_actual, nuevo_estado):
        """Verifica si el usuario puede cambiar el estado de un ticket"""
        if self.es_superadmin():
            return True

        # Reglas específicas por rol
        if self.es_soporte():
            # Agentes pueden cambiar la mayoría de estados
            transiciones_permitidas = {
                'abierto': ['en_revision', 'rechazado'],
                'en_revision': ['aceptado', 'rechazado', 'en_espera_cliente'],
                'aceptado': ['en_reparacion', 'resuelto', 'en_espera_cliente'],
                'en_espera_cliente': ['en_revision', 'aceptado'],
                'resuelto': ['cerrado'],
            }
            return nuevo_estado in transiciones_permitidas.get(estado_actual, [])

        elif self.es_soporte_tecnico():
            # Técnicos pueden trabajar con tickets en reparación
            transiciones_permitidas = {
                'en_reparacion': ['resuelto', 'en_espera_cliente'],
                'en_espera_cliente': ['en_reparacion'],
            }
            return nuevo_estado in transiciones_permitidas.get(estado_actual, [])

        return False

    def get_tickets_activos_count(self):
        """Retorna el número de tickets activos asignados al usuario"""
        if hasattr(self, 'tickets_asignados'):
            return self.tickets_asignados.filter(
                estado__in=['abierto', 'en_revision', 'aceptado', 'en_reparacion', 'en_espera_cliente']
            ).count()
        return 0

    def puede_recibir_mas_tickets(self):
        """Verifica si el usuario puede recibir más tickets"""
        # Superadmin puede recibir tickets sin límite
        if self.es_superadmin():
            return True
        return self.get_tickets_activos_count() < self.max_tickets_simultaneos

    def get_porcentaje_carga_trabajo(self):
        """Retorna el porcentaje de carga de trabajo actual"""
        if self.max_tickets_simultaneos == 0:
            return 0
        return (self.get_tickets_activos_count() / self.max_tickets_simultaneos) * 100

    def esta_sobrecargado(self):
        """Verifica si el usuario está sobrecargado (más tickets que el límite)"""
        return self.get_tickets_activos_count() > self.max_tickets_simultaneos

    # ========== MÉTODOS DE MÉTRICAS Y DESEMPEÑO (para Administrador) ==========

    def get_tickets_resueltos_count(self):
        """Retorna el número total de tickets resueltos por el usuario"""
        if hasattr(self, 'tickets_asignados'):
            return self.tickets_asignados.filter(estado__in=['resuelto', 'cerrado']).count()
        return 0

    def get_tickets_totales_count(self):
        """Retorna el número total de tickets asignados al usuario"""
        if hasattr(self, 'tickets_asignados'):
            return self.tickets_asignados.count()
        return 0

    def get_tasa_resolucion(self):
        """Retorna la tasa de resolución del usuario (tickets resueltos / tickets totales)"""
        totales = self.get_tickets_totales_count()
        if totales == 0:
            return 0
        return (self.get_tickets_resueltos_count() / totales) * 100

    def get_tiempo_promedio_resolucion(self):
        """Retorna el tiempo promedio de resolución en días"""
        if not hasattr(self, 'tickets_asignados'):
            return 0

        from django.db.models import Avg, F, ExpressionWrapper, fields

        tickets_resueltos = self.tickets_asignados.filter(
            estado__in=['resuelto', 'cerrado'],
            fecha_resolucion__isnull=False
        )

        if not tickets_resueltos.exists():
            return 0

        resultado = tickets_resueltos.aggregate(
            promedio=Avg(
                ExpressionWrapper(
                    F('fecha_resolucion') - F('created_at'),
                    output_field=fields.DurationField()
                )
            )
        )

        if resultado['promedio']:
            return resultado['promedio'].total_seconds() / 86400  # Convertir a días
        return 0

    def get_tickets_reabiertos_count(self):
        """Retorna el número de tickets reabiertos (que volvieron de resuelto a otro estado)"""
        if not hasattr(self, 'tickets_asignados'):
            return 0

        # Esto requeriría un campo adicional en el modelo Ticket para rastrear reaperturas
        # Por ahora retornamos 0, se implementará cuando se agregue el campo
        return 0

    def get_tickets_escalados_count(self):
        """Retorna el número de tickets escalados a soporte técnico"""
        if not hasattr(self, 'tickets_asignados'):
            return 0

        # Esto requeriría un campo adicional en el modelo Ticket para rastrear escalamientos
        # Por ahora retornamos 0, se implementará cuando se agregue el campo
        return 0

    def get_metricas_desempeno(self):
        """Retorna un diccionario con todas las métricas de desempeño del usuario"""
        return {
            'tickets_activos': self.get_tickets_activos_count(),
            'tickets_resueltos': self.get_tickets_resueltos_count(),
            'tickets_totales': self.get_tickets_totales_count(),
            'tasa_resolucion': self.get_tasa_resolucion(),
            'tiempo_promedio_resolucion': self.get_tiempo_promedio_resolucion(),
            'tickets_reabiertos': self.get_tickets_reabiertos_count(),
            'tickets_escalados': self.get_tickets_escalados_count(),
            'porcentaje_carga': self.get_porcentaje_carga_trabajo(),
            'esta_sobrecargado': self.esta_sobrecargado(),
        }

    # ========== MÉTODOS DE GESTIÓN DE CLIENTES (para Administrador) ==========

    def marcar_como_vip(self, admin_user):
        """Marca al cliente como VIP (solo Administrador)"""
        if not admin_user.puede_marcar_cliente_vip():
            raise PermissionError("Solo los administradores pueden marcar clientes como VIP")

        self.es_vip = True
        self.save(update_fields=['es_vip', 'updated_at'])

    def quitar_marca_vip(self, admin_user):
        """Quita la marca VIP del cliente (solo Administrador)"""
        if not admin_user.puede_marcar_cliente_vip():
            raise PermissionError("Solo los administradores pueden quitar la marca VIP")

        self.es_vip = False
        self.save(update_fields=['es_vip', 'updated_at'])

    def aplicar_restriccion(self, motivo, admin_user):
        """Aplica restricciones al cliente por fraude o abuso (solo Administrador)"""
        if not admin_user.puede_aplicar_restricciones_cliente():
            raise PermissionError("Solo los administradores pueden aplicar restricciones")

        self.tiene_restricciones = True
        self.motivo_restriccion = motivo
        self.fecha_restriccion = timezone.now()
        self.save(update_fields=['tiene_restricciones', 'motivo_restriccion', 'fecha_restriccion', 'updated_at'])

    def quitar_restriccion(self, admin_user):
        """Quita las restricciones del cliente (solo Administrador)"""
        if not admin_user.puede_aplicar_restricciones_cliente():
            raise PermissionError("Solo los administradores pueden quitar restricciones")

        self.tiene_restricciones = False
        self.motivo_restriccion = None
        self.fecha_restriccion = None
        self.save(update_fields=['tiene_restricciones', 'motivo_restriccion', 'fecha_restriccion', 'updated_at'])

    def agregar_nota_interna(self, nota, usuario):
        """Agrega una nota interna al cliente"""
        if not usuario.puede_editar_notas_internas():
            raise PermissionError("No tienes permisos para editar notas internas")

        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        nueva_nota = f"[{timestamp}] {usuario.get_full_name()}: {nota}\n"

        if self.notas_internas:
            self.notas_internas += nueva_nota
        else:
            self.notas_internas = nueva_nota

        self.save(update_fields=['notas_internas', 'updated_at'])

    def get_historial_tickets_cliente(self):
        """Retorna el historial completo de tickets del cliente"""
        if not self.es_cliente():
            return None

        if hasattr(self, 'tickets'):
            return self.tickets.all().order_by('-created_at')
        return None

    def get_estadisticas_cliente(self):
        """Retorna estadísticas del cliente para vista de Administrador"""
        if not self.es_cliente():
            return None

        if not hasattr(self, 'tickets'):
            return {
                'total_tickets': 0,
                'tickets_aprobados': 0,
                'tickets_rechazados': 0,
                'tickets_resueltos': 0,
                'tickets_activos': 0,
                'tiempo_promedio_resolucion': 0,
            }

        from django.db.models import Avg, F, ExpressionWrapper, fields

        tickets = self.tickets.all()
        tickets_resueltos = tickets.filter(estado__in=['resuelto', 'cerrado'], fecha_resolucion__isnull=False)

        tiempo_promedio = 0
        if tickets_resueltos.exists():
            resultado = tickets_resueltos.aggregate(
                promedio=Avg(
                    ExpressionWrapper(
                        F('fecha_resolucion') - F('created_at'),
                        output_field=fields.DurationField()
                    )
                )
            )
            if resultado['promedio']:
                tiempo_promedio = resultado['promedio'].total_seconds() / 86400

        return {
            'total_tickets': tickets.count(),
            'tickets_aprobados': tickets.filter(estado='aceptado').count(),
            'tickets_rechazados': tickets.filter(estado='rechazado').count(),
            'tickets_resueltos': tickets.filter(estado__in=['resuelto', 'cerrado']).count(),
            'tickets_activos': tickets.filter(estado__in=['abierto', 'en_revision', 'aceptado', 'en_reparacion', 'en_espera_cliente']).count(),
            'tiempo_promedio_resolucion': tiempo_promedio,
        }

    # ========== MÉTODOS DE GESTIÓN DE USUARIOS (para Administrador) ==========

    def desactivar_usuario(self, motivo, admin_user):
        """Desactiva el usuario (solo Administrador)"""
        if not admin_user.puede_desactivar_usuarios():
            raise PermissionError("Solo los administradores pueden desactivar usuarios")

        self.estado = 'inactivo'
        self.is_active = False
        self.motivo_desactivacion = motivo
        self.fecha_desactivacion = timezone.now()
        self.desactivado_por = admin_user
        self.save(update_fields=['estado', 'is_active', 'motivo_desactivacion', 'fecha_desactivacion', 'desactivado_por', 'updated_at'])

    def activar_usuario(self, admin_user):
        """Activa el usuario (solo Administrador)"""
        if not admin_user.puede_desactivar_usuarios():
            raise PermissionError("Solo los administradores pueden activar usuarios")

        self.estado = 'activo'
        self.is_active = True
        self.motivo_desactivacion = None
        self.fecha_desactivacion = None
        self.desactivado_por = None
        self.save(update_fields=['estado', 'is_active', 'motivo_desactivacion', 'fecha_desactivacion', 'desactivado_por', 'updated_at'])

    def puede_ser_eliminado(self):
        """Verifica si el usuario puede ser eliminado (no tiene tickets asignados)"""
        if hasattr(self, 'tickets_asignados'):
            return self.tickets_asignados.count() == 0
        return True

    def actualizar_ultima_actividad(self):
        """Actualiza el timestamp de última actividad del usuario"""
        self.ultima_actividad = timezone.now()
        self.save(update_fields=['ultima_actividad'])

    def get_dashboard_url(self):
        """Retorna la URL del dashboard correspondiente según el rol del usuario"""
        from django.urls import reverse

        if self.es_superadmin():
            return reverse('accounts:dashboard_superadmin')
        elif self.es_soporte():
            return reverse('accounts:dashboard_soporte')
        elif self.es_soporte_tecnico():
            return reverse('accounts:dashboard_tecnico')
        elif self.es_cliente():
            return reverse('accounts:dashboard_cliente')
        else:
            # Por defecto, redirigir al dashboard de empleado (legacy)
            return reverse('accounts:dashboard_empleado')