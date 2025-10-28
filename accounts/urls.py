from django.urls import path
from . import views

app_name = 'accounts'


urlpatterns = [
    # Autenticación
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    # Dashboards por rol
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/soporte/', views.dashboard_soporte, name='dashboard_soporte'),
    path('dashboard/tecnico/', views.dashboard_tecnico, name='dashboard_tecnico'),
    path('dashboard/empleado/', views.dashboard_empleado, name='dashboard_empleado'),  # Legacy
    path('dashboard/superadmin/', views.dashboard_superadmin, name='dashboard_superadmin'),

    # Gestión de perfil
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Gestión de usuarios (solo superadmin)
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/<uuid:usuario_id>/cambiar-estado/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('usuarios/<uuid:usuario_id>/asignar-rol/', views.asignar_rol_usuario, name='asignar_rol_usuario'),
    path('usuarios/estadisticas/', views.estadisticas_usuarios, name='estadisticas_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<uuid:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/<uuid:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
]