import uuid
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.utils import (
    generar_nombre_unico,
    obtener_tipo_mime,
    es_imagen,
    es_video,
    es_documento,
    validar_tamaño_archivo
)
from django.core.exceptions import ValidationError  # ← AGREGAR ESTA LÍNEA

def upload_to_ticket(instance, filename):
    """
    Función para determinar la ruta de subida de archivos
    Organiza los archivos por ticket y tipo de objeto
    """
    # Generar nombre único para evitar conflictos
    nombre_unico = generar_nombre_unico(filename)

    if instance.tipo_objeto == 'ticket':
        return f'tickets/{instance.objeto_id}/{nombre_unico}'
    elif instance.tipo_objeto == 'comentario':
        # Obtener el ticket del comentario para organizar mejor
        try:
            from tickets.models import Comentario
            comentario = Comentario.objects.get(id=instance.objeto_id)
            return f'tickets/{comentario.ticket.id}/comentarios/{instance.objeto_id}/{nombre_unico}'
        except:
            return f'comentarios/{instance.objeto_id}/{nombre_unico}'
    else:
        return f'adjuntos/{instance.objeto_id}/{nombre_unico}'


def validar_extension_archivo(archivo):
    """
    Valida que la extensión del archivo esté permitida
    """
    extensiones_permitidas = [
        # Imágenes
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
        # Videos
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
        # Documentos
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
        # Otros
        '.zip', '.rar', '.7z'
    ]

    nombre_archivo = archivo.name.lower()
    extension = os.path.splitext(nombre_archivo)[1]

    if extension not in extensiones_permitidas:
        raise ValidationError(
            f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(extensiones_permitidas)}'
        )


class AdjuntoManager(models.Manager):
    """Manager personalizado para el modelo Adjunto"""

    def de_ticket(self, ticket_id):
        """Retorna adjuntos de un ticket específico"""
        return self.filter(tipo_objeto='ticket', objeto_id=ticket_id)

    def de_comentario(self, comentario_id):
        """Retorna adjuntos de un comentario específico"""
        return self.filter(tipo_objeto='comentario', objeto_id=comentario_id)

    def imagenes(self):
        """Retorna solo adjuntos de tipo imagen"""
        return self.filter(tipo_archivo='imagen')

    def videos(self):
        """Retorna solo adjuntos de tipo video"""
        return self.filter(tipo_archivo='video')

    def documentos(self):
        """Retorna solo adjuntos de tipo documento"""
        return self.filter(tipo_archivo='documento')

    def por_usuario(self, usuario):
        """Retorna adjuntos subidos por un usuario específico"""
        return self.filter(subido_por=usuario)


