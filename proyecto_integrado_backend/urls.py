"""
URL configuration for proyecto_integrado_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_limarGO.views import (inicio, listar_clientes, listar_conductores,
                              listar_vehiculos, listar_mantenciones, listar_pagos,
                              listar_usuarios, listar_viajes)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", inicio, name="inicio"),
    path("listar_clientes", listar_clientes, name="listar_clientes"),
    path("listar_viajes", listar_viajes, name="listar_viajes"),
    path("listar_usuarios", listar_usuarios, name="listar_usuarios"),
    path("listar_vehiculos", listar_vehiculos, name="listar_vehiculos"),
    path("listar_pagos", listar_pagos, name="listar_pagos"),
    path("listar_mantenciones", listar_mantenciones, name="listar_mantenciones")


]
