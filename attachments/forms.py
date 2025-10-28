from django import forms
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Adjunto

User = get_user_model()


class AdjuntoForm(forms.ModelForm):
    """Formulario para subir un archivo adjunto"""

    class Meta:
        model = Adjunto
        fields = ['archivo', 'descripcion', 'es_publico']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.mp4,.avi,.mov,.wmv,.flv,.webm,.mkv,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar,.7z'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción opcional del archivo...'
            }),
            'es_publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Configurar ayuda y validaciones
        self.fields['archivo'].help_text = (
            'Tipos permitidos: JPG, PNG, WEBP, MP4, MOV, PDF, DOC, XLS, etc. '
            'Tamaño máximo: 25MB por archivo.'
        )

        # Los clientes no pueden subir archivos privados
        if user and user.es_cliente():
            self.fields['es_publico'].widget = forms.HiddenInput()
            self.fields['es_publico'].initial = True
        else:
            self.fields['es_publico'].help_text = 'Los archivos públicos son visibles para el cliente'


class MultipleFileInput(forms.ClearableFileInput):
    """Widget personalizado para múltiples archivos"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Campo personalizado para múltiples archivos"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Reuse the parent single-file clean for each item when multiple files are provided
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class AdjuntoMultipleForm(forms.Form):
    """Formulario para subir múltiples archivos a la vez"""

    archivos = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx',
            'multiple': True
        }),
        help_text='Puede seleccionar múltiples archivos. Tamaño máximo: 25MB por archivo.',
        required=False  # Cambiado a False para que no sea obligatorio
    )

    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Descripción opcional de los archivos...'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_archivos(self):
        archivos = self.cleaned_data.get('archivos', [])
        if not archivos:
            return []
            
        if not isinstance(archivos, list):
            archivos = [archivos]

        for archivo in archivos:
            if archivo.size > 25 * 1024 * 1024:  # 25MB
                raise forms.ValidationError(f'El archivo {archivo.name} excede el tamaño máximo de 25MB')

            ext = os.path.splitext(archivo.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']:
                raise forms.ValidationError(f'El tipo de archivo {ext} no está permitido')

        return archivos


class FiltroAdjuntosForm(forms.Form):
    """Formulario para filtrar adjuntos"""

    TIPOS_ARCHIVO = [
        ('', 'Todos los tipos'),
        ('imagen', 'Imágenes'),
        ('video', 'Videos'),
        ('documento', 'Documentos'),
        ('otro', 'Otros'),
    ]

    tipo_archivo = forms.ChoiceField(
        choices=TIPOS_ARCHIVO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de archivo...'
        })
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

    solo_publicos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo archivos públicos'
    )