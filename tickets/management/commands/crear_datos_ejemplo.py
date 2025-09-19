from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.models import Categoria, Ticket
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de tickets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuarios',
            type=int,
            default=5,
            help='Número de usuarios de ejemplo a crear'
        )
        parser.add_argument(
            '--tickets',
            type=int,
            default=10,
            help='Número de tickets de ejemplo a crear'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo...')
        
        # Crear categorías
        categorias = [
            {'nombre': 'Producto Defectuoso', 'descripcion': 'Problemas con la calidad del producto'},
            {'nombre': 'Servicio al Cliente', 'descripcion': 'Problemas con la atención recibida'},
            {'nombre': 'Facturación', 'descripcion': 'Errores en facturación o cobros'},
            {'nombre': 'Entrega', 'descripcion': 'Problemas con la entrega del producto'},
            {'nombre': 'Garantía', 'descripcion': 'Reclamaciones de garantía'},
        ]
        
        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
            if created:
                self.stdout.write(f'Categoría creada: {categoria.nombre}')
        
        # Crear usuarios de ejemplo
        usuarios_data = [
            {'username': 'cliente1', 'email': 'cliente1@example.com', 'rol': 'cliente', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'cliente2', 'email': 'cliente2@example.com', 'rol': 'cliente', 'first_name': 'María', 'last_name': 'García'},
            {'username': 'empleado1', 'email': 'empleado1@example.com', 'rol': 'empleado', 'first_name': 'Carlos', 'last_name': 'López'},
            {'username': 'empleado2', 'email': 'empleado2@example.com', 'rol': 'empleado', 'first_name': 'Ana', 'last_name': 'Martínez'},
        ]
        
        for user_data in usuarios_data[:options['usuarios']]:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'rol': user_data['rol'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Usuario creado: {user.username} ({user.rol})')
        
        # Crear tickets de ejemplo
        clientes = User.objects.filter(rol='cliente')
        empleados = User.objects.filter(rol='empleado')
        categorias_list = list(Categoria.objects.all())
        
        if clientes.exists() and categorias_list:
            tickets_data = [
                {
                    'numero_factura': 'FAC-2024-001',
                    'asunto': 'Producto llegó dañado',
                    'descripcion': 'El producto que pedí llegó con daños en el empaque y el contenido está roto.',
                    'prioridad': 'alta'
                },
                {
                    'numero_factura': 'FAC-2024-002',
                    'asunto': 'Error en facturación',
                    'descripcion': 'Me cobraron de más en mi última compra, necesito una corrección.',
                    'prioridad': 'media'
                },
                {
                    'numero_factura': 'FAC-2024-003',
                    'asunto': 'Producto no funciona',
                    'descripcion': 'El producto que compré no funciona correctamente desde el primer día.',
                    'prioridad': 'alta'
                },
            ]
            
            import random
            
            for i, ticket_data in enumerate(tickets_data[:options['tickets']]):
                if i < len(tickets_data):
                    data = tickets_data[i]
                else:
                    data = {
                        'numero_factura': f'FAC-2024-{str(i+1).zfill(3)}',
                        'asunto': f'Ticket de ejemplo {i+1}',
                        'descripcion': f'Descripción del ticket de ejemplo número {i+1}',
                        'prioridad': random.choice(['baja', 'media', 'alta'])
                    }
                
                ticket = Ticket.objects.create(
                    numero_factura=data['numero_factura'],
                    asunto=data['asunto'],
                    descripcion=data['descripcion'],
                    categoria=random.choice(categorias_list),
                    prioridad=data['prioridad'],
                    cliente=random.choice(clientes),
                    agente=random.choice(empleados) if empleados.exists() and random.choice([True, False]) else None,
                    estado=random.choice(['abierto', 'en_revision', 'resuelto'])
                )
                self.stdout.write(f'Ticket creado: {ticket.asunto}')
        
        self.stdout.write(
            self.style.SUCCESS('Datos de ejemplo creados exitosamente!')
        )