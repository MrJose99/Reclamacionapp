# Al final de tu urlpatterns:
urlpatterns += [
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<uuid:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/<uuid:usuario_id>/editar/', views.editar_usuario_admin, name='editar_usuario'),
]