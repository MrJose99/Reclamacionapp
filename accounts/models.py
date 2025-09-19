from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioManager(models.Manager):
    """
    Manager personalizado para el modelo Usuario
    """
    def clientes(self):
        return self.filter(rol='cliente')
    
    def empleados(self):
        return self.filter(rol='empleado')
    
    def administradores(self):
        return self.filter(rol='admin')
    
    def activos(self):
        return self.filter(estado='activo')


class Usuario(AbstractUser):
    """
    Modelo de usuario extendido con roles específicos del sistema
    """
    ROLES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('admin', 'Administrador'),
    ]
    
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    
    # Campos adicionales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def es_cliente(self):
        return self.rol == 'cliente'
    
    def es_empleado(self):
        return self.rol == 'empleado'
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def puede_gestionar_tickets(self):
        return self.rol in ['empleado', 'admin']