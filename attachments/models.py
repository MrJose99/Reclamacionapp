from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
import os


def upload_to_ticket(instance, filename):
    """
    Función para organizar la subida de archivos por ticket
    """
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Generar nombre único para evitar conflictos
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Organizar por tipo de objeto (ticket o comentario)
    if hasattr(instance, 'ticket_id'):
        return f'tickets/{instance.ticket_id}/comentarios/{filename}'
    else:
        return f'tickets/{instance.objeto_id}/{filename}'


class Adjunto(models.Model):
    """
    Archivos adjuntos para tickets y comentarios
    """
    TIPOS_OBJETO = [
        ('ticket', 'Ticket'),
        ('comentario', 'Comentario'),
    ]
    
    TIPOS_ARCHIVO = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('documento', 'Documento'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relación genérica con ticket o comentario
    objeto_id = models.UUIDField()
    tipo_objeto = models.CharField(max_length=10, choices=TIPOS_OBJETO)
    
    # Información del archivo
    archivo = models.FileField(
        upload_to=upload_to_ticket,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mov', 'pdf']
            )
        ]
    )
    nombre_original = models.CharField(max_length=255)
    tipo_archivo = models.CharField(max_length=10, choices=TIPOS_ARCHIVO)
    tipo_mime = models.CharField(max_length=100)
    tamaño_bytes = models.PositiveIntegerField()
    checksum = models.CharField(max_length=64, blank=True)  # Para verificar integridad
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['objeto_id', 'tipo_objeto']),
        ]
    
    def __str__(self):
        return f"{self.nombre_original} ({self.tipo_archivo})"
    
    def save(self, *args, **kwargs):
        if self.archivo:
            # Determinar tipo de archivo basado en la extensión
            ext = self.archivo.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                self.tipo_archivo = 'imagen'
            elif ext in ['mp4', 'mov']:
                self.tipo_archivo = 'video'
            else:
                self.tipo_archivo = 'documento'
            
            # Guardar tamaño del archivo
            if hasattr(self.archivo, 'size'):
                self.tamaño_bytes = self.archivo.size
        
        super().save(*args, **kwargs)