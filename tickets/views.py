from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Ticket, Categoria, Comentario
from .forms import TicketForm, ComentarioForm, AsignarTicketForm
from attachments.models import Adjunto
from attachments.forms import AdjuntoMultipleForm


@login_required
def listar_tickets(request):
    """
    Lista tickets según rol y aplica filtros + paginación.
    URL name: tickets:listar_tickets
    Template: tickets/listar_tickets.html
    """
    usuario = request.user

    # Filtros base según el rol
    if usuario.es_cliente():
        tickets = Ticket.objects.filter(cliente=usuario)
    elif usuario.es_empleado():
        tickets = Ticket.objects.filter(Q(agente=usuario) | Q(agente__isnull=True))
    else:  # superadmin
        tickets = Ticket.objects.all()

    # Filtros GET
    busqueda = request.GET.get('busqueda', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    prioridad_filtro = request.GET.get('prioridad', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()

    if busqueda:
        tickets = tickets.filter(
            Q(numero_factura__icontains=busqueda) |
            Q(asunto__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    if estado_filtro:
        tickets = tickets.filter(estado=estado_filtro)

    if prioridad_filtro:
        tickets = tickets.filter(prioridad=prioridad_filtro)

    if categoria_filtro:
        tickets = tickets.filter(categoria_id=categoria_filtro)

    tickets = tickets.select_related("cliente", "agente", "categoria").order_by('-created_at')

    # Paginación
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'categoria_filtro': categoria_filtro,
        'estados': getattr(Ticket, 'ESTADOS', ()),
        'prioridades': getattr(Ticket, 'PRIORIDADES', ()),
        'categorias': Categoria.objects.activas() if hasattr(Categoria.objects, "activas") else Categoria.objects.all(),
    }
    return render(request, 'tickets/listar_tickets.html', context)


@login_required
def crear_ticket(request):
    """
    Crea un ticket (solo clientes).
    URL name: tickets:crear_ticket
    Template: tickets/crear_ticket.html
    """
    import logging
    logger = logging.getLogger(__name__)

    if not request.user.es_cliente():
        logger.warning(f"Usuario '{request.user}' intentó crear ticket pero no es cliente.")
        return HttpResponseForbidden("Solo los clientes pueden crear tickets.")

    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                ticket = form.save(commit=False)
                ticket.cliente = request.user
                ticket.save()

                # Adjuntos múltiples (campo input name="archivos" en el form)
                archivos = request.FILES.getlist('archivos')
                archivos_guardados = 0
                logger.info(f"Archivos recibidos: {len(archivos)}")

                for archivo in archivos:
                    try:
                        if not archivo or not hasattr(archivo, 'name'):
                            logger.warning("Archivo vacío o inválido ignorado")
                            continue

                        adjunto = Adjunto(
                            objeto_id=str(ticket.id),  # asegurar string si tu modelo Adjunto lo espera
                            tipo_objeto='ticket',
                            archivo=archivo,
                            nombre_original=archivo.name,
                            subido_por=request.user,
                            es_publico=True
                        )
                        adjunto.save()
                        archivos_guardados += 1
                        logger.info(f"Adjunto guardado: {adjunto.nombre_original}")
                    except ValidationError as e:
                        logger.error(f"Validación adjunto {archivo.name}: {e}")
                        messages.warning(request, f"Archivo {archivo.name} no válido: {e}")
                    except Exception as e:
                        logger.exception(f"Error al guardar archivo {getattr(archivo, 'name', '(sin nombre)')}")
                        messages.warning(request, f"No se pudo guardar el archivo {getattr(archivo, 'name', '(sin nombre)')}: {e}")

                if archivos_guardados > 0:
                    messages.success(request, f'Ticket creado exitosamente con {archivos_guardados} archivo(s) adjunto(s).')
                else:
                    messages.success(request, 'Ticket creado exitosamente.')

                # Redirigir al detalle con el nombre de URL correcto
                return redirect('tickets:detalle_ticket', ticket_id=ticket.id)

            except Exception as e:
                logger.exception(f"Error al crear ticket: {e}")
                messages.error(request, f'Error al crear el ticket: {e}')
        else:
            # Mostrar errores de validación de campos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = TicketForm(user=request.user)

    return render(request, 'tickets/crear_ticket.html', {'form': form})


@login_required  
def detalle_ticket(request, ticket_id):  
    """  
    Detalle de ticket con comentarios y adjuntos.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
  
    # Permisos de visualización  
    if request.user.es_cliente() and ticket.cliente != request.user:  
        return HttpResponseForbidden("No tienes permisos para ver este ticket.")  
  
    # Comentarios según visibilidad  
    comentarios = ticket.comentarios.all()  
    if request.user.es_cliente():  
        comentarios = comentarios.filter(visibilidad='publico')  
  
    # Adjuntos de este ticket  
    adjuntos = Adjunto.objects.filter(objeto_id=str(ticket.id), tipo_objeto='ticket')  
  
    # Formularios  
    comentario_form = ComentarioForm()  
    adjunto_form = AdjuntoMultipleForm(user=request.user)  
    asignar_form = AsignarTicketForm(instance=ticket) if request.user.puede_gestionar_tickets() else None  
  
    context = {  
        'ticket': ticket,  
        'comentarios': comentarios,  
        'adjuntos': adjuntos,  
        'comentario_form': comentario_form,  
        'adjunto_form': adjunto_form,  
        'asignar_form': asignar_form,  
        'puede_editar': ticket.puede_ser_editado_por(request.user),  
    }  
    return render(request, 'tickets/detalle_ticket.html', context)  
  
  
@login_required  
def agregar_comentario(request, ticket_id):  
    """  
    Agregar un comentario al ticket con archivos adjuntos opcionales.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
      
    if not ticket.puede_ser_comentado_por(request.user):  
        messages.error(request, "No tienes permisos para comentar en este ticket.")  
        return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
      
    if request.method == 'POST':  
        form = ComentarioForm(request.POST, request.FILES)  
        if form.is_valid():  
            comentario = form.save(commit=False)  
            comentario.ticket = ticket  
            comentario.autor = request.user  
              
            # Si es personal de soporte, puede elegir visibilidad  
            if request.user.puede_gestionar_tickets():  
                comentario.visibilidad = form.cleaned_data.get('visibilidad', 'publico')  
            else:  
                comentario.visibilidad = 'publico'  
              
            comentario.save()  
              
            # Procesar archivos adjuntos si existen  
            archivos = request.FILES.getlist('archivos')  
            for archivo in archivos:  
                Adjunto.objects.create(  
                    archivo=archivo,  
                    nombre_original=archivo.name,  
                    tipo_objeto='comentario',  
                    objeto_id=str(comentario.id),  
                    subido_por=request.user  
                )  
              
            messages.success(request, "Comentario agregado exitosamente.")  
            return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
        else:  
            messages.error(request, "Error al agregar el comentario.")  
      
    return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
  
  
@login_required  
def agregar_adjuntos(request, ticket_id):  
    """  
    Agregar archivos adjuntos adicionales al ticket.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
      
    if not (ticket.puede_ser_editado_por(request.user) or request.user.puede_gestionar_tickets()):  
        messages.error(request, "No tienes permisos para agregar archivos a este ticket.")  
        return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
      
    if request.method == 'POST':  
        archivos = request.FILES.getlist('archivos')  
        if archivos:  
            for archivo in archivos:  
                Adjunto.objects.create(  
                    archivo=archivo,  
                    nombre_original=archivo.name,  
                    tipo_objeto='ticket',  
                    objeto_id=str(ticket.id),  
                    subido_por=request.user  
                )  
            messages.success(request, f"{len(archivos)} archivo(s) agregado(s) exitosamente.")  
        else:  
            messages.warning(request, "No se seleccionaron archivos.")  
      
    return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
  
  
@login_required  
def cambiar_estado(request, ticket_id):  
    """  
    Cambiar el estado del ticket.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
      
    if not request.user.puede_gestionar_tickets():  
        messages.error(request, "No tienes permisos para cambiar el estado del ticket.")  
        return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
      
    if request.method == 'POST':  
        nuevo_estado = request.POST.get('estado')  
        motivo = request.POST.get('motivo', '')  
          
        if nuevo_estado in dict(Ticket.ESTADOS):  
            estado_anterior = ticket.get_estado_display()  
            ticket.estado = nuevo_estado  
              
            # Actualizar fechas según el estado  
            if nuevo_estado == 'resuelto' and not ticket.fecha_resolucion:  
                ticket.fecha_resolucion = timezone.now()  
            elif nuevo_estado == 'cerrado' and not ticket.closed_at:  
                ticket.closed_at = timezone.now()  
            elif nuevo_estado == 'rechazado':  
                ticket.motivo_rechazo = motivo  
              
            ticket.save()  
              
            # Crear comentario automático del cambio de estado  
            texto_comentario = f"Estado cambiado de '{estado_anterior}' a '{ticket.get_estado_display()}'"  
            if motivo:  
                texto_comentario += f"\n\nMotivo: {motivo}"  
              
            Comentario.objects.create(  
                ticket=ticket,  
                autor=request.user,  
                texto=texto_comentario,  
                visibilidad='publico'  
            )  
              
            messages.success(request, f"Estado actualizado a '{ticket.get_estado_display()}'.")  
        else:  
            messages.error(request, "Estado inválido.")  
      
    return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
  
  
@login_required  
def asignar_personal(request, ticket_id):  
    """  
    Asignar agente o técnico al ticket.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
      
    if not request.user.puede_gestionar_tickets():  
        messages.error(request, "No tienes permisos para asignar personal.")  
        return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
      
    if request.method == 'POST':  
        form = AsignarTicketForm(request.POST, instance=ticket)  
        if form.is_valid():  
            form.save()  
              
            # Crear comentario de asignación  
            if ticket.agente:  
                Comentario.objects.create(  
                    ticket=ticket,  
                    autor=request.user,  
                    texto=f"Ticket asignado a {ticket.agente.get_full_name()}",  
                    visibilidad='privado'  
                )  
              
            messages.success(request, "Personal asignado exitosamente.")  
        else:  
            messages.error(request, "Error al asignar personal.")  
      
    return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
  
  
@login_required  
def resolver_ticket(request, ticket_id):  
    """  
    Marcar ticket como resuelto con descripción de resolución.  
    """  
    ticket = get_object_or_404(Ticket, id=ticket_id)  
      
    if not request.user.puede_gestionar_tickets():  
        messages.error(request, "No tienes permisos para resolver tickets.")  
        return redirect('tickets:detalle_ticket', ticket_id=ticket_id)  
      
    if request.method == 'POST':  
        resolucion = request.POST.get('resolucion', '')  
          
        if resolucion:  
            ticket.estado = 'resuelto'  
            ticket.fecha_resolucion = timezone.now()  
            ticket.save()  
              
            # Crear comentario con la resolución  
            Comentario.objects.create(  
                ticket=ticket,  
                autor=request.user,  
                texto=f"**TICKET RESUELTO**\n\n{resolucion}",  
                visibilidad='publico',  
                resuelve_ticket=True  
            )  
              
            messages.success(request, "Ticket marcado como resuelto.")  
        else:  
            messages.error(request, "Debes proporcionar una descripción de la resolución.")  
      
    return redirect('tickets:detalle_ticket', ticket_id=ticket_id)

@login_required
def editar_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('tickets:detalle_ticket', ticket_id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/editar_ticket.html', {'form': form, 'ticket': ticket})



@login_required
def asignar_ticket(request, ticket_id):
    """
    Asigna o desasigna ticket a un empleado (empleados/superadmin).
    URL sugerida: tickets:asignar
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.puede_gestionar_tickets():
        return HttpResponseForbidden("No tienes permisos para asignar tickets.")

    if request.method == 'POST':
        form = AsignarTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()

            if ticket.agente:
                Comentario.objects.create(
                    ticket=ticket,
                    autor=request.user,
                    texto=f'Ticket asignado a {ticket.agente.get_full_name() or ticket.agente.username}',
                    visibilidad='privada'
                )
                messages.success(request, f'Ticket asignado a {ticket.agente.get_full_name() or ticket.agente.username}.')
            else:
                messages.success(request, 'Ticket desasignado.')
        else:
            messages.error(request, 'Error al asignar el ticket.')

    return redirect('tickets:detalle_ticket', ticket_id=ticket.id)


@login_required
def estadisticas_tickets(request):
    """
    Estadísticas para empleados/superadmin.
    URL name: tickets:estadisticas_tickets
    Template: tickets/estadisticas_tickets.html
    """
    if not request.user.puede_gestionar_tickets():
        return HttpResponseForbidden("No tienes permisos para ver las estadísticas.")

    total_tickets = Ticket.objects.count()
    tickets_por_estado = Ticket.objects.values('estado').annotate(count=Count('estado'))
    tickets_por_prioridad = Ticket.objects.values('prioridad').annotate(count=Count('prioridad'))
    tickets_por_categoria = Ticket.objects.values('categoria__nombre').annotate(count=Count('categoria'))

    tickets_sin_asignar = Ticket.objects.filter(agente__isnull=True).count()

    # Si es superadmin, cargamos distribución por empleado
    tickets_por_empleado = None
    if request.user.es_superadmin():
        from accounts.models import Usuario
        empleados = getattr(Usuario.objects, 'empleados', None)
        empleados_qs = empleados() if callable(empleados) else Usuario.objects.filter(rol__in=['soporte', 'soporte_tecnico', 'empleado'])
        tickets_por_empleado = [
            {'empleado': e, 'count': Ticket.objects.filter(agente=e).count()}
            for e in empleados_qs
        ]

    context = {
        'total_tickets': total_tickets,
        'tickets_por_estado': tickets_por_estado,
        'tickets_por_prioridad': tickets_por_prioridad,
        'tickets_por_categoria': tickets_por_categoria,
        'tickets_sin_asignar': tickets_sin_asignar,
        'tickets_por_empleado': tickets_por_empleado,
    }
    return render(request, 'tickets/estadisticas_tickets.html', context)



@login_required
def tickets_sin_asignar(request):
    """
    Lista todos los tickets sin asignar (agente y técnico vacíos).
    Solo accesible para empleados, soporte, técnicos y superadmin.
    URL name: tickets:tickets_sin_asignar
    Template: tickets/tickets_sin_asignar.html
    """
    if not request.user.puede_gestionar_tickets():
        return HttpResponseForbidden("No tienes permisos para ver tickets sin asignar.")

    # Tickets sin agente ni técnico asignado
    tickets = Ticket.objects.filter(
        agente__isnull=True,
        tecnico__isnull=True,
        estado='abierto'
    ).select_related('cliente', 'categoria').order_by('-created_at')

    # Filtros opcionales
    prioridad_filtro = request.GET.get('prioridad', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()

    if prioridad_filtro:
        tickets = tickets.filter(prioridad=prioridad_filtro)

    if categoria_filtro:
        tickets = tickets.filter(categoria_id=categoria_filtro)

    # Paginación
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'prioridad_filtro': prioridad_filtro,
        'categoria_filtro': categoria_filtro,
        'prioridades': Ticket.PRIORIDADES,
        'categorias': Categoria.objects.activas() if hasattr(Categoria.objects, "activas") else Categoria.objects.all(),
    }
    return render(request, 'tickets/tickets_sin_asignar.html', context)


@login_required
def tomar_ticket(request, ticket_id):
    """
    Permite que un empleado/soporte/técnico se autoasigne un ticket.
    URL name: tickets:tomar_ticket
    """
    if not request.user.puede_gestionar_tickets():
        return HttpResponseForbidden("No tienes permisos para tomar tickets.")

    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Validar que el ticket esté sin asignar
    if ticket.agente or ticket.tecnico:
        messages.warning(request, 'Este ticket ya está asignado.')
        return redirect('tickets:detalle_ticket', ticket_id=ticket.id)

    # Validar que el usuario pueda recibir más tickets
    if not request.user.puede_recibir_mas_tickets():
        messages.error(request, f'Has alcanzado tu límite de {request.user.max_tickets_simultaneos} tickets simultáneos.')
        return redirect('tickets:tickets_sin_asignar')

    # Autoasignación según el rol
    if request.user.es_soporte() or request.user.es_empleado() or request.user.es_superadmin():
        ticket.agente = request.user
        ticket.fecha_asignacion = timezone.now()
        ticket.estado = 'en_revision'
        ticket.save()

        # Crear comentario interno
        Comentario.objects.create(
            ticket=ticket,
            autor=request.user,
            texto=f'{request.user.get_full_name() or request.user.username} tomó este ticket.',
            visibilidad='privada'
        )

        messages.success(request, f'Ticket #{str(ticket.id)[:8]} asignado a ti correctamente.')

    elif request.user.es_soporte_tecnico():
        ticket.tecnico = request.user
        ticket.estado = 'en_reparacion'
        ticket.save()

        Comentario.objects.create(
            ticket=ticket,
            autor=request.user,
            texto=f'Técnico {request.user.get_full_name() or request.user.username} tomó este ticket.',
            visibilidad='privada'
        )

        messages.success(request, f'Ticket #{str(ticket.id)[:8]} asignado a ti como técnico.')

    return redirect('tickets:detalle_ticket', ticket_id=ticket.id)