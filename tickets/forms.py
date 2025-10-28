from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Ticket, Comentario, Categoria

User = get_user_model()


class TicketForm(forms.ModelForm):
    """Formulario para crear y editar tickets"""
    
    fecha_compra = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=True,
        help_text='Fecha de compra del producto (requerida para validar garantía)'
    )

    class Meta:
        model = Ticket
        fields = [
            'numero_factura', 'numero_serie', 'fecha_compra', 'asunto',
            'descripcion', 'categoria', 'prioridad', 'tipo_reclamo'
        ]
        widgets = {
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: FAC-2024-001234'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie del producto (si aplica)'
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resumen breve del problema'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describa detalladamente el problema o solicitud'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'tipo_reclamo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Solo mostrar categorías activas
        self.fields['categoria'].queryset = Categoria.objects.activas()

        # Si es un cliente, limitar algunas opciones
        if user and user.es_cliente():
            # Los clientes no pueden establecer prioridad crítica
            self.fields['prioridad'].choices = [
                choice for choice in self.fields['prioridad'].choices
                if choice[0] != 'critica'
            ]

        # Agregar ayuda contextual
        self.fields['numero_serie'].help_text = 'Requerido para productos con garantía'
        self.fields['categoria'].help_text = 'Seleccione la categoría que mejor describa su solicitud'
        self.fields['prioridad'].help_text = 'La prioridad puede ser ajustada por el equipo de soporte'

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        numero_serie = cleaned_data.get('numero_serie')
        numero_factura = cleaned_data.get('numero_factura')

        # Validar campos requeridos según la categoría
        if categoria:
            if categoria.requiere_numero_serie and not numero_serie:
                self.add_error('numero_serie', 'Este campo es requerido para la categoría seleccionada')

            if categoria.requiere_factura and not numero_factura:
                self.add_error('numero_factura', 'Este campo es requerido para la categoría seleccionada')

        return cleaned_data


class ComentarioForm(forms.ModelForm):
    """Formulario para agregar comentarios a tickets"""

    class Meta:
        model = Comentario
        fields = ['texto', 'visibilidad', 'resuelve_ticket']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba su comentario aquí...'
            }),
            'visibilidad': forms.Select(attrs={'class': 'form-select'}),
            'resuelve_ticket': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)

        # Los clientes solo pueden hacer comentarios públicos
        if user and user.es_cliente():
            self.fields['visibilidad'].widget = forms.HiddenInput()
            self.fields['visibilidad'].initial = 'publico'

            # Los clientes no pueden marcar como resuelto directamente
            self.fields['resuelve_ticket'].widget = forms.HiddenInput()
            self.fields['resuelve_ticket'].initial = False

        # Solo personal de soporte puede marcar como resuelto
        if user and not user.puede_gestionar_tickets():
            self.fields['resuelve_ticket'].widget = forms.HiddenInput()
            self.fields['resuelve_ticket'].initial = False

        # Agregar ayuda contextual
        if user and user.puede_gestionar_tickets():
            self.fields['visibilidad'].help_text = 'Los comentarios privados solo son visibles para el equipo de soporte'
            self.fields['resuelve_ticket'].help_text = 'Marque si este comentario resuelve el ticket'


class AsignarTicketForm(forms.ModelForm):
    """Formulario para asignar tickets a agentes"""

    class Meta:
        model = Ticket
        fields = ['agente']
        widgets = {
            'agente': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar agentes de soporte activos
        self.fields['agente'].queryset = User.objects.soporte().order_by('first_name', 'last_name')
        self.fields['agente'].empty_label = "Seleccionar agente..."


class DerivarTecnicoForm(forms.ModelForm):
    """Formulario para derivar tickets a técnicos"""

    class Meta:
        model = Ticket
        fields = ['tecnico']
        widgets = {
            'tecnico': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar técnicos activos
        self.fields['tecnico'].queryset = User.objects.soporte_tecnico().order_by('first_name', 'last_name')
        self.fields['tecnico'].empty_label = "Seleccionar técnico..."


class CambiarEstadoForm(forms.ModelForm):
    """Formulario para cambiar el estado de un ticket"""

    motivo_rechazo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explique el motivo del rechazo...'
        }),
        required=False,
        help_text='Requerido solo cuando se rechaza un ticket'
    )

    class Meta:
        model = Ticket
        fields = ['estado', 'motivo_rechazo']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)

        # Filtrar estados disponibles según el rol del usuario y estado actual
        if user and ticket:
            estados_disponibles = []
            estado_actual = ticket.estado

            if user.es_soporte():
                transiciones = {
                    'abierto': [('en_revision', 'En Revisión'), ('rechazado', 'Rechazado')],
                    'en_revision': [('aceptado', 'Aceptado'), ('rechazado', 'Rechazado'), ('en_espera_cliente', 'En Espera del Cliente')],
                    'aceptado': [('en_reparacion', 'En Reparación'), ('resuelto', 'Resuelto'), ('en_espera_cliente', 'En Espera del Cliente')],
                    'en_espera_cliente': [('en_revision', 'En Revisión'), ('aceptado', 'Aceptado')],
                    'resuelto': [('cerrado', 'Cerrado')],
                }
                estados_disponibles = transiciones.get(estado_actual, [])

            elif user.es_soporte_tecnico():
                transiciones = {
                    'en_reparacion': [('resuelto', 'Resuelto'), ('en_espera_cliente', 'En Espera del Cliente')],
                    'en_espera_cliente': [('en_reparacion', 'En Reparación')],
                }
                estados_disponibles = transiciones.get(estado_actual, [])

            elif user.es_superadmin():
                # Los superadmins pueden cambiar a cualquier estado
                estados_disponibles = Ticket.ESTADOS

            self.fields['estado'].choices = [('', 'Seleccionar nuevo estado...')] + estados_disponibles

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        motivo_rechazo = cleaned_data.get('motivo_rechazo')

        # Validar que se proporcione motivo cuando se rechaza
        if estado == 'rechazado' and not motivo_rechazo:
            self.add_error('motivo_rechazo', 'Debe proporcionar un motivo para rechazar el ticket')

        return cleaned_data


