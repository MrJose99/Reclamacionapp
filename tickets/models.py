from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class CategoriaManager(models.Manager):
    """
    Manager personalizado para Categoria
    """
    def activas(self):
        return self.filter(activa=True)


class TicketManager(models.Manager):
    """
    Manager personalizado para Ticket
    """
    def abiertos(self):
        return self.filter(estado='abierto')
    
    def en_revision(self):
        return self.filter(estado='en_revision')
    
    def resueltos(self):
        return self.filter(estado='resuelto')
    
    def cerrados(self):
        return self.filter(estado='cerrado')
    
    def por_cliente(self, cliente):
        return self.filter(cliente=cliente)
    
    def por_agente(self, agente):
        return self.filter(agente=agente)
    
    def sin_asignar(self):
        return self.filter(agente__isnull=True)
    
    def por_prioridad(self, prioridad):
        return self.filter(prioridad=prioridad)


class Categoria(models.Model):
    """
    Categorías para clasificar los tickets de reclamación
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CategoriaManager()
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    """
    Modelo principal para los tickets de reclamación/garantía
    """
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    ESTADOS = [
        ('abierto', 'Abierto'),
        ('en_revision', 'En Revisión'),
        ('en_espera_cliente', 'En Espera de Cliente'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Identificador único del ticket
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Campos obligatorios
    numero_factura = models.CharField(
        max_length=50, 
        help_text="Número de factura asociado a la reclamación"
    )
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Campos opcionales
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto')
    
    # Relaciones con usuarios
    cliente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tickets_creados'
    )
    agente = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tickets_asignados',
        limit_choices_to={'rol__in': ['empleado', 'admin']}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    objects = TicketManager()
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['numero_factura']),
            models.Index(fields=['estado']),
            models.Index(fields=['cliente']),
            models.Index(fields=['agente']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Ticket {str(self.id)[:8]} - {self.asunto}"
    
    def save(self, *args, **kwargs):
        # Actualizar closed_at cuando el estado cambia a cerrado
        if self.estado == 'cerrado' and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.estado != 'cerrado':
            self.closed_at = None
        
        super().save(*args, **kwargs)
    
    def esta_abierto(self):
        return self.estado == 'abierto'
    
    def esta_cerrado(self):
        return self.estado == 'cerrado'
    
    def puede_ser_editado_por(self, usuario):
        """Verifica si un usuario puede editar este ticket"""
        if usuario.es_admin():
            return True
        if usuario.es_empleado() and self.agente == usuario:
            return True
        if usuario.es_cliente() and self.cliente == usuario and self.esta_abierto():
            return True
        return False
    
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación"""
        return timezone.now() - self.created_at


class Comentario(models.Model):
    """
    Comentarios en los tickets
    """
    VISIBILIDADES = [
        ('publica', 'Pública'),
        ('privada', 'Privada (Solo Empleados)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    visibilidad = models.CharField(max_length=10, choices=VISIBILIDADES, default='publica')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comentario de {self.autor.get_full_name()} en {self.ticket}"
    
    def es_visible_para(self, usuario):
        """Verifica si un comentario es visible para un usuario"""
        if self.visibilidad == 'publica':
            return True
        if self.visibilidad == 'privada' and usuario.puede_gestionar_tickets():
            return True
        return False