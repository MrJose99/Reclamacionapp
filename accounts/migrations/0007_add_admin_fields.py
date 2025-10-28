# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_usuario_estado_alter_usuario_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='es_vip',
            field=models.BooleanField(default=False, help_text='Marca al cliente como VIP para atención prioritaria', verbose_name='Cliente VIP'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='tiene_restricciones',
            field=models.BooleanField(default=False, help_text='Marca al cliente con restricciones por fraude o abuso', verbose_name='Tiene restricciones'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='notas_internas',
            field=models.TextField(blank=True, help_text='Notas visibles solo para empleados y administradores', null=True, verbose_name='Notas internas'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='motivo_restriccion',
            field=models.TextField(blank=True, help_text='Razón por la cual el cliente tiene restricciones', null=True, verbose_name='Motivo de restricción'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='fecha_restriccion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de restricción'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='ultima_actividad',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Última actividad'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='motivo_desactivacion',
            field=models.TextField(blank=True, null=True, verbose_name='Motivo de desactivación'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='fecha_desactivacion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de desactivación'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='desactivado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios_desactivados', to=settings.AUTH_USER_MODEL, verbose_name='Desactivado por'),
        ),
    ]
