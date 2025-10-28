"""
Comando de gestión para corregir formato de UUIDs
Ubicación: attachments/management/commands/corregir_uuids.py

Uso:
    python manage.py corregir_uuids
    python manage.py corregir_uuids --dry-run
"""

import uuid
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Corrige el formato de UUIDs (sin guiones -> con guiones)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se corregiría sin hacer cambios',
        )

    def formatear_uuid_sin_guiones(self, uuid_str):
        """
        Convierte UUID sin guiones al formato estándar
        e445e6cef7274fac89ae3b36e0e85b12 -> e445e6ce-f727-4fac-89ae-3b36e0e85b12
        """
        if len(uuid_str) == 32:
            return f"{uuid_str[0:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:32]}"
        return uuid_str

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY-RUN: No se harán cambios\n'))
        
        self.stdout.write('Iniciando corrección de UUIDs...\n')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, objeto_id, tipo_objeto, nombre_original 
                FROM attachments_adjunto
            """)
            rows = cursor.fetchall()
            
            self.stdout.write(f'Total de registros: {len(rows)}\n')
            
            actualizados = 0
            ya_correctos = 0
            errores = 0
            
            for row in rows:
                adjunto_id, objeto_id, tipo_objeto, nombre_original = row
                
                try:
                    # Verificar si ya tiene formato correcto
                    uuid.UUID(objeto_id)
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Ya OK: {nombre_original[:50]}')
                    )
                    ya_correctos += 1
                    
                except (ValueError, AttributeError):
                    # Intentar corregir
                    try:
                        if len(objeto_id) == 32:
                            nuevo_objeto_id = self.formatear_uuid_sin_guiones(objeto_id)
                            
                            # Validar el nuevo formato
                            uuid.UUID(nuevo_objeto_id)
                            
                            self.stdout.write(
                                self.style.WARNING(f'⟳ Corrigiendo: {nombre_original[:50]}')
                            )
                            self.stdout.write(f'  {objeto_id} → {nuevo_objeto_id}')
                            
                            if not dry_run:
                                cursor.execute(
                                    "UPDATE attachments_adjunto SET objeto_id = ? WHERE id = ?",
                                    [nuevo_objeto_id, adjunto_id]
                                )
                            
                            actualizados += 1
                            
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'✗ No se puede corregir: {nombre_original[:50]} '
                                    f'(longitud: {len(objeto_id)})'
                                )
                            )
                            errores += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error: {nombre_original[:50]} - {str(e)}'
                            )
                        )
                        errores += 1
            
            # Resumen
            self.stdout.write('\n' + '='*60)
            self.stdout.write('RESUMEN:')
            self.stdout.write(f'  Total: {len(rows)}')
            self.stdout.write(
                self.style.SUCCESS(f'  Ya correctos: {ya_correctos}')
            )
            
            if actualizados > 0:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'  Se corregirían: {actualizados}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Corregidos: {actualizados}')
                    )
            
            if errores > 0:
                self.stdout.write(
                    self.style.ERROR(f'  Errores: {errores}')
                )
            
            self.stdout.write('='*60 + '\n')
            
            if actualizados > 0 and not dry_run:
                self.stdout.write(
                    self.style.SUCCESS('✓ Corrección completada exitosamente')
                )
            elif dry_run and actualizados > 0:
                self.stdout.write(
                    self.style.WARNING('Ejecuta sin --dry-run para aplicar los cambios')
                )
            elif errores > 0:
                self.stdout.write(
                    self.style.ERROR('⚠ Se encontraron errores')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ Todos los UUIDs están correctos')
                )