class FiltroTicketsForm(forms.Form):
    """Formulario para filtrar tickets"""

    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por asunto, número de factura o serie...'
        })
    )

    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Ticket.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    prioridad = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + Ticket.PRIORIDADES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.activas(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tipo_reclamo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Ticket.TIPOS_RECLAMO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    solo_vencidos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo tickets vencidos'
    )

    solo_sin_asignar = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo tickets sin asignar'
    )


class MultipleFileInput(forms.ClearableFileInput):
    """Widget personalizado para múltiples archivos"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Campo personalizado para múltiples archivos"""
    def __init__(self, *args, **kwargs):
        # If a widget was not provided, use our MultipleFileInput
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Si se reciben múltiples archivos (lista/tupla), aplicar la limpieza
        del FileField a cada uno y devolver la lista. Si viene un solo
        archivo, devolver el resultado habitual.
        """
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class AdjuntoMultipleForm(forms.Form):
    """Formulario para subir múltiples archivos"""

    archivos = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.mp4,.avi,.mov,.wmv,.flv,.webm,.mkv,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar,.7z'
        }),
        help_text='Puede seleccionar múltiples archivos. Tamaño máximo: 25MB por archivo.',
        required=False
    )

    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Descripción opcional de los archivos...'
        }),
        required=False
    )

    es_publico = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Los archivos públicos son visibles para el cliente'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Los clientes no pueden subir archivos privados
        if user and user.es_cliente():
            self.fields['es_publico'].widget = forms.HiddenInput()
            self.fields['es_publico'].initial = True


class ValidacionGarantiaForm(forms.Form):
    """Formulario para validar garantía manualmente"""

    fecha_compra = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Fecha de compra del producto'
    )

    numero_factura = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de factura'
        })
    )

    numero_serie = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de serie (opcional)'
        })
    )

    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.activas(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Categoría del producto para determinar días de garantía'
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_compra = cleaned_data.get('fecha_compra')
        categoria = cleaned_data.get('categoria')

        if fecha_compra and categoria:
            from django.utils import timezone
            from datetime import timedelta

            dias_transcurridos = (timezone.now().date() - fecha_compra).days

            if dias_transcurridos < 0:
                self.add_error('fecha_compra', 'La fecha de compra no puede ser futura')

            # Advertir si la garantía está próxima a vencer
            dias_restantes = categoria.dias_garantia_defecto - dias_transcurridos
            if 0 < dias_restantes <= 30:
                self.add_error(None, f'Advertencia: La garantía vence en {dias_restantes} días')

        return cleaned_data


class ReporteForm(forms.Form):
    """Formulario para generar reportes"""

    TIPOS_REPORTE = [
        ('general', 'Reporte General'),
        ('por_agente', 'Reporte por Agente'),
        ('por_categoria', 'Reporte por Categoría'),
        ('tiempos_respuesta', 'Tiempos de Respuesta'),
        ('satisfaccion', 'Satisfacción del Cliente'),
    ]

    tipo_reporte = forms.ChoiceField(
        choices=TIPOS_REPORTE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    formato = forms.ChoiceField(
        choices=[
            ('html', 'Ver en pantalla'),
            ('pdf', 'Descargar PDF'),
            ('excel', 'Descargar Excel'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    incluir_cerrados = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir tickets cerrados'
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                self.add_error('fecha_fin', 'La fecha de fin debe ser posterior a la fecha de inicio')

            # Limitar el rango a un año máximo
            from datetime import timedelta
            if (fecha_fin - fecha_inicio) > timedelta(days=365):
                self.add_error(None, 'El rango de fechas no puede ser mayor a un año')

        return cleaned_data