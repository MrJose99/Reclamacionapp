from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Tu cuenta ha sido creada con éxito.')
            return redirect('inicio')
    else:
        form = UserRegisterForm()
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {username}!")
                return redirect('inicio')  
        messages.error(request, "Usuario o contraseña incorrectos.")  
    else:
        form = AuthenticationForm()  
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    messages.success(request, '¡Has cerrado sesión correctamente!')
    return redirect('Login')  