"""
Ejemplos de Uso - Funcionalidades del Administrador
====================================================

Este archivo contiene ejemplos prácticos de cómo utilizar las nuevas
funcionalidades del rol Administrador implementadas en el modelo Usuario.
"""

from accounts.models import Usuario
from django.utils import timezone


# ============================================================================
# 1. GESTIÓN DE CLIENTES VIP
# ============================================================================

def ejemplo_marcar_cliente_vip():
    """Ejemplo: Marcar un cliente como VIP"""
    
    # Obtener el administrador y el cliente
    admin = Usuario.objects.get(rol='superadmin', username='admin')
    cliente = Usuario.objects.get(email='cliente_importante@example.com')
    
    # Marcar como VIP
    try:
        cliente.marcar_como_vip(admin)
        print(f"✓ Cliente {cliente.get_full_name()} marcado como VIP")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_quitar_marca_vip():
    """Ejemplo: Quitar marca VIP de un cliente"""
    
    admin = Usuario.objects.get(rol='superadmin')
    cliente = Usuario.objects.get(email='cliente@example.com', es_vip=True)
    
    try:
        cliente.quitar_marca_vip(admin)
        print(f"✓ Marca VIP removida de {cliente.get_full_name()}")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_listar_clientes_vip():
    """Ejemplo: Listar todos los clientes VIP"""
    
    clientes_vip = Usuario.objects.filter(rol='cliente', es_vip=True, estado='activo')
    
    print(f"\n=== Clientes VIP ({clientes_vip.count()}) ===")
    for cliente in clientes_vip:
        print(f"- {cliente.get_full_name()} ({cliente.email})")


# ============================================================================
# 2. GESTIÓN DE RESTRICCIONES
# ============================================================================

def ejemplo_aplicar_restriccion():
    """Ejemplo: Aplicar restricción a un cliente por fraude"""
    
    admin = Usuario.objects.get(rol='superadmin')
    cliente = Usuario.objects.get(email='cliente_sospechoso@example.com')
    
    motivo = """
    Cliente detectado con múltiples reclamos fraudulentos:
    - 5 tickets con evidencias falsificadas
    - 3 productos reportados como defectuosos sin serlo
    - Intento de obtener reembolsos indebidos
    """
    
    try:
        cliente.aplicar_restriccion(motivo.strip(), admin)
        print(f"✓ Restricción aplicada a {cliente.get_full_name()}")
        print(f"  Fecha: {cliente.fecha_restriccion}")
        print(f"  Motivo: {cliente.motivo_restriccion}")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_quitar_restriccion():
    """Ejemplo: Quitar restricción después de revisión"""
    
    admin = Usuario.objects.get(rol='superadmin')
    cliente = Usuario.objects.get(email='cliente@example.com', tiene_restricciones=True)
    
    try:
        cliente.quitar_restriccion(admin)
        print(f"✓ Restricción removida de {cliente.get_full_name()}")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_listar_clientes_con_restricciones():
    """Ejemplo: Listar clientes con restricciones activas"""
    
    clientes_restringidos = Usuario.objects.filter(
        rol='cliente',
        tiene_restricciones=True,
        estado='activo'
    ).order_by('-fecha_restriccion')
    
    print(f"\n=== Clientes con Restricciones ({clientes_restringidos.count()}) ===")
    for cliente in clientes_restringidos:
        print(f"\n- {cliente.get_full_name()} ({cliente.email})")
        print(f"  Fecha: {cliente.fecha_restriccion}")
        print(f"  Motivo: {cliente.motivo_restriccion[:100]}...")


# ============================================================================
# 3. NOTAS INTERNAS
# ============================================================================

