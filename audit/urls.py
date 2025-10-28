from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.listar_eventos, name='listar_eventos'),
    path('ticket/<uuid:ticket_id>/', views.eventos_ticket, name='eventos_ticket'),
]