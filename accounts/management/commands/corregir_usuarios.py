from django.core.management.base import BaseCommand
from accounts.models import Usuario


class Command(BaseCommand):
    help = 'Corrige usuarios con problemas de activación (is_active o estado)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué usuarios se corregirían sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar usuarios con problemas
        usuarios_problema = Usuario.objects.filter(
            is_active=False
        ) | Usuario.objects.filter(
            estado='inactivo'
        )
        
        if not usuarios_problema.exists():
            self.stdout.write(
                self.style.SUCCESS('✓ No se encontraron usuarios con problemas de activación')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Se encontraron {usuarios_problema.count()} usuario(s) con problemas:')
        )
        
        for usuario in usuarios_problema:
            self.stdout.write(
                f'  - {usuario.username} (email: {usuario.email})'
            )
            self.stdout.write(
                f'    is_active: {usuario.is_active}, estado: {usuario.estado}'
            )
            
            if not dry_run:
                # Corregir el usuario
                usuario.is_active = True
                usuario.estado = 'activo'
                usuario.save()
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Usuario {usuario.username} corregido')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠ Modo dry-run: No se realizaron cambios')
            )
            self.stdout.write(
                'Ejecuta el comando sin --dry-run para aplicar los cambios'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Se corrigieron {usuarios_problema.count()} usuario(s)')
            )
