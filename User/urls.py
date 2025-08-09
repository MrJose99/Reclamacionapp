from django.urls import path

from User import views

urlpatterns = [
    path('',views.login_view, name='Login'),
    path('logout',views.logout_view,name='Logout'),
    path('registro',views.register,name='Registro'),

]
