from django.urls import path
from . import views

app_name = 'attachments'

urlpatterns = [
    # Gestión de adjuntos
    path('subir/<uuid:ticket_id>/', views.subir_adjunto, name='subir_adjunto'),
    path('descargar/<uuid:adjunto_id>/', views.descargar_adjunto, name='descargar_adjunto'),
    path('eliminar/<uuid:adjunto_id>/', views.eliminar_adjunto, name='eliminar_adjunto'),

    # Listado (solo superadmin)
    path('', views.listar_adjuntos, name='listar_adjuntos'),
]