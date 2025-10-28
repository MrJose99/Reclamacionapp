import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime

User = get_user_model()


class CategoriaManager(models.Manager):
    """Manager personalizado para el modelo Categoria"""

    def activas(self):
        """Retorna solo las categorías activas"""
        return self.filter(activa=True)


class Categoria(models.Model):
    """Modelo para las categorías de tickets"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    # Campos para validación de garantía
    dias_garantia_defecto = models.PositiveIntegerField(default=365, verbose_name='Días de garantía por defecto')
    requiere_factura = models.BooleanField(default=True, verbose_name='Requiere factura')
    requiere_numero_serie = models.BooleanField(default=True, verbose_name='Requiere número de serie')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    objects = CategoriaManager()

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TicketManager(models.Manager):
    """Manager personalizado para el modelo Ticket"""

    def abiertos(self):
        """Retorna tickets abiertos"""
        return self.filter(estado='abierto')

    def en_revision(self):
        """Retorna tickets en revisión"""
        return self.filter(estado='en_revision')

    def aceptados(self):
        """Retorna tickets aceptados"""
        return self.filter(estado='aceptado')

    def en_reparacion(self):
        """Retorna tickets en reparación"""
        return self.filter(estado='en_reparacion')

    def resueltos(self):
        """Retorna tickets resueltos"""
        return self.filter(estado='resuelto')

    def cerrados(self):
        """Retorna tickets cerrados"""
        return self.filter(estado='cerrado')

    def rechazados(self):
        """Retorna tickets rechazados"""
        return self.filter(estado='rechazado')

    def activos(self):
        """Retorna tickets activos (no cerrados ni rechazados)"""
        return self.exclude(estado__in=['cerrado', 'rechazado'])

    def del_cliente(self, cliente):
        """Retorna tickets de un cliente específico"""
        return self.filter(cliente=cliente)

    def asignados_a(self, agente):
        """Retorna tickets asignados a un agente específico"""
        return self.filter(agente=agente)

    def sin_asignar(self):
        """Retorna tickets sin asignar"""
        return self.filter(agente__isnull=True, estado='abierto')

    def por_prioridad(self, prioridad):
        """Retorna tickets por prioridad"""
        return self.filter(prioridad=prioridad)

    def vencidos(self):
        """Retorna tickets que han superado el tiempo esperado de respuesta"""
        from django.utils import timezone
        limite_alta = timezone.now() - timedelta(hours=4)
        limite_media = timezone.now() - timedelta(hours=24)
        limite_baja = timezone.now() - timedelta(hours=72)

        return self.filter(
            models.Q(prioridad='alta', created_at__lt=limite_alta) |
            models.Q(prioridad='media', created_at__lt=limite_media) |
            models.Q(prioridad='baja', created_at__lt=limite_baja)
        ).exclude(estado__in=['cerrado', 'rechazado'])


class Ticket(models.Model):
    """Modelo para los tickets de reclamos/garantías"""

    ESTADOS = [
        ('abierto', 'Abierto'),
        ('en_revision', 'En Revisión'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
        ('en_reparacion', 'En Reparación'),
        ('en_espera_cliente', 'En Espera del Cliente'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]

    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    TIPOS_RECLAMO = [
        ('garantia', 'Garantía'),
        ('reclamo', 'Reclamo'),
        ('consulta', 'Consulta'),
        ('devolucion', 'Devolución'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica del ticket
    numero_factura = models.CharField(max_length=50, verbose_name='Número de Factura')
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Serie')
    fecha_compra = models.DateField(blank=True, null=True, verbose_name='Fecha de Compra')

    asunto = models.CharField(max_length=200, verbose_name='Asunto')
    descripcion = models.TextField(verbose_name='Descripción del Problema')

    # Clasificación
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name='Categoría')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media', verbose_name='Prioridad')
    tipo_reclamo = models.CharField(max_length=20, choices=TIPOS_RECLAMO, default='reclamo', verbose_name='Tipo de Reclamo')

    # Estados y seguimiento
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto', verbose_name='Estado')

    # Usuarios involucrados
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_creados', verbose_name='Cliente')
    agente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='tickets_asignados', verbose_name='Agente Asignado',
                              limit_choices_to={'rol__in': ['soporte', 'empleado']})
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='tickets_tecnicos', verbose_name='Técnico Asignado',
                               limit_choices_to={'rol': 'soporte_tecnico'})

    # Validación de garantía
    garantia_vigente = models.BooleanField(default=False, verbose_name='Garantía Vigente')
    fecha_vencimiento_garantia = models.DateField(blank=True, null=True, verbose_name='Fecha Vencimiento Garantía')
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo de Rechazo')

    # Tiempos y fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    fecha_asignacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Asignación')
    fecha_primera_respuesta = models.DateTimeField(blank=True, null=True, verbose_name='Fecha Primera Respuesta')
    fecha_resolucion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Resolución')
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Cierre')

    # Métricas
    tiempo_respuesta_horas = models.PositiveIntegerField(blank=True, null=True, verbose_name='Tiempo de Respuesta (horas)')
    tiempo_resolucion_horas = models.PositiveIntegerField(blank=True, null=True, verbose_name='Tiempo de Resolución (horas)')

    objects = TicketManager()

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['cliente']),
            models.Index(fields=['agente']),
            models.Index(fields=['tecnico']),
            models.Index(fields=['created_at']),
            models.Index(fields=['numero_factura']),
            models.Index(fields=['numero_serie']),
        ]

    def __str__(self):
        return f"Ticket #{str(self.id)[:8]} - {self.asunto}"

    def save(self, *args, **kwargs):
        # Actualizar fecha de cierre cuando el estado cambia a cerrado
        if self.estado == 'cerrado' and not self.closed_at:
            self.closed_at = timezone.now()
            if not self.fecha_resolucion:
                self.fecha_resolucion = timezone.now()

        # Calcular tiempos de respuesta y resolución
        if self.fecha_primera_respuesta and not self.tiempo_respuesta_horas:
            delta = self.fecha_primera_respuesta - self.created_at
            self.tiempo_respuesta_horas = int(delta.total_seconds() / 3600)

        if self.fecha_resolucion and not self.tiempo_resolucion_horas:
            delta = self.fecha_resolucion - self.created_at
            self.tiempo_resolucion_horas = int(delta.total_seconds() / 3600)

        # Validar garantía automáticamente
        if self.fecha_compra and self.categoria:
            dias_transcurridos = (timezone.now().date() - self.fecha_compra).days
            self.garantia_vigente = dias_transcurridos <= self.categoria.dias_garantia_defecto
            self.fecha_vencimiento_garantia = self.fecha_compra + timedelta(days=self.categoria.dias_garantia_defecto)

        super().save(*args, **kwargs)

    def esta_abierto(self):
        """Verifica si el ticket está abierto"""
        return self.estado not in ['cerrado', 'rechazado']

    def esta_cerrado(self):
        """Verifica si el ticket está cerrado"""
        return self.estado in ['cerrado', 'rechazado']

    def puede_ser_editado_por(self, usuario):
        """Verifica si un usuario puede editar el ticket"""
        if usuario.es_superadmin():
            return True
        if usuario.es_cliente() and usuario == self.cliente and self.estado == 'abierto':
            return True
        if usuario.puede_gestionar_tickets() and (self.agente == usuario or self.tecnico == usuario):
            return True
        return False

    def puede_ser_comentado_por(self, usuario):
        """Verifica si un usuario puede comentar en el ticket"""
        if usuario.es_superadmin():
            return True
        if usuario == self.cliente:
            return True
        if usuario.puede_gestionar_tickets():
            return True
        return False

    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación"""
        if self.closed_at:
            delta = self.closed_at - self.created_at
        else:
            delta = timezone.now() - self.created_at

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            return f"{days} días, {hours} horas"
        elif hours > 0:
            return f"{hours} horas, {minutes} minutos"
        else:
            return f"{minutes} minutos"

    def get_tiempo_limite_respuesta(self):
        """Retorna el tiempo límite de respuesta según la prioridad"""
        limites = {
            'critica': timedelta(hours=1),
            'alta': timedelta(hours=4),
            'media': timedelta(hours=24),
            'baja': timedelta(hours=72),
        }
        return limites.get(self.prioridad, timedelta(hours=24))

    def esta_vencido(self):
        """Verifica si el ticket ha superado el tiempo de respuesta esperado"""
        if self.estado in ['cerrado', 'rechazado']:
            return False

        tiempo_limite = self.get_tiempo_limite_respuesta()
        return timezone.now() > (self.created_at + tiempo_limite)

    def asignar_automaticamente(self):
        """Asigna automáticamente el ticket al agente con menos carga"""
        if not self.agente and self.estado == 'abierto':
            agente_disponible = User.objects.agentes_disponibles().first()
            if agente_disponible and agente_disponible.puede_recibir_mas_tickets():
                self.agente = agente_disponible
                self.fecha_asignacion = timezone.now()
                self.estado = 'en_revision'
                self.save()
                return True
        return False

    def derivar_a_tecnico(self):
        """Deriva el ticket a un técnico disponible"""
        if self.estado == 'aceptado':
            tecnico_disponible = User.objects.tecnicos_disponibles().first()
            if tecnico_disponible and tecnico_disponible.puede_recibir_mas_tickets():
                self.tecnico = tecnico_disponible
                self.estado = 'en_reparacion'
                self.save()
                return True
        return False

    def calcular_prioridad_automatica(self):
        """Calcula la prioridad automáticamente basada en criterios"""
        # Lógica para calcular prioridad automática
        if self.tipo_reclamo == 'garantia' and not self.garantia_vigente:
            return 'baja'
        elif self.categoria and 'critico' in self.categoria.nombre.lower():
            return 'alta'
        elif self.tipo_reclamo == 'devolucion':
            return 'media'
        else:
            return 'media'