def ejemplo_agregar_nota_interna():
    """Ejemplo: Agregar nota interna a un cliente"""
    
    agente = Usuario.objects.get(rol='soporte', username='agente1')
    cliente = Usuario.objects.get(email='cliente@example.com')
    
    nota = "Cliente muy exigente. Requiere atención especial y respuestas rápidas."
    
    try:
        cliente.agregar_nota_interna(nota, agente)
        print(f"✓ Nota agregada al cliente {cliente.get_full_name()}")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_ver_notas_internas():
    """Ejemplo: Ver todas las notas internas de un cliente"""
    
    usuario = Usuario.objects.get(username='current_user')
    cliente = Usuario.objects.get(email='cliente@example.com')
    
    if usuario.puede_ver_notas_internas():
        if cliente.notas_internas:
            print(f"\n=== Notas Internas de {cliente.get_full_name()} ===")
            print(cliente.notas_internas)
        else:
            print("No hay notas internas para este cliente")
    else:
        print("No tienes permisos para ver notas internas")


def ejemplo_agregar_multiples_notas():
    """Ejemplo: Agregar múltiples notas a lo largo del tiempo"""
    
    agente1 = Usuario.objects.get(username='agente1')
    agente2 = Usuario.objects.get(username='agente2')
    admin = Usuario.objects.get(rol='superadmin')
    cliente = Usuario.objects.get(email='cliente@example.com')
    
    # Primera nota del agente 1
    cliente.agregar_nota_interna(
        "Primera interacción. Cliente amable y colaborador.",
        agente1
    )
    
    # Segunda nota del agente 2
    cliente.agregar_nota_interna(
        "Cliente reporta problema recurrente. Posible defecto de fábrica.",
        agente2
    )
    
    # Nota del administrador
    cliente.agregar_nota_interna(
        "Aprobado para reemplazo directo sin evaluación adicional.",
        admin
    )
    
    print(f"✓ 3 notas agregadas al cliente {cliente.get_full_name()}")


# ============================================================================
# 4. MÉTRICAS Y DESEMPEÑO
# ============================================================================

def ejemplo_obtener_metricas_agente():
    """Ejemplo: Obtener métricas de desempeño de un agente"""
    
    agente = Usuario.objects.get(rol='soporte', username='agente1')
    metricas = agente.get_metricas_desempeno()
    
    print(f"\n=== Métricas de {agente.get_full_name()} ===")
    print(f"Tickets activos: {metricas['tickets_activos']}")
    print(f"Tickets resueltos: {metricas['tickets_resueltos']}")
    print(f"Tickets totales: {metricas['tickets_totales']}")
    print(f"Tasa de resolución: {metricas['tasa_resolucion']:.2f}%")
    print(f"Tiempo promedio de resolución: {metricas['tiempo_promedio_resolucion']:.2f} días")
    print(f"Tickets reabiertos: {metricas['tickets_reabiertos']}")
    print(f"Tickets escalados: {metricas['tickets_escalados']}")
    print(f"Porcentaje de carga: {metricas['porcentaje_carga']:.2f}%")
    print(f"Sobrecargado: {'Sí' if metricas['esta_sobrecargado'] else 'No'}")


def ejemplo_comparar_desempeno_agentes():
    """Ejemplo: Comparar desempeño de todos los agentes"""
    
    agentes = Usuario.objects.filter(rol='soporte', estado='activo')
    
    print(f"\n=== Comparación de Desempeño de Agentes ===\n")
    print(f"{'Agente':<25} {'Activos':<10} {'Resueltos':<12} {'Tasa':<10} {'Tiempo Prom.':<15}")
    print("-" * 80)
    
    for agente in agentes:
        metricas = agente.get_metricas_desempeno()
        print(f"{agente.get_full_name():<25} "
              f"{metricas['tickets_activos']:<10} "
              f"{metricas['tickets_resueltos']:<12} "
              f"{metricas['tasa_resolucion']:<10.2f}% "
              f"{metricas['tiempo_promedio_resolucion']:<15.2f} días")


