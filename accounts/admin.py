from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del admin para el modelo Usuario
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'estado', 'is_active')
    list_filter = ('rol', 'estado', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('telefono', 'fecha_nacimiento', 'direccion', 'rol', 'estado')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'telefono', 'fecha_nacimiento', 'direccion', 'rol', 'estado')
        }),
    )