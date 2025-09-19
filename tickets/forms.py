from django import forms
from .models import Ticket, Comentario, Categoria


class CrearTicketForm(forms.ModelForm):
    """
    Formulario para crear nuevos tickets
    """
    class Meta:
        model = Ticket
        fields = ('numero_factura', 'asunto', 'descripcion', 'categoria', 'prioridad')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'numero_factura': forms.TextInput(attrs={'placeholder': 'Ej: FAC-2024-001'}),
            'asunto': forms.TextInput(attrs={'placeholder': 'Resumen breve del problema'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True)
        self.fields['categoria'].empty_label = "Seleccionar categoría"


class ComentarioForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a tickets
    """
    class Meta:
        model = Comentario
        fields = ('texto', 'visibilidad')
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escriba su comentario aquí...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Solo empleados y admins pueden crear comentarios privados
        if user and user.rol not in ['empleado', 'admin']:
            self.fields['visibilidad'].widget = forms.HiddenInput()
            self.fields['visibilidad'].initial = 'publica'


class FiltroTicketsForm(forms.Form):
    """
    Formulario para filtrar tickets
    """
    ESTADOS_CHOICES = [('', 'Todos los estados')] + Ticket.ESTADOS
    PRIORIDADES_CHOICES = [('', 'Todas las prioridades')] + Ticket.PRIORIDADES
    
    estado = forms.ChoiceField(choices=ESTADOS_CHOICES, required=False)
    prioridad = forms.ChoiceField(choices=PRIORIDADES_CHOICES, required=False)
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías"
    )
    numero_factura = forms.CharField(max_length=50, required=False)
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))