def ejemplo_identificar_agentes_sobrecargados():
    """Ejemplo: Identificar agentes sobrecargados"""
    
    agentes = Usuario.objects.filter(
        rol__in=['soporte', 'soporte_tecnico'],
        estado='activo'
    )
    
    sobrecargados = []
    for agente in agentes:
        if agente.esta_sobrecargado():
            sobrecargados.append({
                'agente': agente,
                'activos': agente.get_tickets_activos_count(),
                'limite': agente.max_tickets_simultaneos,
                'porcentaje': agente.get_porcentaje_carga_trabajo()
            })
    
    if sobrecargados:
        print(f"\n=== Agentes Sobrecargados ({len(sobrecargados)}) ===\n")
        for item in sobrecargados:
            print(f"⚠ {item['agente'].get_full_name()}")
            print(f"  Tickets activos: {item['activos']} / {item['limite']}")
            print(f"  Carga: {item['porcentaje']:.2f}%\n")
    else:
        print("✓ No hay agentes sobrecargados")


def ejemplo_agentes_disponibles_para_asignacion():
    """Ejemplo: Obtener agentes disponibles ordenados por carga"""
    
    agentes_disponibles = Usuario.objects.agentes_disponibles()
    
    print(f"\n=== Agentes Disponibles para Asignación ===\n")
    for agente in agentes_disponibles[:5]:  # Top 5
        activos = agente.get_tickets_activos_count()
        porcentaje = agente.get_porcentaje_carga_trabajo()
        print(f"- {agente.get_full_name()}: {activos} tickets ({porcentaje:.1f}% carga)")


# ============================================================================
# 5. ESTADÍSTICAS DE CLIENTES
# ============================================================================

def ejemplo_obtener_estadisticas_cliente():
    """Ejemplo: Obtener estadísticas completas de un cliente"""
    
    cliente = Usuario.objects.get(email='cliente@example.com')
    stats = cliente.get_estadisticas_cliente()
    
    if stats:
        print(f"\n=== Estadísticas de {cliente.get_full_name()} ===")
        print(f"Total de tickets: {stats['total_tickets']}")
        print(f"Tickets aprobados: {stats['tickets_aprobados']}")
        print(f"Tickets rechazados: {stats['tickets_rechazados']}")
        print(f"Tickets resueltos: {stats['tickets_resueltos']}")
        print(f"Tickets activos: {stats['tickets_activos']}")
        print(f"Tiempo promedio de resolución: {stats['tiempo_promedio_resolucion']:.2f} días")
        
        # Calcular tasa de aprobación
        if stats['total_tickets'] > 0:
            tasa_aprobacion = (stats['tickets_aprobados'] / stats['total_tickets']) * 100
            print(f"Tasa de aprobación: {tasa_aprobacion:.2f}%")


def ejemplo_identificar_clientes_problematicos():
    """Ejemplo: Identificar clientes con alta tasa de rechazo"""
    
    clientes = Usuario.objects.filter(rol='cliente', estado='activo')
    problematicos = []
    
    for cliente in clientes:
        stats = cliente.get_estadisticas_cliente()
        if stats and stats['total_tickets'] >= 3:  # Mínimo 3 tickets
            tasa_rechazo = (stats['tickets_rechazados'] / stats['total_tickets']) * 100
            if tasa_rechazo >= 50:  # 50% o más de rechazo
                problematicos.append({
                    'cliente': cliente,
                    'total': stats['total_tickets'],
                    'rechazados': stats['tickets_rechazados'],
                    'tasa_rechazo': tasa_rechazo
                })
    
    if problematicos:
        print(f"\n=== Clientes con Alta Tasa de Rechazo ({len(problematicos)}) ===\n")
        for item in problematicos:
            print(f"⚠ {item['cliente'].get_full_name()} ({item['cliente'].email})")
            print(f"  Total tickets: {item['total']}")
            print(f"  Rechazados: {item['rechazados']}")
            print(f"  Tasa de rechazo: {item['tasa_rechazo']:.2f}%\n")


def ejemplo_historial_tickets_cliente():
    """Ejemplo: Ver historial completo de tickets de un cliente"""
    
    cliente = Usuario.objects.get(email='cliente@example.com')
    historial = cliente.get_historial_tickets_cliente()
    
    if historial:
        print(f"\n=== Historial de Tickets de {cliente.get_full_name()} ===\n")
        for ticket in historial[:10]:  # Últimos 10
            print(f"Ticket #{ticket.id}")
            print(f"  Estado: {ticket.get_estado_display()}")
            print(f"  Creado: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Producto: {ticket.producto if hasattr(ticket, 'producto') else 'N/A'}")
            print()


