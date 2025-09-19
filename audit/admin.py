from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'tipo', 'actor', 'created_at')
    list_filter = ('tipo', 'created_at')
    search_fields = ('ticket_id', 'descripcion', 'actor__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('id', 'ticket_id', 'tipo', 'descripcion')
        }),
        ('Actor', {
            'fields': ('actor',)
        }),
        ('Datos Adicionales', {
            'fields': ('datos_json',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )