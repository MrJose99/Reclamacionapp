# Solución al Problema de Login: "Credenciales inválidas o cuenta inactiva"

## Problema Identificado

El error "Credenciales inválidas o cuenta inactiva" ocurría porque los nuevos usuarios no tenían correctamente configurados los campos:
- `is_active` (campo de Django)
- `estado` (campo personalizado del modelo Usuario)

## Cambios Realizados

### 1. Formulario de Registro (`accounts/forms.py`)
Se modificó el método `save()` del formulario `RegistroUsuarioForm` para establecer explícitamente:
```python
usuario.is_active = True
usuario.estado = 'activo'
```

### 2. Manager de Usuario (`accounts/models.py`)
Se actualizó el método `create_user()` del `UsuarioManager` para establecer valores por defecto:
```python
extra_fields.setdefault('is_active', True)
extra_fields.setdefault('estado', 'activo')
```

### 3. Admin de Django (`accounts/admin.py`)
Se agregó el método `save_model()` para asegurar que los usuarios creados desde el panel de administración también estén activos:
```python
def save_model(self, request, obj, form, change):
    if not change:  # Si es un nuevo usuario
        if not hasattr(obj, 'is_active') or obj.is_active is None:
            obj.is_active = True
        if not obj.estado:
            obj.estado = 'activo'
    super().save_model(request, obj, form, change)
```

### 4. Comando de Corrección (`accounts/management/commands/corregir_usuarios.py`)
Se creó un comando de Django para corregir usuarios existentes con problemas.

## Cómo Usar

### Para Nuevos Usuarios
Los nuevos usuarios creados a partir de ahora (ya sea por registro o desde el admin) tendrán automáticamente:
- `is_active = True`
- `estado = 'activo'`

### Para Corregir Usuarios Existentes

Si tienes usuarios que ya fueron creados y tienen problemas para iniciar sesión, ejecuta:

```bash
# Ver qué usuarios tienen problemas (sin hacer cambios)
python manage.py corregir_usuarios --dry-run

# Corregir los usuarios con problemas
python manage.py corregir_usuarios
```

## Verificación

Para verificar el estado de los usuarios en tu base de datos:

```bash
python manage.py shell -c "from accounts.models import Usuario; [print(f'{u.username}: is_active={u.is_active}, estado={u.estado}') for u in Usuario.objects.all()]"
```

## Notas Importantes

1. **Todos los nuevos usuarios** creados después de estos cambios podrán iniciar sesión sin problemas.

2. **Usuarios existentes**: Si tienes usuarios que ya fueron creados antes de estos cambios, usa el comando `corregir_usuarios` para arreglarlos.

3. **Validación de Login**: El sistema valida que:
   - El usuario exista
   - `is_active = True`
   - `estado = 'activo'`
   
   Si alguna de estas condiciones no se cumple, se mostrará el error "Credenciales inválidas o cuenta inactiva".

4. **Creación desde el Admin**: Ahora cuando crees usuarios desde el panel de administración de Django, el campo `is_active` estará visible y se establecerá automáticamente en `True`.

## Solución de Problemas

Si un usuario específico sigue sin poder iniciar sesión:

1. Verifica su estado en el shell de Django:
```bash
python manage.py shell
>>> from accounts.models import Usuario
>>> u = Usuario.objects.get(username='nombre_usuario')
>>> print(f'is_active: {u.is_active}, estado: {u.estado}')
```

2. Si los valores no son correctos, corrígelos manualmente:
```bash
>>> u.is_active = True
>>> u.estado = 'activo'
>>> u.save()
```

3. O usa el comando de corrección:
```bash
python manage.py corregir_usuarios
```
