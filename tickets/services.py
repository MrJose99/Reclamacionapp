"""
Servicios para el sistema de tickets
Incluye balanceo de carga, notificaciones y validaciones automáticas
"""

import logging
from datetime import datetime, timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import Ticket, Comentario

User = get_user_model()
logger = logging.getLogger(__name__)


class BalanceadorCarga:
    """Servicio para balancear la carga de trabajo entre agentes y técnicos"""
    
    @staticmethod
    def asignar_ticket_automaticamente(ticket):
        """
        Asigna automáticamente un ticket al agente con menos carga de trabajo
        """
        try:
            # Buscar agente disponible con menos carga
            agente_disponible = User.objects.agentes_disponibles().first()
            
            if agente_disponible and agente_disponible.puede_recibir_mas_tickets():
                ticket.agente = agente_disponible
                ticket.fecha_asignacion = timezone.now()
                ticket.estado = 'en_revision'
                ticket.save()
                
                # Enviar notificación al agente
                NotificacionService.notificar_asignacion_ticket(ticket, agente_disponible)
                
                logger.info(f"Ticket {ticket.id} asignado automáticamente a {agente_disponible.username}")
                return True
            else:
                logger.warning(f"No hay agentes disponibles para asignar el ticket {ticket.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al asignar ticket automáticamente: {str(e)}")
            return False
    
    @staticmethod
    def derivar_a_tecnico(ticket):
        """
        Deriva un ticket a un técnico disponible
        """
        try:
            if ticket.estado != 'aceptado':
                return False
            
            # Buscar técnico disponible con menos carga
            tecnico_disponible = User.objects.tecnicos_disponibles().first()
            
            if tecnico_disponible and tecnico_disponible.puede_recibir_mas_tickets():
                ticket.tecnico = tecnico_disponible
                ticket.estado = 'en_reparacion'
                ticket.save()
                
                # Enviar notificación al técnico
                NotificacionService.notificar_derivacion_tecnico(ticket, tecnico_disponible)
                
                logger.info(f"Ticket {ticket.id} derivado a técnico {tecnico_disponible.username}")
                return True
            else:
                logger.warning(f"No hay técnicos disponibles para derivar el ticket {ticket.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al derivar ticket a técnico: {str(e)}")
            return False
    
    @staticmethod
    def redistribuir_carga():
        """
        Redistribuye tickets sin asignar entre agentes disponibles
        """
        tickets_sin_asignar = Ticket.objects.sin_asignar()
        asignados = 0
        
        for ticket in tickets_sin_asignar:
            if BalanceadorCarga.asignar_ticket_automaticamente(ticket):
                asignados += 1
        
        logger.info(f"Redistribuidos {asignados} tickets sin asignar")
        return asignados
    
    @staticmethod
    def obtener_estadisticas_carga():
        """
        Obtiene estadísticas de carga de trabajo por agente y técnico
        """
        agentes_stats = User.objects.soporte().annotate(
            tickets_activos=Count('tickets_asignados', filter=Q(
                tickets_asignados__estado__in=['abierto', 'en_revision', 'aceptado', 'en_espera_cliente']
            )),
            tickets_vencidos=Count('tickets_asignados', filter=Q(
                tickets_asignados__created_at__lt=timezone.now() - timedelta(hours=24),
                tickets_asignados__estado__in=['abierto', 'en_revision']
            ))
        ).values('username', 'first_name', 'last_name', 'tickets_activos', 'tickets_vencidos', 'max_tickets_simultaneos')
        
        tecnicos_stats = User.objects.soporte_tecnico().annotate(
            tickets_activos=Count('tickets_tecnicos', filter=Q(
                tickets_tecnicos__estado='en_reparacion'
            ))
        ).values('username', 'first_name', 'last_name', 'tickets_activos', 'max_tickets_simultaneos')
        
        return {
            'agentes': list(agentes_stats),
            'tecnicos': list(tecnicos_stats)
        }