# ============================================================================
# 6. GESTIÓN DE USUARIOS
# ============================================================================

def ejemplo_desactivar_usuario():
    """Ejemplo: Desactivar un usuario"""
    
    admin = Usuario.objects.get(rol='superadmin')
    empleado = Usuario.objects.get(username='empleado_saliente')
    
    motivo = "Fin de contrato laboral - Último día: 2024-12-31"
    
    try:
        empleado.desactivar_usuario(motivo, admin)
        print(f"✓ Usuario {empleado.get_full_name()} desactivado")
        print(f"  Motivo: {empleado.motivo_desactivacion}")
        print(f"  Fecha: {empleado.fecha_desactivacion}")
        print(f"  Desactivado por: {empleado.desactivado_por.get_full_name()}")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_activar_usuario():
    """Ejemplo: Reactivar un usuario"""
    
    admin = Usuario.objects.get(rol='superadmin')
    empleado = Usuario.objects.get(username='empleado_reingreso', estado='inactivo')
    
    try:
        empleado.activar_usuario(admin)
        print(f"✓ Usuario {empleado.get_full_name()} reactivado")
    except PermissionError as e:
        print(f"✗ Error: {e}")


def ejemplo_verificar_si_puede_eliminar_usuario():
    """Ejemplo: Verificar si un usuario puede ser eliminado"""
    
    usuario = Usuario.objects.get(username='usuario_a_eliminar')
    
    if usuario.puede_ser_eliminado():
        print(f"✓ {usuario.get_full_name()} puede ser eliminado (sin tickets asignados)")
        # Aquí se podría proceder con la eliminación
    else:
        tickets_count = usuario.tickets_asignados.count()
        print(f"✗ {usuario.get_full_name()} NO puede ser eliminado")
        print(f"  Tiene {tickets_count} tickets asignados")
        print(f"  Debe reasignar los tickets antes de eliminar")


def ejemplo_actualizar_ultima_actividad():
    """Ejemplo: Actualizar última actividad (útil en login o acciones importantes)"""
    
    usuario = Usuario.objects.get(username='usuario_actual')
    usuario.actualizar_ultima_actividad()
    print(f"✓ Última actividad actualizada: {usuario.ultima_actividad}")


def ejemplo_listar_usuarios_inactivos():
    """Ejemplo: Listar usuarios inactivos con detalles"""
    
    usuarios_inactivos = Usuario.objects.filter(estado='inactivo').order_by('-fecha_desactivacion')
    
    print(f"\n=== Usuarios Inactivos ({usuarios_inactivos.count()}) ===\n")
    for usuario in usuarios_inactivos:
        print(f"- {usuario.get_full_name()} ({usuario.get_rol_display()})")
        if usuario.fecha_desactivacion:
            print(f"  Desactivado: {usuario.fecha_desactivacion.strftime('%Y-%m-%d')}")
        if usuario.desactivado_por:
            print(f"  Por: {usuario.desactivado_por.get_full_name()}")
        if usuario.motivo_desactivacion:
            print(f"  Motivo: {usuario.motivo_desactivacion[:80]}...")
        print()


# ============================================================================
# 7. VERIFICACIÓN DE PERMISOS
# ============================================================================

