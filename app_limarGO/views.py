
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count

from .models import (
    Usuario,
    Cliente,
    Conductor,
    Vehiculo,
    Viaje,
    Pago,
    Mantencion,
)

def inicio(request):
    contexto = {
        "total_clientes": Cliente.objects.count(),
        "total_conductores": Conductor.objects.count(),
        "total_vehiculos": Vehiculo.objects.count(),
        "total_viajes": Viaje.objects.count(),
        "viajes_programados": Viaje.objects.filter(
            estado="Programado"
        ).count(),
        "pagos_pendientes": Pago.objects.filter(
            estado="Pendiente"
        ).count(),
        "total_mantenciones": Mantencion.objects.count(),
    }

    return render(request, "gestion/inicio.html", contexto)



def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by("nombre")

    return render(request, "gestion/usuarios.html", {
        "usuarios": usuarios
    })



def listar_clientes(request):
    clientes = Cliente.objects.all().order_by("nombre")

    return render(request, "gestion/clientes.html", {
        "clientes": clientes
    })



def listar_conductores(request):
    conductores = Conductor.objects.all().order_by("nombre")

    return render(request, "gestion/conductores.html", {
        "conductores": conductores
    })




def listar_vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by("patente")

    return render(request, "gestion/vehiculos.html", {
        "vehiculos": vehiculos
    })


def listar_viajes(request):
    viajes = Viaje.objects.select_related(
        "id_cliente",
        "id_conductor",
        "id_vehiculo",
    ).order_by("-fecha", "-hora")

    return render(request, "gestion/viajes.html", {
        "viajes": viajes
    })



def listar_pagos(request):
    pagos = Pago.objects.select_related(
        "id_viaje",
        "id_viaje__id_cliente",
    ).order_by("-fecha_pago", "-id_pago")

    return render(request, "gestion/pagos.html", {
        "pagos": pagos
    })

def listar_mantenciones(request):
    mantenciones = Mantencion.objects.select_related(
        "id_vehiculo"
    ).order_by("-fecha")

    return render(request, "gestion/mantenciones.html", {
        "mantenciones": mantenciones
    })
