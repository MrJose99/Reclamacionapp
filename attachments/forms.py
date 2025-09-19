from django import forms
from .models import Adjunto


class SubirAdjuntoForm(forms.ModelForm):
    """
    Formulario para subir archivos adjuntos
    """
    class Meta:
        model = Adjunto
        fields = ('archivo',)
        widgets = {
            'archivo': forms.FileInput(attrs={
                'accept': '.jpg,.jpeg,.png,.webp,.mp4,.mov,.pdf',
                'multiple': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].help_text = (
            'Formatos permitidos: JPG, PNG, WEBP, MP4, MOV, PDF. '
            'Tamaño máximo: 25MB por archivo.'
        )