from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import Usuario
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, LoginForm
from tickets.models import Ticket
from tickets.services import MetricasService, BalanceadorCarga


def registro_usuario(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ya puede iniciar sesión.')
            return redirect('accounts:iniciar_sesion')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'accounts/registro.html', {'form': form})


def iniciar_sesion(request):
    """Vista para iniciar sesión"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Intentar autenticar con username o email
            user = authenticate(request, username=username, password=password)
            if not user:
                # Intentar con email
                try:
                    usuario_obj = Usuario.objects.get(email=username)
                    user = authenticate(request, username=usuario_obj.username, password=password)
                except Usuario.DoesNotExist:
                    pass

            if user and user.is_active and user.estado == 'activo':
                login(request, user)
                messages.success(request, f'Bienvenido, {user.get_full_name()}')

                # Redirigir según el rol del usuario
                return redirect(user.get_dashboard_url())
            else:
                messages.error(request, 'Credenciales inválidas o cuenta inactiva.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def cerrar_sesion(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('accounts:iniciar_sesion')


@login_required
def dashboard_cliente(request):
    """Dashboard para clientes"""
    if not request.user.es_cliente():
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('accounts:iniciar_sesion')

    # Obtener estadísticas del cliente
    tickets_cliente = Ticket.objects.del_cliente(request.user)

    context = {
        'total_tickets': tickets_cliente.count(),
        'tickets_abiertos': tickets_cliente.filter(estado__in=['abierto', 'en_revision', 'aceptado', 'en_reparacion']).count(),
        'tickets_resueltos': tickets_cliente.filter(estado='resuelto').count(),
        'tickets_cerrados': tickets_cliente.filter(estado='cerrado').count(),
        'tickets_recientes': tickets_cliente.order_by('-created_at')[:5],
        'tickets_vencidos': sum(1 for ticket in tickets_cliente if ticket.esta_vencido()),
    }

    return render(request, 'accounts/dashboard_cliente.html', context)


@login_required
def dashboard_soporte(request):
    """Dashboard para agentes de soporte"""
    if not request.user.es_soporte():
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('accounts:iniciar_sesion')

    # Obtener estadísticas del agente
    tickets_asignados = Ticket.objects.asignados_a(request.user)
    tickets_sin_asignar = Ticket.objects.sin_asignar()

    context = {
        'tickets_asignados': tickets_asignados.count(),
        'tickets_activos': tickets_asignados.exclude(estado__in=['cerrado', 'rechazado']).count(),
        'tickets_sin_asignar': tickets_sin_asignar.count(),
        'tickets_vencidos': sum(1 for ticket in tickets_asignados if ticket.esta_vencido()),
        'tickets_recientes': tickets_asignados.order_by('-created_at')[:10],
        'tickets_urgentes': tickets_asignados.filter(prioridad__in=['alta', 'critica']).order_by('-created_at')[:5],
        'estadisticas_carga': BalanceadorCarga.obtener_estadisticas_carga(),
    }

    return render(request, 'accounts/dashboard_soporte.html', context)


@login_required
def dashboard_tecnico(request):
    """Dashboard para técnicos"""
    if not request.user.es_soporte_tecnico():
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('accounts:iniciar_sesion')

    # Obtener estadísticas del técnico
    tickets_tecnicos = Ticket.objects.filter(tecnico=request.user)

    context = {
        'tickets_en_reparacion': tickets_tecnicos.filter(estado='en_reparacion').count(),
        'tickets_completados': tickets_tecnicos.filter(estado='resuelto').count(),
        'tickets_recientes': tickets_tecnicos.order_by('-updated_at')[:10],
        'tickets_urgentes': tickets_tecnicos.filter(
            prioridad__in=['alta', 'critica'],
            estado='en_reparacion'
        ).order_by('-created_at')[:5],
    }

    return render(request, 'accounts/dashboard_tecnico.html', context)


@login_required
def dashboard_empleado(request):
    """Dashboard para empleados (legacy - compatibilidad)"""
    if not request.user.es_empleado():
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('accounts:iniciar_sesion')

    # Redirigir a dashboard de soporte si es empleado legacy
    messages.info(request, 'Su rol ha sido actualizado. Será redirigido al dashboard de soporte.')
    return redirect('accounts:dashboard_soporte')

    return render(request, 'accounts/dashboard_empleado.html', context)


@login_required
def dashboard_superadmin(request):
    """Dashboard para superadministradores"""
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")

    from tickets.models import Ticket

    context = {
        'usuario': request.user,
        'total_usuarios': Usuario.objects.count(),
        'total_clientes': Usuario.objects.clientes().count(),
        'total_empleados': Usuario.objects.empleados().count(),
        'total_tickets': Ticket.objects.count(),
        'tickets_abiertos': Ticket.objects.abiertos().count(),
        'tickets_resueltos': Ticket.objects.resueltos().count(),
        'tickets_recientes': Ticket.objects.all().order_by('-created_at')[:5],
    }

    return render(request, 'accounts/dashboard_superadmin.html', context)


@login_required
def perfil_usuario(request):
    """Vista para ver el perfil del usuario"""
    return render(request, 'accounts/perfil.html', {'user': request.user})


@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('accounts:perfil_usuario')
    else:
        form = PerfilUsuarioForm(instance=request.user)

    return render(request, 'accounts/editar_perfil.html', {'form': form})


@login_required
def listar_usuarios(request):
    """Vista para listar usuarios (solo superadmin)"""
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")

    busqueda = request.GET.get('busqueda', '')
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')

    usuarios = Usuario.objects.all()

    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)

    if estado_filtro:
        usuarios = usuarios.filter(estado=estado_filtro)

    usuarios = usuarios.order_by('-created_at')

    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'roles': Usuario.ROLES,
        'estados': Usuario.ESTADOS,
    }

    return render(request, 'accounts/listar_usuarios.html', context)


@login_required
def cambiar_estado_usuario(request, usuario_id):
    """Vista para cambiar el estado de un usuario (solo superadmin)"""
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Usuario.ESTADOS):
            usuario.estado = nuevo_estado
            usuario.save()
            messages.success(request, f'Estado del usuario {usuario.username} cambiado a {nuevo_estado}.')
        else:
            messages.error(request, 'Estado no válido.')

    return redirect('accounts:listar_usuarios')


@login_required
def asignar_rol_usuario(request, usuario_id):
    """Vista para cambiar el rol de un usuario (solo superadmin)"""
    if not request.user.es_superadmin():
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('accounts:listar_usuarios')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        roles_validos = [choice[0] for choice in Usuario.ROLES]

        if nuevo_rol in roles_validos:
            rol_anterior = usuario.get_rol_display()
            usuario.rol = nuevo_rol
            usuario.save()

            messages.success(
                request,
                f'Rol del usuario {usuario.get_full_name()} cambiado de {rol_anterior} a {usuario.get_rol_display()}.'
            )
        else:
            messages.error(request, 'Rol inválido.')

    return redirect('accounts:listar_usuarios')


@login_required
def estadisticas_usuarios(request):
    """Vista para mostrar estadísticas de usuarios (solo superadmin)"""
    if not request.user.es_superadmin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:iniciar_sesion')

    # Estadísticas por rol
    stats_por_rol = Usuario.objects.values('rol').annotate(
        total=Count('id'),
        activos=Count('id', filter=Q(estado='activo'))
    ).order_by('rol')

    # Usuarios más activos (por tickets creados/asignados)
    usuarios_activos = Usuario.objects.annotate(
        tickets_creados=Count('tickets_creados'),
        tickets_asignados=Count('tickets_asignados')
    ).order_by('-tickets_creados', '-tickets_asignados')[:10]

    context = {
        'stats_por_rol': stats_por_rol,
        'usuarios_activos': usuarios_activos,
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos_count': Usuario.objects.activos().count(),
        'nuevos_usuarios_mes': Usuario.objects.filter(
            date_joined__gte=timezone.now().replace(day=1)
        ).count(),
    }

    return render(request, 'accounts/estadisticas_usuarios.html', context)

@login_required
def crear_usuario(request):
    """Vista para crear usuarios administrativos (solo superadmin)"""
    if not request.user.es_superadmin():
        messages.error(request, 'No tienes permisos para crear usuarios.')
        return redirect('accounts:listar_usuarios')

    from .forms import AdminUsuarioForm
    titulo = "Crear usuario administrativo"
    mostrar_passwords = True

    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = True
            usuario.save()
            messages.success(request, f'Usuario "{usuario.username}" creado correctamente.')
            return redirect('accounts:listar_usuarios')
        else:
            messages.error(request, "Corrige los errores para continuar.")
    else:
        form = AdminUsuarioForm()

    return render(request, 'accounts/usuario_form.html', {
        'form': form,
        'titulo_form': titulo,
        'mostrar_passwords': mostrar_passwords
    })


@login_required
def detalle_usuario(request, usuario_id):
    """Vista para ver el detalle de un usuario (solo superadmin)"""
    if not request.user.es_superadmin():
        messages.error(request, 'No tienes permisos para ver detalles de usuarios.')
        return redirect('accounts:listar_usuarios')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    context = {
        'usuario': usuario,
    }

    return render(request, 'accounts/detalle_usuario.html', context)



@login_required
def editar_usuario(request, usuario_id):
    """Vista para editar un usuario (solo superadmin)"""
    if not request.user.es_superadmin():
        messages.error(request, 'No tienes permisos para editar usuarios.')
        return redirect('accounts:listar_usuarios')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado correctamente.')
            return redirect('accounts:listar_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PerfilUsuarioForm(instance=usuario)

    return render(request, 'accounts/editar_usuario.html', {'form': form, 'usuario': usuario})



