from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from app_limarGO.views import (
    inicio, 
    listar_clientes, crear_cliente, editar_cliente,
    listar_conductores, crear_conductor, editar_conductor,
    listar_vehiculos, crear_vehiculo, editar_vehiculo,
    listar_mantenciones, crear_mantencion, editar_mantencion,
    listar_pagos, crear_pago, editar_pago,
    listar_usuarios,
    listar_viajes, crear_viaje, editar_viaje,
    eliminar_vehiculo, eliminar_viaje, eliminar_pago, eliminar_mantencion,
    eliminar_cliente, eliminar_conductor, registro, reportes,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='app_limarGO/gestion/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/registro/', registro, name='registro'),

    # Vista Principal
    path("", inicio, name="inicio"),

    # Rutas de Clientes
    path("listar_clientes", listar_clientes, name="listar_clientes"),
    path("clientes/nuevo/", crear_cliente, name="crear_cliente"),
    path("clientes/editar/<int:pk>/", editar_cliente, name="editar_cliente"),

    # Rutas de Conductores
    path("listar_conductores", listar_conductores, name="listar_conductores"),
    path("conductores/nuevo/", crear_conductor, name="crear_conductor"),
    path("conductores/editar/<int:pk>/", editar_conductor, name="editar_conductor"),

    # Rutas de Vehículos
    path("listar_vehiculos", listar_vehiculos, name="listar_vehiculos"),
    path("vehiculos/nuevo/", crear_vehiculo, name="crear_vehiculo"),
    path("vehiculos/editar/<int:pk>/", editar_vehiculo, name="editar_vehiculo"),

    # Rutas de Viajes
    path("listar_viajes", listar_viajes, name="listar_viajes"),
    path("viajes/nuevo/", crear_viaje, name="crear_viaje"),
    path("viajes/editar/<int:pk>/", editar_viaje, name="editar_viaje"),

    # Rutas de Pagos
    path("listar_pagos", listar_pagos, name="listar_pagos"),
    path("pagos/nuevo/", crear_pago, name="crear_pago"),
    path("pagos/editar/<int:pk>/", editar_pago, name="editar_pago"),

    # Rutas de Mantenciones
    path("listar_mantenciones", listar_mantenciones, name="listar_mantenciones"),
    path("mantenciones/nuevo/", crear_mantencion, name="crear_mantencion"),
    path("mantenciones/editar/<int:pk>/", editar_mantencion, name="editar_mantencion"),

    # Rutas de eliminación
    path("vehiculos/eliminar/<int:pk>/", eliminar_vehiculo, name="eliminar_vehiculo"),
    path("viajes/eliminar/<int:pk>/", eliminar_viaje, name="eliminar_viaje"),
    path("pagos/eliminar/<int:pk>/", eliminar_pago, name="eliminar_pago"),
    path("mantenciones/eliminar/<int:pk>/", eliminar_mantencion, name="eliminar_mantencion"),
    path("clientes/eliminar/<int:pk>/", eliminar_cliente, name="eliminar_cliente"),
    path("conductores/eliminar/<int:pk>/", eliminar_conductor, name="eliminar_conductor"),

    # Usuarios
    path("listar_usuarios", listar_usuarios, name="listar_usuarios"),

    # Reportes
    path("reportes/", reportes, name="reportes"),
]