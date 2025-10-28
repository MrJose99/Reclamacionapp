from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Usuario
User = get_user_model()


class RegistroUsuarioForm(UserCreationForm):
    """Formulario para registro de nuevos usuarios"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombres'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )

    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    direccion = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección (opcional)'
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',   
                'class': 'form-control'
            }
        ),
        label="Fecha de nacimiento"
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'fecha_nacimiento','password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.first_name = self.cleaned_data['first_name']
        usuario.last_name = self.cleaned_data['last_name']
        usuario.telefono = self.cleaned_data.get('telefono') or None
        usuario.direccion = self.cleaned_data.get('direccion') or None
        usuario.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento') or None
        # Asegurar que el usuario esté activo
        usuario.is_active = True
        usuario.estado = 'activo'
        if commit:
            usuario.save()
        return usuario


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'direccion')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.fecha_nacimiento:
            self.initial['fecha_nacimiento'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')


class LoginForm(forms.Form):
    """Formulario personalizado para login"""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o correo electrónico'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class AdminUsuarioForm(UserCreationForm):
    """Formulario de creación de usuarios administrativos (superadmin, soporte, técnico, empleado)"""

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # Esto genera un input date en HTML
                'class': 'form-control'
            }
        ),
        label="Fecha de nacimiento"
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'rol', 'estado', 'telefono', 'direccion', 'fecha_nacimiento',
            'especialidad', 'max_tickets_simultaneos', 'recibir_notificaciones',
            'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs.update({'class': 'form-control'})
        # Personalizar selects
        self.fields['rol'].widget.attrs.update({'class': 'form-select'})
        self.fields['estado'].widget.attrs.update({'class': 'form-select'})

    def clean_rol(self):
        rol = self.cleaned_data['rol']
        if rol == 'cliente':
            raise forms.ValidationError("No puedes crear usuarios con rol de cliente desde este formulario.")
        return rol