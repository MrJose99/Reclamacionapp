from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # URLs para gestión de tickets
    # path('', views.lista_tickets, name='lista'),
    # path('crear/', views.crear_ticket, name='crear'),
    # path('<uuid:ticket_id>/', views.detalle_ticket, name='detalle'),
    # path('<uuid:ticket_id>/comentar/', views.agregar_comentario, name='comentar'),
    # path('<uuid:ticket_id>/asignar/', views.asignar_ticket, name='asignar'),
    # path('<uuid:ticket_id>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
]