from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Evento(models.Model):
    """
    Bitácora de eventos para auditoría del sistema
    """
    TIPOS_EVENTO = [
        ('creacion', 'Creación de Ticket'),
        ('asignacion', 'Asignación de Agente'),
        ('cambio_estado', 'Cambio de Estado'),
        ('comentario', 'Nuevo Comentario'),
        ('adjunto', 'Archivo Adjuntado'),
        ('cierre', 'Cierre de Ticket'),
        ('reapertura', 'Reapertura de Ticket'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Usamos CharField para evitar dependencia circular con tickets
    ticket_id = models.UUIDField()
    tipo = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    descripcion = models.TextField()
    datos_json = models.JSONField(default=dict, blank=True)  # Datos adicionales del evento
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_id', 'created_at']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - Ticket {str(self.ticket_id)[:8]}"