class Comentario(models.Model):
    """Modelo para los comentarios en tickets"""

    VISIBILIDAD_CHOICES = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios', verbose_name='Ticket')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    texto = models.TextField(verbose_name='Comentario')
    visibilidad = models.CharField(max_length=10, choices=VISIBILIDAD_CHOICES, default='publico', verbose_name='Visibilidad')

    # Campos adicionales para mejor seguimiento
    es_respuesta_inicial = models.BooleanField(default=False, verbose_name='Es respuesta inicial')
    resuelve_ticket = models.BooleanField(default=False, verbose_name='Resuelve el ticket')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket']),
            models.Index(fields=['autor']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Comentario de {self.autor.get_full_name()} en {self.ticket}"

    def save(self, *args, **kwargs):
        # Marcar fecha de primera respuesta en el ticket si es la primera respuesta del agente
        if not self.pk and self.autor.puede_gestionar_tickets() and not self.ticket.fecha_primera_respuesta:
            self.ticket.fecha_primera_respuesta = timezone.now()
            self.es_respuesta_inicial = True
            self.ticket.save()

        # Si el comentario resuelve el ticket, actualizar estado
        if self.resuelve_ticket and self.ticket.estado != 'resuelto':
            self.ticket.estado = 'resuelto'
            self.ticket.fecha_resolucion = timezone.now()
            self.ticket.save()

        super().save(*args, **kwargs)

    def es_visible_para(self, usuario):
        """Verifica si el comentario es visible para un usuario"""
        if self.visibilidad == 'publico':
            return True

        # Los comentarios privados solo son visibles para:
        # - El autor del comentario
        # - Personal de soporte/técnico/admin
        # - El cliente propietario del ticket (en algunos casos)
        if usuario == self.autor:
            return True

        if usuario.puede_gestionar_tickets():
            return True

        # El cliente puede ver comentarios privados dirigidos a él
        if usuario == self.ticket.cliente and 'cliente' in self.texto.lower():
            return True

        return False
    
    def es_visible_para(self, usuario):
        """Verifica si un comentario es visible para un usuario"""
        if self.visibilidad == 'publica':
            return True
        if self.visibilidad == 'privada' and usuario.puede_gestionar_tickets():
            return True
        return False