class NotificacionService:
    """Servicio para envío de notificaciones por email"""
    
    @staticmethod
    def enviar_email(destinatario, asunto, template_html, template_txt, contexto):
        """
        Envía un email usando templates HTML y texto plano
        """
        try:
            if not destinatario.recibir_notificaciones:
                return False
            
            html_content = render_to_string(template_html, contexto)
            text_content = render_to_string(template_txt, contexto)
            
            msg = EmailMultiAlternatives(
                subject=asunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email enviado a {destinatario.email}: {asunto}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email a {destinatario.email}: {str(e)}")
            return False
    
    @staticmethod
    def notificar_nuevo_ticket(ticket):
        """Notifica la creación de un nuevo ticket"""
        contexto = {
            'ticket': ticket,
            'cliente': ticket.cliente,
            'url_ticket': f"{settings.SITE_URL}/tickets/{ticket.id}/"
        }
        
        # Notificar al cliente
        NotificacionService.enviar_email(
            destinatario=ticket.cliente,
            asunto=f"Ticket #{str(ticket.id)[:8]} creado exitosamente",
            template_html='emails/ticket_creado.html',
            template_txt='emails/ticket_creado.txt',
            contexto=contexto
        )
    
    @staticmethod
    def notificar_asignacion_ticket(ticket, agente):
        """Notifica la asignación de un ticket a un agente"""
        contexto = {
            'ticket': ticket,
            'agente': agente,
            'url_ticket': f"{settings.SITE_URL}/tickets/{ticket.id}/"
        }
        
        # Notificar al agente
        NotificacionService.enviar_email(
            destinatario=agente,
            asunto=f"Nuevo ticket asignado: #{str(ticket.id)[:8]}",
            template_html='emails/ticket_asignado.html',
            template_txt='emails/ticket_asignado.txt',
            contexto=contexto
        )
        
        # Notificar al cliente
        NotificacionService.enviar_email(
            destinatario=ticket.cliente,
            asunto=f"Su ticket #{str(ticket.id)[:8]} está siendo revisado",
            template_html='emails/ticket_en_revision.html',
            template_txt='emails/ticket_en_revision.txt',
            contexto=contexto
        )
    
    @staticmethod
    def notificar_derivacion_tecnico(ticket, tecnico):
        """Notifica la derivación de un ticket a un técnico"""
        contexto = {
            'ticket': ticket,
            'tecnico': tecnico,
            'url_ticket': f"{settings.SITE_URL}/tickets/{ticket.id}/"
        }
        
        # Notificar al técnico
        NotificacionService.enviar_email(
            destinatario=tecnico,
            asunto=f"Ticket derivado para reparación: #{str(ticket.id)[:8]}",
            template_html='emails/ticket_derivado_tecnico.html',
            template_txt='emails/ticket_derivado_tecnico.txt',
            contexto=contexto
        )
    
    @staticmethod
    def notificar_cambio_estado(ticket, estado_anterior, usuario_que_cambio):
        """Notifica cambios de estado en un ticket"""
        contexto = {
            'ticket': ticket,
            'estado_anterior': estado_anterior,
            'estado_nuevo': ticket.get_estado_display(),
            'usuario_que_cambio': usuario_que_cambio,
            'url_ticket': f"{settings.SITE_URL}/tickets/{ticket.id}/"
        }
        
        # Notificar al cliente siempre
        NotificacionService.enviar_email(
            destinatario=ticket.cliente,
            asunto=f"Actualización en su ticket #{str(ticket.id)[:8]}",
            template_html='emails/cambio_estado.html',
            template_txt='emails/cambio_estado.txt',
            contexto=contexto
        )
        
        # Notificar al agente si no fue quien hizo el cambio
        if ticket.agente and ticket.agente != usuario_que_cambio:
            NotificacionService.enviar_email(
                destinatario=ticket.agente,
                asunto=f"Cambio de estado en ticket #{str(ticket.id)[:8]}",
                template_html='emails/cambio_estado.html',
                template_txt='emails/cambio_estado.txt',
                contexto=contexto
            )
    
    @staticmethod
    def notificar_nuevo_comentario(comentario):
        """Notifica cuando se agrega un nuevo comentario"""
        ticket = comentario.ticket
        contexto = {
            'comentario': comentario,
            'ticket': ticket,
            'autor': comentario.autor,
            'url_ticket': f"{settings.SITE_URL}/tickets/{ticket.id}/"
        }
        
        # Lista de usuarios a notificar
        usuarios_a_notificar = []
        
        # Siempre notificar al cliente si no es el autor
        if ticket.cliente != comentario.autor:
            usuarios_a_notificar.append(ticket.cliente)
        
        # Notificar al agente si no es el autor
        if ticket.agente and ticket.agente != comentario.autor:
            usuarios_a_notificar.append(ticket.agente)
        
        # Notificar al técnico si no es el autor
        if ticket.tecnico and ticket.tecnico != comentario.autor:
            usuarios_a_notificar.append(ticket.tecnico)
        
        # Enviar notificaciones
        for usuario in usuarios_a_notificar:
            if comentario.es_visible_para(usuario):
                NotificacionService.enviar_email(
                    destinatario=usuario,
                    asunto=f"Nuevo comentario en ticket #{str(ticket.id)[:8]}",
                    template_html='emails/nuevo_comentario.html',
                    template_txt='emails/nuevo_comentario.txt',
                    contexto=contexto
                )


class ValidadorGarantia:
    """Servicio para validar garantías automáticamente"""
    
    @staticmethod
    def validar_garantia(ticket):
        """
        Valida si un ticket tiene garantía vigente
        """
        try:
            if not ticket.fecha_compra or not ticket.categoria:
                return False, "Faltan datos para validar la garantía"
            
            dias_transcurridos = (timezone.now().date() - ticket.fecha_compra).days
            dias_garantia = ticket.categoria.dias_garantia_defecto
            
            if dias_transcurridos <= dias_garantia:
                ticket.garantia_vigente = True
                ticket.fecha_vencimiento_garantia = ticket.fecha_compra + timedelta(days=dias_garantia)
                ticket.save()
                return True, f"Garantía vigente. Vence el {ticket.fecha_vencimiento_garantia.strftime('%d/%m/%Y')}"
            else:
                ticket.garantia_vigente = False
                ticket.fecha_vencimiento_garantia = ticket.fecha_compra + timedelta(days=dias_garantia)
                ticket.save()
                dias_vencida = dias_transcurridos - dias_garantia
                return False, f"Garantía vencida hace {dias_vencida} días"
                
        except Exception as e:
            logger.error(f"Error al validar garantía del ticket {ticket.id}: {str(e)}")
            return False, "Error al validar la garantía"
    
    @staticmethod
    def validar_documentos_requeridos(ticket):
        """
        Valida que el ticket tenga todos los documentos requeridos
        """
        errores = []
        
        if ticket.categoria.requiere_factura and not ticket.numero_factura:
            errores.append("Se requiere número de factura")
        
        if ticket.categoria.requiere_numero_serie and not ticket.numero_serie:
            errores.append("Se requiere número de serie")
        
        if not ticket.fecha_compra:
            errores.append("Se requiere fecha de compra")
        
        # Verificar si hay adjuntos de factura
        adjuntos_factura = ticket.adjuntos.filter(tipo_archivo='documento')
        if ticket.categoria.requiere_factura and not adjuntos_factura.exists():
            errores.append("Se requiere adjuntar copia de la factura")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def procesar_validacion_completa(ticket):
        """
        Procesa la validación completa de un ticket
        """
        resultados = {
            'garantia_valida': False,
            'documentos_completos': False,
            'errores': [],
            'advertencias': []
        }
        
        # Validar garantía
        garantia_valida, mensaje_garantia = ValidadorGarantia.validar_garantia(ticket)
        resultados['garantia_valida'] = garantia_valida
        
        if not garantia_valida:
            resultados['errores'].append(mensaje_garantia)
        else:
            resultados['advertencias'].append(mensaje_garantia)
        
        # Validar documentos
        documentos_ok, errores_docs = ValidadorGarantia.validar_documentos_requeridos(ticket)
        resultados['documentos_completos'] = documentos_ok
        
        if not documentos_ok:
            resultados['errores'].extend(errores_docs)
        
        # Determinar si el ticket puede ser aceptado
        resultados['puede_ser_aceptado'] = garantia_valida and documentos_ok
        
        return resultados


class MetricasService:
    """Servicio para generar métricas y reportes"""
    
    @staticmethod
    def obtener_metricas_generales(fecha_inicio=None, fecha_fin=None):
        """
        Obtiene métricas generales del sistema
        """
        if not fecha_inicio:
            fecha_inicio = timezone.now() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now()
        
        tickets_periodo = Ticket.objects.filter(
            created_at__range=[fecha_inicio, fecha_fin]
        )
        
        metricas = {
            'total_tickets': tickets_periodo.count(),
            'tickets_abiertos': tickets_periodo.filter(estado='abierto').count(),
            'tickets_en_revision': tickets_periodo.filter(estado='en_revision').count(),
            'tickets_aceptados': tickets_periodo.filter(estado='aceptado').count(),
            'tickets_en_reparacion': tickets_periodo.filter(estado='en_reparacion').count(),
            'tickets_resueltos': tickets_periodo.filter(estado='resuelto').count(),
            'tickets_cerrados': tickets_periodo.filter(estado='cerrado').count(),
            'tickets_rechazados': tickets_periodo.filter(estado='rechazado').count(),
            'tiempo_promedio_respuesta': 0,
            'tiempo_promedio_resolucion': 0,
            'tickets_vencidos': 0
        }
        
        # Calcular tiempos promedio
        tickets_con_respuesta = tickets_periodo.exclude(tiempo_respuesta_horas__isnull=True)
        if tickets_con_respuesta.exists():
            metricas['tiempo_promedio_respuesta'] = tickets_con_respuesta.aggregate(
                promedio=models.Avg('tiempo_respuesta_horas')
            )['promedio'] or 0
        
        tickets_resueltos = tickets_periodo.exclude(tiempo_resolucion_horas__isnull=True)
        if tickets_resueltos.exists():
            metricas['tiempo_promedio_resolucion'] = tickets_resueltos.aggregate(
                promedio=models.Avg('tiempo_resolucion_horas')
            )['promedio'] or 0
        
        # Contar tickets vencidos
        metricas['tickets_vencidos'] = sum(1 for ticket in tickets_periodo if ticket.esta_vencido())
        
        return metricas
    
    @staticmethod
    def obtener_metricas_por_agente(fecha_inicio=None, fecha_fin=None):
        """
        Obtiene métricas por agente
        """
        if not fecha_inicio:
            fecha_inicio = timezone.now() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now()
        
        agentes = User.objects.soporte()
        metricas_agentes = []
        
        for agente in agentes:
            tickets_agente = Ticket.objects.filter(
                agente=agente,
                created_at__range=[fecha_inicio, fecha_fin]
            )
            
            metricas_agente = {
                'agente': agente,
                'total_tickets': tickets_agente.count(),
                'tickets_activos': tickets_agente.activos().count(),
                'tickets_resueltos': tickets_agente.filter(estado='resuelto').count(),
                'tickets_cerrados': tickets_agente.filter(estado='cerrado').count(),
                'tiempo_promedio_respuesta': 0,
                'tiempo_promedio_resolucion': 0
            }
            
            # Calcular tiempos promedio
            tickets_con_respuesta = tickets_agente.exclude(tiempo_respuesta_horas__isnull=True)
            if tickets_con_respuesta.exists():
                metricas_agente['tiempo_promedio_respuesta'] = tickets_con_respuesta.aggregate(
                    promedio=models.Avg('tiempo_respuesta_horas')
                )['promedio'] or 0
            
            tickets_resueltos = tickets_agente.exclude(tiempo_resolucion_horas__isnull=True)
            if tickets_resueltos.exists():
                metricas_agente['tiempo_promedio_resolucion'] = tickets_resueltos.aggregate(
                    promedio=models.Avg('tiempo_resolucion_horas')
                )['promedio'] or 0
            
            metricas_agentes.append(metricas_agente)
        
        return metricas_agentes