from django.urls import path
from . import views

app_name = 'attachments'

urlpatterns = [
    # URLs para gestión de adjuntos
    # path('subir/', views.subir_adjunto, name='subir'),
    # path('<uuid:adjunto_id>/', views.ver_adjunto, name='ver'),
    # path('<uuid:adjunto_id>/eliminar/', views.eliminar_adjunto, name='eliminar'),
]