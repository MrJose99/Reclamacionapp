from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # URLs para auditoría
    # path('eventos/<uuid:ticket_id>/', views.eventos_ticket, name='eventos_ticket'),
    # path('bitacora/', views.bitacora_general, name='bitacora'),
]