def ejemplo_verificar_permisos_usuario():
    """Ejemplo: Verificar todos los permisos de un usuario"""
    
    usuario = Usuario.objects.get(username='usuario_actual')
    
    print(f"\n=== Permisos de {usuario.get_full_name()} ({usuario.get_rol_display()}) ===\n")
    
    permisos = {
        'Gestionar tickets': usuario.puede_gestionar_tickets(),
        'Eliminar elementos': usuario.puede_eliminar(),
        'Asignar tickets': usuario.puede_asignar_tickets(),
        'Derivar a técnico': usuario.puede_derivar_a_tecnico(),
        'Reasignar libremente': usuario.puede_reasignar_libremente(),
        'Acceder todos los tickets': usuario.puede_acceder_todos_tickets(),
        'Gestionar usuarios': usuario.puede_gestionar_usuarios(),
        'Crear empleados': usuario.puede_crear_empleados(),
        'Editar cualquier usuario': usuario.puede_editar_cualquier_usuario(),
        'Desactivar usuarios': usuario.puede_desactivar_usuarios(),
        'Eliminar usuarios': usuario.puede_eliminar_usuarios(),
        'Ver auditoría completa': usuario.puede_ver_auditoria_completa(),
        'Configurar sistema': usuario.puede_configurar_sistema(),
        'Generar reportes': usuario.puede_generar_reportes(),
        'Ver métricas globales': usuario.puede_ver_metricas_globales(),
        'Forzar cambios de estado': usuario.puede_forzar_cambios_estado(),
        'Editar datos de ticket': usuario.puede_editar_datos_ticket(),
        'Gestionar clientes': usuario.puede_gestionar_clientes(),
        'Marcar cliente VIP': usuario.puede_marcar_cliente_vip(),
        'Aplicar restricciones': usuario.puede_aplicar_restricciones_cliente(),
        'Ver notas internas': usuario.puede_ver_notas_internas(),
        'Editar notas internas': usuario.puede_editar_notas_internas(),
    }
    
    for permiso, tiene_permiso in permisos.items():
        simbolo = '✓' if tiene_permiso else '✗'
        print(f"{simbolo} {permiso}")


def ejemplo_verificar_cambio_estado_ticket():
    """Ejemplo: Verificar si un usuario puede cambiar el estado de un ticket"""
    
    usuario = Usuario.objects.get(username='usuario_actual')
    
    # Probar diferentes transiciones
    transiciones = [
        ('abierto', 'en_revision'),
        ('en_revision', 'aceptado'),
        ('aceptado', 'en_reparacion'),
        ('en_reparacion', 'resuelto'),
        ('resuelto', 'cerrado'),
        ('cerrado', 'abierto'),  # No permitida normalmente
    ]
    
    print(f"\n=== Transiciones de Estado Permitidas para {usuario.get_full_name()} ===\n")
    for estado_actual, nuevo_estado in transiciones:
        puede = usuario.puede_cambiar_estado_ticket(estado_actual, nuevo_estado)
        simbolo = '✓' if puede else '✗'
        print(f"{simbolo} {estado_actual} → {nuevo_estado}")


# ============================================================================
# 8. REPORTES Y ANÁLISIS
# ============================================================================

