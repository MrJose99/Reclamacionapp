from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.listar_tickets, name="listar_tickets"),  
    path("crear/", views.crear_ticket, name="crear_ticket"),  
    path("estadisticas/", views.estadisticas_tickets, name="estadisticas_tickets"),  
      
    # Lista de tickets sin asignar  
    path("sin-asignar/", views.tickets_sin_asignar, name="tickets_sin_asignar"),  
  
    path("<str:ticket_id>/", views.detalle_ticket, name="detalle_ticket"),  
    path("<str:ticket_id>/comentarios/agregar/", views.agregar_comentario, name="agregar_comentario"),  
      
    # 👇 CORREGIDO: cambiar_estado en lugar de cambiar_estado_ticket  
    path("<str:ticket_id>/estado/cambiar/", views.cambiar_estado, name="cambiar_estado"),  
      
    # 👇 NUEVAS RUTAS para las funcionalidades adicionales  
    path("<str:ticket_id>/adjuntos/agregar/", views.agregar_adjuntos, name="agregar_adjuntos"),  
    path("<str:ticket_id>/personal/asignar/", views.asignar_personal, name="asignar_personal"),  
    path("<str:ticket_id>/resolver/", views.resolver_ticket, name="resolver"),  
      
    # Rutas originales  
    path("<str:ticket_id>/asignar/", views.asignar_ticket, name="asignar_ticket"),  
    path("<str:ticket_id>/tomar/", views.tomar_ticket, name="tomar_ticket"),
    path("editar/<uuid:id>/", views.editar_ticket, name="editar"),
    
    ]