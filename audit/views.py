from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Evento
from tickets.models import Ticket


@login_required
def listar_eventos(request):
    """Vista para listar eventos de auditoría (solo superadmin)"""
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para ver los eventos de auditoría.")

    eventos = Evento.objects.all().order_by('-created_at')

    # Filtros
    tipo_filtro = request.GET.get('tipo', '')
    actor_filtro = request.GET.get('actor', '')
    ticket_filtro = request.GET.get('ticket', '')

    if tipo_filtro:
        eventos = eventos.filter(tipo=tipo_filtro)

    if actor_filtro:
        eventos = eventos.filter(actor__username__icontains=actor_filtro)

    if ticket_filtro:
        eventos = eventos.filter(ticket_id=ticket_filtro)

    # Paginación
    paginator = Paginator(eventos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'tipo_filtro': tipo_filtro,
        'actor_filtro': actor_filtro,
        'ticket_filtro': ticket_filtro,
        'tipos_evento': dict(Evento.TIPOS_EVENTO),
    }

    return render(request, 'audit/listar_eventos.html', context)


@login_required
def eventos_ticket(request, ticket_id):
    """Vista para ver eventos de un ticket específico"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verificar permisos
    if request.user.es_cliente() and ticket.cliente != request.user:
        return HttpResponseForbidden("No tienes permisos para ver los eventos de este ticket.")

    eventos = Evento.objects.filter(ticket_id=str(ticket.id)).order_by('-created_at')

    context = {
        'ticket': ticket,
        'eventos': eventos,
    }

    return render(request, 'audit/eventos_ticket.html', context)