def ejemplo_reporte_carga_trabajo_equipo():
    """Ejemplo: Generar reporte de carga de trabajo del equipo"""
    
    print(f"\n=== Reporte de Carga de Trabajo del Equipo ===\n")
    print(f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Agentes de soporte
    print("AGENTES DE SOPORTE:")
    print("-" * 80)
    agentes = Usuario.objects.filter(rol='soporte', estado='activo')
    for agente in agentes:
        activos = agente.get_tickets_activos_count()
        porcentaje = agente.get_porcentaje_carga_trabajo()
        estado = "⚠ SOBRECARGADO" if agente.esta_sobrecargado() else "✓ Normal"
        print(f"{agente.get_full_name():<30} {activos:>3}/{agente.max_tickets_simultaneos:<3} "
              f"({porcentaje:>6.2f}%)  {estado}")
    
    print("\n")
    
    # Técnicos
    print("SOPORTE TÉCNICO:")
    print("-" * 80)
    tecnicos = Usuario.objects.filter(rol='soporte_tecnico', estado='activo')
    for tecnico in tecnicos:
        activos = tecnico.get_tickets_activos_count()
        porcentaje = tecnico.get_porcentaje_carga_trabajo()
        especialidad = tecnico.especialidad or "General"
        estado = "⚠ SOBRECARGADO" if tecnico.esta_sobrecargado() else "✓ Normal"
        print(f"{tecnico.get_full_name():<30} {activos:>3}/{tecnico.max_tickets_simultaneos:<3} "
              f"({porcentaje:>6.2f}%)  [{especialidad}]  {estado}")


def ejemplo_reporte_clientes_especiales():
    """Ejemplo: Generar reporte de clientes VIP y con restricciones"""
    
    print(f"\n=== Reporte de Clientes Especiales ===\n")
    print(f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Clientes VIP
    vips = Usuario.objects.filter(rol='cliente', es_vip=True, estado='activo')
    print(f"CLIENTES VIP ({vips.count()}):")
    print("-" * 80)
    for cliente in vips:
        stats = cliente.get_estadisticas_cliente()
        print(f"⭐ {cliente.get_full_name():<30} {cliente.email:<35} "
              f"Tickets: {stats['total_tickets']}")
    
    print("\n")
    
    # Clientes con restricciones
    restringidos = Usuario.objects.filter(rol='cliente', tiene_restricciones=True, estado='activo')
    print(f"CLIENTES CON RESTRICCIONES ({restringidos.count()}):")
    print("-" * 80)
    for cliente in restringidos:
        fecha = cliente.fecha_restriccion.strftime('%Y-%m-%d') if cliente.fecha_restriccion else 'N/A'
        print(f"⚠ {cliente.get_full_name():<30} {cliente.email:<35} Desde: {fecha}")


def ejemplo_reporte_desempeno_mensual():
    """Ejemplo: Generar reporte de desempeño mensual de agentes"""
    
    print(f"\n=== Reporte de Desempeño Mensual ===\n")
    print(f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    agentes = Usuario.objects.filter(
        rol__in=['soporte', 'soporte_tecnico'],
        estado='activo'
    ).order_by('rol', 'last_name')
    
    print(f"{'Agente':<25} {'Rol':<20} {'Resueltos':<12} {'Tasa':<10} {'Tiempo Prom.':<15}")
    print("=" * 90)
    
    for agente in agentes:
        metricas = agente.get_metricas_desempeno()
        print(f"{agente.get_full_name():<25} "
              f"{agente.get_rol_display():<20} "
              f"{metricas['tickets_resueltos']:<12} "
              f"{metricas['tasa_resolucion']:<10.2f}% "
              f"{metricas['tiempo_promedio_resolucion']:<15.2f} días")


# ============================================================================
# 9. CASOS DE USO COMPLEJOS
# ============================================================================

def ejemplo_flujo_completo_gestion_cliente():
    """Ejemplo: Flujo completo de gestión de un cliente problemático"""
    
    admin = Usuario.objects.get(rol='superadmin')
    cliente = Usuario.objects.get(email='cliente_problematico@example.com')
    
    print(f"\n=== Gestión de Cliente: {cliente.get_full_name()} ===\n")
    
    # 1. Revisar estadísticas
    stats = cliente.get_estadisticas_cliente()
    print("1. Estadísticas del cliente:")
    print(f"   Total tickets: {stats['total_tickets']}")
    print(f"   Rechazados: {stats['tickets_rechazados']}")
    tasa_rechazo = (stats['tickets_rechazados'] / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0
    print(f"   Tasa de rechazo: {tasa_rechazo:.2f}%\n")
    
    # 2. Agregar nota interna
    print("2. Agregando nota interna...")
    cliente.agregar_nota_interna(
        "Cliente con alta tasa de rechazo. Revisar evidencias cuidadosamente.",
        admin
    )
    print("   ✓ Nota agregada\n")
    
    # 3. Aplicar restricción si es necesario
    if tasa_rechazo >= 60:
        print("3. Aplicando restricción por alta tasa de rechazo...")
        cliente.aplicar_restriccion(
            f"Alta tasa de rechazo ({tasa_rechazo:.2f}%). "
            f"Requiere revisión manual de todos los tickets futuros.",
            admin
        )
        print("   ✓ Restricción aplicada\n")
    else:
        print("3. No se requiere restricción en este momento\n")
    
    # 4. Resumen final
    print("4. Estado final del cliente:")
    print(f"   VIP: {'Sí' if cliente.es_vip else 'No'}")
    print(f"   Restricciones: {'Sí' if cliente.tiene_restricciones else 'No'}")
    print(f"   Última actividad: {cliente.ultima_actividad or 'N/A'}")


def ejemplo_reasignacion_tickets_empleado_saliente():
    """Ejemplo: Reasignar tickets de un empleado que sale"""
    
    admin = Usuario.objects.get(rol='superadmin')
    empleado_saliente = Usuario.objects.get(username='empleado_saliente')
    
    print(f"\n=== Reasignación de Tickets: {empleado_saliente.get_full_name()} ===\n")
    
    # 1. Verificar tickets activos
    tickets_activos = empleado_saliente.get_tickets_activos_count()
    print(f"1. Tickets activos a reasignar: {tickets_activos}\n")
    
    if tickets_activos > 0:
        # 2. Obtener agentes disponibles
        print("2. Buscando agentes disponibles...")
        agentes_disponibles = Usuario.objects.agentes_disponibles()[:3]
        
        print("   Agentes con menor carga:")
        for agente in agentes_disponibles:
            carga = agente.get_porcentaje_carga_trabajo()
            print(f"   - {agente.get_full_name()}: {carga:.1f}% carga")
        print()
        
        # 3. Reasignar (simulado - requiere implementación en modelo Ticket)
        print("3. Reasignando tickets...")
        print("   ✓ Tickets reasignados exitosamente\n")
    
    # 4. Desactivar empleado
    print("4. Desactivando empleado...")
    empleado_saliente.desactivar_usuario(
        "Fin de contrato laboral. Tickets reasignados.",
        admin
    )
    print(f"   ✓ Empleado desactivado\n")


# ============================================================================
# FUNCIÓN PRINCIPAL PARA EJECUTAR EJEMPLOS
# ============================================================================

def ejecutar_todos_los_ejemplos():
    """Ejecuta todos los ejemplos (comentar los que no se necesiten)"""
    
    print("\n" + "=" * 80)
    print("EJEMPLOS DE USO - FUNCIONALIDADES DEL ADMINISTRADOR")
    print("=" * 80)
    
    # Descomentar los ejemplos que quieras ejecutar:
    
    # ejemplo_marcar_cliente_vip()
    # ejemplo_quitar_marca_vip()
    # ejemplo_listar_clientes_vip()
    
    # ejemplo_aplicar_restriccion()
    # ejemplo_quitar_restriccion()
    # ejemplo_listar_clientes_con_restricciones()
    
    # ejemplo_agregar_nota_interna()
    # ejemplo_ver_notas_internas()
    # ejemplo_agregar_multiples_notas()
    
    # ejemplo_obtener_metricas_agente()
    # ejemplo_comparar_desempeno_agentes()
    # ejemplo_identificar_agentes_sobrecargados()
    # ejemplo_agentes_disponibles_para_asignacion()
    
    # ejemplo_obtener_estadisticas_cliente()
    # ejemplo_identificar_clientes_problematicos()
    # ejemplo_historial_tickets_cliente()
    
    # ejemplo_desactivar_usuario()
    # ejemplo_activar_usuario()
    # ejemplo_verificar_si_puede_eliminar_usuario()
    # ejemplo_actualizar_ultima_actividad()
    # ejemplo_listar_usuarios_inactivos()
    
    # ejemplo_verificar_permisos_usuario()
    # ejemplo_verificar_cambio_estado_ticket()
    
    # ejemplo_reporte_carga_trabajo_equipo()
    # ejemplo_reporte_clientes_especiales()
    # ejemplo_reporte_desempeno_mensual()
    
    # ejemplo_flujo_completo_gestion_cliente()
    # ejemplo_reasignacion_tickets_empleado_saliente()
    
    print("\n" + "=" * 80)
    print("FIN DE EJEMPLOS")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    # Para ejecutar desde Django shell:
    # python manage.py shell < ejemplos_uso_administrador.py
    
    # O importar en Django shell:
    # from ejemplos_uso_administrador import *
    # ejemplo_marcar_cliente_vip()
    
    pass
