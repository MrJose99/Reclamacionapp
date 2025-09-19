from django.contrib import admin
from .models import Categoria, Ticket, Comentario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'created_at')
    list_filter = ('activa', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'asunto', 'numero_factura', 'cliente', 'agente', 'estado', 'prioridad', 'created_at')
    list_filter = ('estado', 'prioridad', 'categoria', 'created_at')
    search_fields = ('asunto', 'numero_factura', 'cliente__username', 'cliente__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'closed_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'numero_factura', 'asunto', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'prioridad', 'estado')
        }),
        ('Asignación', {
            'fields': ('cliente', 'agente')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'autor', 'visibilidad', 'created_at')
    list_filter = ('visibilidad', 'created_at')
    search_fields = ('ticket__asunto', 'autor__username', 'texto')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')