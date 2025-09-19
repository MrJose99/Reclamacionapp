from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from tickets.models import Ticket, Comentario
from attachments.models import Adjunto
from .models import Evento

User = get_user_model()


@receiver(post_save, sender=Ticket)
def crear_evento_ticket(sender, instance, created, **kwargs):
    """
    Crear evento de auditoría cuando se crea o modifica un ticket
    """
    if created:
        Evento.objects.create(
            ticket_id=instance.id,
            tipo='creacion',
            descripcion=f'Ticket creado: {instance.asunto}',
            datos_json={
                'numero_factura': instance.numero_factura,
                'categoria': instance.categoria.nombre if instance.categoria else None,
                'prioridad': instance.prioridad,
            },
            actor=instance.cliente
        )
    else:
        # Detectar cambios de estado o asignación
        if hasattr(instance, '_estado_anterior'):
            if instance._estado_anterior != instance.estado:
                Evento.objects.create(
                    ticket_id=instance.id,
                    tipo='cambio_estado',
                    descripcion=f'Estado cambiado de {instance._estado_anterior} a {instance.estado}',
                    datos_json={
                        'estado_anterior': instance._estado_anterior,
                        'estado_nuevo': instance.estado,
                    },
                    actor=getattr(instance, '_usuario_modificador', None)
                )


@receiver(post_save, sender=Comentario)
def crear_evento_comentario(sender, instance, created, **kwargs):
    """
    Crear evento de auditoría cuando se crea un comentario
    """
    if created:
        Evento.objects.create(
            ticket_id=instance.ticket.id,
            tipo='comentario',
            descripcion=f'Nuevo comentario de {instance.autor.get_full_name()}',
            datos_json={
                'visibilidad': instance.visibilidad,
                'longitud_texto': len(instance.texto),
            },
            actor=instance.autor
        )


@receiver(post_save, sender=Adjunto)
def crear_evento_adjunto(sender, instance, created, **kwargs):
    """
    Crear evento de auditoría cuando se sube un adjunto
    """
    if created:
        Evento.objects.create(
            ticket_id=instance.objeto_id,
            tipo='adjunto',
            descripcion=f'Archivo adjuntado: {instance.nombre_original}',
            datos_json={
                'tipo_archivo': instance.tipo_archivo,
                'tamaño_bytes': instance.tamaño_bytes,
                'tipo_objeto': instance.tipo_objeto,
            },
            actor=None  # Se puede mejorar pasando el usuario desde la vista
        )