class Adjunto(models.Model):
    """
    Modelo para gestionar archivos adjuntos
    Puede estar asociado a tickets o comentarios usando GenericForeignKey
    """

    TIPOS_OBJETO = [
        ('ticket', 'Ticket'),
        ('comentario', 'Comentario'),
    ]

    TIPOS_ARCHIVO = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('documento', 'Documento'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relación genérica para asociar con tickets o comentarios
    objeto_id = models.UUIDField(verbose_name='ID del Objeto')
    tipo_objeto = models.CharField(max_length=20, choices=TIPOS_OBJETO, verbose_name='Tipo de Objeto')

    # Información del archivo
    archivo = models.FileField(
        upload_to=upload_to_ticket,
        validators=[validar_extension_archivo],
        verbose_name='Archivo'
    )
    nombre_original = models.CharField(max_length=255, verbose_name='Nombre Original')
    tipo_archivo = models.CharField(max_length=20, choices=TIPOS_ARCHIVO, verbose_name='Tipo de Archivo')
    tipo_mime = models.CharField(max_length=100, verbose_name='Tipo MIME')
    tamaño_bytes = models.PositiveIntegerField(verbose_name='Tamaño en Bytes')
    checksum = models.CharField(max_length=64, blank=True, null=True, verbose_name='Checksum SHA-256')

    # Metadatos adicionales
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    es_publico = models.BooleanField(default=True, verbose_name='Es Público')
    # Usamos un pequeño wrapper para inyectar temporalmente null=True y blank=True
    # sin modificar las líneas siguientes (se completan en el sufijo).
    _adjunto_fk = lambda *a, **k: models.ForeignKey(*a, null=True, blank=True, **k)
    subido_por = _adjunto_fk(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        verbose_name='Subido Por',
        related_name='adjuntos_subidos'
    )

    # Campos para organización y búsqueda
    etiquetas = models.CharField(max_length=200, blank=True, null=True, verbose_name='Etiquetas')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    objects = AdjuntoManager()

    class Meta:
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['objeto_id', 'tipo_objeto']),
            models.Index(fields=['tipo_archivo']),
            models.Index(fields=['subido_por']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.nombre_original} ({self.get_tipo_archivo_display()})"

    def save(self, *args, **kwargs):
        if self.archivo:
            # Obtener el nombre del archivo de forma segura
            if hasattr(self.archivo, 'name'):
                nombre_archivo = self.archivo.name
            elif hasattr(self.archivo, 'file') and hasattr(self.archivo.file, 'name'):
                nombre_archivo = self.archivo.file.name
            else:
                # Si ya es una string (archivo ya guardado), usar basename
                nombre_archivo = os.path.basename(str(self.archivo))

            # Guardar nombre original solo si no está establecido
            if not self.nombre_original:
                self.nombre_original = nombre_archivo

            # Determinar tipo de archivo basado en la extensión
            if es_imagen(nombre_archivo):
                self.tipo_archivo = 'imagen'
            elif es_video(nombre_archivo):
                self.tipo_archivo = 'video'
            elif es_documento(nombre_archivo):
                self.tipo_archivo = 'documento'
            else:
                self.tipo_archivo = 'otro'

            # Obtener tipo MIME
            self.tipo_mime = obtener_tipo_mime(nombre_archivo)

            # Guardar tamaño del archivo solo si está disponible
            if hasattr(self.archivo, 'size') and self.archivo.size:
                self.tamaño_bytes = self.archivo.size
            elif hasattr(self.archivo, 'file') and hasattr(self.archivo.file, 'size'):
                self.tamaño_bytes = self.archivo.file.size
            elif not self.tamaño_bytes and hasattr(self.archivo, 'path'):
                # Si el archivo ya está guardado, obtener el tamaño del sistema de archivos
                try:
                    self.tamaño_bytes = os.path.getsize(self.archivo.path)
                except:
                    self.tamaño_bytes = 0

            # Validar tamaño del archivo solo si es un archivo nuevo
            if hasattr(self.archivo, 'size'):
                try:
                    validar_tamaño_archivo(self.archivo)
                except ValidationError as e:
                    raise ValidationError(f"Error en el archivo {self.nombre_original}: {str(e)}")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Elimina el archivo físico al eliminar el registro"""
        if self.archivo:
            try:
                if os.path.isfile(self.archivo.path):
                    os.remove(self.archivo.path)
            except:
                pass  # Si no se puede eliminar el archivo, continuar
        super().delete(*args, **kwargs)

    def get_tamaño_legible(self):
        """Retorna el tamaño del archivo en formato legible"""
        from core.utils import formatear_tamaño_archivo
        return formatear_tamaño_archivo(self.tamaño_bytes)

    def es_imagen(self):
        """Verifica si el adjunto es una imagen"""
        return self.tipo_archivo == 'imagen'

    def es_video(self):
        """Verifica si el adjunto es un video"""
        return self.tipo_archivo == 'video'

    def es_documento(self):
        """Verifica si el adjunto es un documento"""
        return self.tipo_archivo == 'documento'

    def puede_ser_visto_por(self, usuario):
        """Verifica si un usuario puede ver este adjunto"""
        # Los adjuntos públicos pueden ser vistos por cualquier usuario autenticado
        if self.es_publico:
            return True

        # El usuario que subió el archivo siempre puede verlo
        if self.subido_por == usuario:
            return True

        # Los superadmins pueden ver todo
        if usuario.es_superadmin():
            return True

        # Lógica específica según el tipo de objeto
        if self.tipo_objeto == 'ticket':
            try:
                from tickets.models import Ticket
                ticket = Ticket.objects.get(id=self.objeto_id)

                # El cliente propietario del ticket puede ver sus adjuntos
                if ticket.cliente == usuario:
                    return True

                # Los agentes y técnicos asignados pueden ver los adjuntos
                if ticket.agente == usuario or ticket.tecnico == usuario:
                    return True

                # Personal de soporte puede ver adjuntos de tickets que pueden gestionar
                if usuario.puede_gestionar_tickets():
                    return True

            except:
                pass

        elif self.tipo_objeto == 'comentario':
            try:
                from tickets.models import Comentario
                comentario = Comentario.objects.get(id=self.objeto_id)
                ticket = comentario.ticket

                # Aplicar las mismas reglas que para los tickets
                if ticket.cliente == usuario or ticket.agente == usuario or ticket.tecnico == usuario:
                    return True

                if usuario.puede_gestionar_tickets():
                    return True

            except:
                pass

        return False

    def puede_ser_eliminado_por(self, usuario):
        """Verifica si un usuario puede eliminar este adjunto"""
        # Solo el usuario que subió el archivo o un superadmin pueden eliminarlo
        if self.subido_por == usuario or usuario.es_superadmin():
            return True

        # Los agentes pueden eliminar adjuntos de sus tickets asignados
        if self.tipo_objeto == 'ticket' and usuario.puede_gestionar_tickets():
            try:
                from tickets.models import Ticket
                ticket = Ticket.objects.get(id=self.objeto_id)
                if ticket.agente == usuario or ticket.tecnico == usuario:
                    return True
            except:
                pass

        return False

    def get_url_descarga(self):
        """Retorna la URL para descargar el adjunto"""
        return f"/attachments/descargar/{self.id}/"

    def get_url_eliminacion(self):
        """Retorna la URL para eliminar el adjunto"""
        return f"/attachments/eliminar/{self.id}/"

    def get_icono_tipo(self):
        """Retorna el icono CSS apropiado según el tipo de archivo"""
        iconos = {
            'imagen': 'bi-image',
            'video': 'bi-camera-video',
            'documento': 'bi-file-text',
            'otro': 'bi-file'
        }
        return iconos.get(self.tipo_archivo, 'bi-file')

    def get_color_tipo(self):
        """Retorna el color CSS apropiado según el tipo de archivo"""
        colores = {
            'imagen': 'text-success',
            'video': 'text-primary',
            'documento': 'text-danger',
            'otro': 'text-secondary'
        }
        return colores.get(self.tipo_archivo, 'text-secondary')


class AdjuntoMultiple(models.Model):
    """
    Modelo auxiliar para manejar múltiples adjuntos en formularios
    Se usa temporalmente durante la subida de múltiples archivos
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, verbose_name='Clave de Sesión')
    adjunto = models.ForeignKey(Adjunto, on_delete=models.CASCADE, verbose_name='Adjunto')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Adjunto Múltiple'
        verbose_name_plural = 'Adjuntos Múltiples'
        ordering = ['orden', 'created_at']

    def __str__(self):
        return f"Adjunto múltiple: {self.adjunto.nombre_original}"