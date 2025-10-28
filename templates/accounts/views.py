from django.http import HttpResponseForbidden
from django import forms

class CrearUsuarioAdminForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento',
            'direccion', 'rol', 'estado', 'especialidad', 'max_tickets_simultaneos', 'recibir_notificaciones'
        ]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden')
        if p1 and len(p1) < 8:
            self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class EditarUsuarioAdminForm(forms.ModelForm):
    password = forms.CharField(label="Nueva contraseña (opcional)", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento',
            'direccion', 'rol', 'estado', 'especialidad', 'max_tickets_simultaneos', 'recibir_notificaciones',
            'es_vip', 'tiene_restricciones', 'notas_internas',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            if len(pwd) < 8:
                self.add_error('password', 'La contraseña debe tener al menos 8 caracteres')
                raise forms.ValidationError('Contraseña inválida')
            user.set_password(pwd)
        if commit:
            user.save()
        return user

@login_required
def crear_usuario(request):
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")
    if request.method == 'POST':
        form = CrearUsuarioAdminForm(request.POST)
        if form.is_valid():
            nuevo = form.save()
            messages.success(request, f'Usuario {nuevo.username} creado.')
            return redirect('accounts:detalle_usuario', usuario_id=nuevo.id)
    else:
        form = CrearUsuarioAdminForm()
    return render(request, 'accounts/usuario_form.html', {
        'form': form,
        'titulo_form': 'Crear usuario',
        'mostrar_passwords': True
    })

@login_required
def editar_usuario_admin(request, usuario_id):
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para realizar esta acción.")
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = EditarUsuarioAdminForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado.')
            return redirect('accounts:detalle_usuario', usuario_id=usuario.id)
    else:
        form = EditarUsuarioAdminForm(instance=usuario)
    return render(request, 'accounts/usuario_form.html', {
        'form': form,
        'titulo_form': f'Editar usuario: {usuario.username}',
        'mostrar_passwords': False
    })

@login_required
def detalle_usuario(request, usuario_id):
    if not request.user.es_superadmin():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
    usuario = get_object_or_404(Usuario, id=usuario_id)
    from tickets.models import Ticket
    if usuario.es_cliente():
        tickets_recientes = Ticket.objects.filter(cliente=usuario).order_by('-updated_at')[:10]
    else:
        tickets_recientes = Ticket.objects.filter(asignado_a=usuario).order_by('-updated_at')[:10]
    return render(request, 'accounts/usuario_detalle.html', {
        'usuario': usuario,
        'tickets_recientes': tickets_recientes
    })