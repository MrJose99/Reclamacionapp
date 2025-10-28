from django.core.management.base import BaseCommand
from tickets.models import Categoria
import uuid

class Command(BaseCommand):
    help = 'Crea categorías por defecto si no existen'

    def handle(self, *args, **kwargs):
        categorias_por_defecto = [
            {
                'nombre': 'Hardware',
                'descripcion': 'Problemas relacionados con hardware',
                'dias_garantia_defecto': 365,
                'requiere_factura': True,
                'requiere_numero_serie': True,
            },
            {
                'nombre': 'Software',
                'descripcion': 'Problemas relacionados con software',
                'dias_garantia_defecto': 180,
                'requiere_factura': False,
                'requiere_numero_serie': False,
            },
            {
                'nombre': 'Redes',
                'descripcion': 'Problemas relacionados con redes y conectividad',
                'dias_garantia_defecto': 90,
                'requiere_factura': True,
                'requiere_numero_serie': False,
            },
        ]

        for cat_data in categorias_por_defecto:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={
                    'descripcion': cat_data['descripcion'],
                    'dias_garantia_defecto': cat_data['dias_garantia_defecto'],
                    'requiere_factura': cat_data['requiere_factura'],
                    'requiere_numero_serie': cat_data['requiere_numero_serie'],
                    'activa': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Categoría '{categoria.nombre}' creada exitosamente."))
            else:
                self.stdout.write(f"Categoría '{categoria.nombre}' ya existe.")