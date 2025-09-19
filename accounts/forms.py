from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios
    """
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=False)
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    direccion = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 
                 'fecha_nacimiento', 'direccion', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data['telefono']
        user.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
        return user


class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para editar perfil de usuario
    """
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 
                 'fecha_nacimiento', 'direccion')
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }