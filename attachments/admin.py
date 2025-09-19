from django.contrib import admin
from .models import Adjunto


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre_original', 'tipo_archivo', 'tipo_objeto', 'tamaño_bytes', 'created_at')
    list_filter = ('tipo_archivo', 'tipo_objeto', 'created_at')
    search_fields = ('nombre_original', 'objeto_id')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'tamaño_bytes', 'checksum', 'created_at')
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('id', 'archivo', 'nombre_original', 'tipo_archivo', 'tipo_mime')
        }),
        ('Relación', {
            'fields': ('objeto_id', 'tipo_objeto')
        }),
        ('Metadatos', {
            'fields': ('tamaño_bytes', 'checksum', 'created_at'),
            'classes': ('collapse',)
        }),
    )