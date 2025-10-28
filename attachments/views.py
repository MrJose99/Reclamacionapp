from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse, Http404
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Adjunto
from .forms import AdjuntoForm
from tickets.models import Ticket
import mimetypes
import os
import uuid

@login_required
def subir_adjunto(request, ticket_id):
    """Vista para subir adjuntos a un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verificar permisos
    if request.user.es_cliente() and ticket.cliente != request.user:
        return HttpResponseForbidden("No tienes permisos para subir archivos a este ticket.")

    if request.method == 'POST':
        form = AdjuntoForm(request.POST, request.FILES)
        if form.is_valid():
            adjunto = form.save(commit=False)
            adjunto.objeto_id = str(ticket.id)  # Convertir UUID a string
            adjunto.tipo_objeto = 'ticket'
            adjunto.subido_por = request.user  # Asignar el usuario que sube el archivo
            adjunto.save()

            messages.success(request, f'Archivo {adjunto.nombre_original} subido exitosamente.')
            return redirect('tickets:detalle_ticket', ticket_id=ticket.id)
        else:
            messages.error(request, 'Error al subir el archivo. Verifica el formato y tamaño.')

    return redirect('tickets:detalle_ticket', ticket_id=ticket.id)


@login_required
def descargar_adjunto(request, adjunto_id):
    """Vista para descargar un adjunto"""
    adjunto = get_object_or_404(Adjunto, id=adjunto_id)

    # Verificar permisos según el tipo de objeto
    if adjunto.tipo_objeto == 'ticket':
        try:
            # Convertir objeto_id a UUID si es necesario
            if isinstance(adjunto.objeto_id, str):
                ticket_uuid = uuid.UUID(adjunto.objeto_id)
            else:
                ticket_uuid = adjunto.objeto_id
                
            ticket = get_object_or_404(Ticket, id=ticket_uuid)

            # Los clientes solo pueden descargar adjuntos de sus propios tickets
            if request.user.es_cliente() and ticket.cliente != request.user:
                raise PermissionDenied("No tienes permisos para descargar este archivo.")

            # Los empleados pueden descargar adjuntos de tickets asignados o sin asignar
            if request.user.es_empleado() and ticket.agente and ticket.agente != request.user:
                raise PermissionDenied("No tienes permisos para descargar este archivo.")
        except (ValueError, Ticket.DoesNotExist):
            raise Http404("El ticket asociado no existe.")

    # Verificar que el archivo existe
    if not adjunto.archivo or not os.path.exists(adjunto.archivo.path):
        raise Http404("El archivo no existe.")

    # Preparar la respuesta
    try:
        with open(adjunto.archivo.path, 'rb') as archivo:
            response = HttpResponse(archivo.read())

        # Determinar el tipo de contenido
        content_type = adjunto.tipo_mime or mimetypes.guess_type(adjunto.archivo.path)[0] or 'application/octet-stream'
        response['Content-Type'] = content_type
        response['Content-Disposition'] = f'attachment; filename="{adjunto.nombre_original}"'
        response['Content-Length'] = adjunto.tamaño_bytes

        return response

    except Exception as e:
        messages.error(request, 'Error al descargar el archivo.')
        try:
            if isinstance(adjunto.objeto_id, str):
                ticket_uuid = uuid.UUID(adjunto.objeto_id)
            else:
                ticket_uuid = adjunto.objeto_id
            return redirect('tickets:detalle_ticket', ticket_id=ticket_uuid)
        except:
            return redirect('tickets:lista_tickets')


@login_required
def eliminar_adjunto(request, adjunto_id):
    """Vista para eliminar un adjunto"""
    adjunto = get_object_or_404(Adjunto, id=adjunto_id)

    # Solo el superadmin puede eliminar adjuntos
    if not request.user.es_superadmin():
        return HttpResponseForbidden("Solo los superadministradores pueden eliminar archivos.")

    if request.method == 'POST':
        ticket_id = adjunto.objeto_id
        nombre_archivo = adjunto.nombre_original

        # Eliminar el archivo físico
        if adjunto.archivo and os.path.exists(adjunto.archivo.path):
            try:
                os.remove(adjunto.archivo.path)
            except OSError:
                pass

        # Eliminar el registro de la base de datos
        adjunto.delete()

        messages.success(request, f'Archivo {nombre_archivo} eliminado exitosamente.')
        
        # Intentar redirigir al ticket si es posible
        try:
            if isinstance(ticket_id, str):
                ticket_uuid = uuid.UUID(ticket_id)
            else:
                ticket_uuid = ticket_id
            return redirect('tickets:detalle_ticket', ticket_id=ticket_uuid)
        except:
            return redirect('attachments:listar_adjuntos')

    # Si no es POST, redirigir según el tipo de objeto
    try:
        if adjunto.tipo_objeto == 'ticket':
            if isinstance(adjunto.objeto_id, str):
                ticket_uuid = uuid.UUID(adjunto.objeto_id)
            else:
                ticket_uuid = adjunto.objeto_id
            return redirect('tickets:detalle_ticket', ticket_id=ticket_uuid)
    except:
        pass
    
    return redirect('attachments:listar_adjuntos')


@login_required
def listar_adjuntos(request):
    """Vista para listar todos los adjuntos (solo superadmin)"""
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para ver esta página.")

    # Obtener adjuntos con select_related para optimizar
    adjuntos = Adjunto.objects.select_related('subido_por').all().order_by('-created_at')

    # Filtros
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        adjuntos = adjuntos.filter(tipo_archivo=tipo_filtro)

    # Preprocesar adjuntos para evitar errores en el template
    adjuntos_procesados = []
    for adjunto in adjuntos:
        # Asegurar que objeto_id sea una string válida
        try:
            if isinstance(adjunto.objeto_id, uuid.UUID):
                adjunto.objeto_id = str(adjunto.objeto_id)
        except:
            pass
        adjuntos_procesados.append(adjunto)

    context = {
        'adjuntos': adjuntos_procesados,
        'tipo_filtro': tipo_filtro,
        'tipos_archivo': ['imagen', 'video', 'documento', 'otro'],
    }

    return render(request, 'attachments/listar_adjuntos.html', context)