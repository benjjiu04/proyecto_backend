from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import (
    Usuario,
    Cliente,
    Conductor,
    Vehiculo,
    Viaje,
    Pago,
    Mantencion,
)
from .forms import (
    ClienteForm,
    ConductorForm,
    VehiculoForm,
    ViajeForm,
    PagoForm,
    MantencionForm,
)

# ==========================================
# VISTA PRINCIPAL (DASHBOARD)
# ==========================================
@login_required(login_url='/accounts/login/')
def inicio(request: HttpRequest) -> HttpResponse:

    contexto = {

        "total_clientes": Cliente.objects.count(),
        "total_conductores": Conductor.objects.count(),
        "total_vehiculos": Vehiculo.objects.count(),
        "total_viajes": Viaje.objects.count(),
        "total_pagos": Pago.objects.count(),

        "viajes_programados": Viaje.objects.filter(
            estado="Programado").count(),

        "pagos_pendientes": Pago.objects.filter(
            estado="Pendiente").count(),

        "total_mantenciones": Mantencion.objects.count(),
    }

    return render(request, "gestion/index.html", contexto)


# ==========================================
# LISTADOS
# ==========================================
@login_required(login_url='/accounts/login/')
def listar_usuarios(request: HttpRequest) -> HttpResponse:

    usuarios = Usuario.objects.all().order_by("nombre")
    return render(request, "gestion/usuarios.html", {"usuarios": usuarios})


@login_required(login_url='/accounts/login/')
def listar_clientes(request: HttpRequest) -> HttpResponse:

    clientes = Cliente.objects.all().order_by("nombre")
    return render(request, "gestion/clientes.html", {"clientes": clientes})


@login_required(login_url='/accounts/login/')
def listar_conductores(request: HttpRequest) -> HttpResponse:

    conductores = Conductor.objects.all().order_by("nombre")
    return render(request, "gestion/conductores.html", {"conductores": conductores})


@login_required(login_url='/accounts/login/')
def listar_vehiculos(request: HttpRequest) -> HttpResponse:

    vehiculos = Vehiculo.objects.all().order_by("patente")
    return render(request, "gestion/vehiculos.html", {"vehiculos": vehiculos})


@login_required(login_url='/accounts/login/')
def listar_viajes(request: HttpRequest) -> HttpResponse:

    viajes = Viaje.objects.select_related(
        "id_cliente",
        "id_conductor",
        "id_vehiculo",
    ).order_by("-fecha", "-hora")
    return render(request, "gestion/viajes.html", {"viajes": viajes})


@login_required(login_url='/accounts/login/')
def listar_pagos(request: HttpRequest) -> HttpResponse:

    pagos = Pago.objects.select_related(
        "id_viaje",
        "id_viaje__id_cliente",
    ).order_by("-fecha_pago", "-id_pago")
    return render(request, "gestion/pagos.html", {"pagos": pagos})


@login_required(login_url='/accounts/login/')
def listar_mantenciones(request: HttpRequest) -> HttpResponse:

    mantenciones = Mantencion.objects.select_related(
        "id_vehiculo"
    ).order_by("-fecha")
    return render(request, "gestion/mantenciones.html", {"mantenciones": mantenciones})


# ==========================================
# CREACIÓN DE REGISTROS
# ==========================================

@login_required(login_url='/accounts/login/')
def crear_cliente(request: HttpRequest):
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Cliente registrado exitosamente.")
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'gestion/form_cliente.html', {'form': form})


@login_required(login_url='/accounts/login/')
def crear_conductor(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    
    if request.method == 'POST':
        form = ConductorForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(request, "Conductor registrado exitosamente.")
            return redirect('listar_conductores')
    else:
        form = ConductorForm()
    return render(request, 'gestion/form_conductor.html', {'form': form})


@login_required(login_url='/accounts/login/')
def crear_vehiculo(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Vehículo registrado exitosamente.")
            return redirect('listar_vehiculos')
    else:
        form = VehiculoForm()
    return render(request, 'gestion/form_vehiculo.html', {'form': form})


@login_required(login_url='/accounts/login/')
def crear_viaje(request):
    
    if request.method == 'POST':
        form = ViajeForm(request.POST)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Viaje programado exitosamente.")
            return redirect('listar_viajes')
    else:
        form = ViajeForm()
    return render(request, 'gestion/form_viaje.html', {'form': form})


@login_required(login_url='/accounts/login/')
def crear_pago(request):
    
    if request.method == 'POST':
        form = PagoForm(request.POST)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Pago registrado exitosamente.")
            return redirect('listar_pagos')
    else:
        form = PagoForm()
    return render(request, 'gestion/form_pago.html', {'form': form})


@login_required(login_url='/accounts/login/')
def crear_mantencion(request):
    
    if request.method == 'POST':
        form = MantencionForm(request.POST)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Mantención registrada exitosamente.")
            return redirect('listar_mantenciones')
    else:
        form = MantencionForm()
    return render(request, 'gestion/form_mantencion.html', {'form': form})


# ==========================================
# EDICIÓN DE REGISTROS
# ==========================================

@login_required(login_url='/accounts/login/')
def editar_cliente(request, pk):
    
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Cliente actualizado exitosamente.")
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'gestion/form_cliente.html', {'form': form})


@login_required(login_url='/accounts/login/')
def editar_conductor(request, pk):
    
    conductor = get_object_or_404(Conductor, pk=pk)
    
    if request.method == 'POST':
        form = ConductorForm(request.POST, instance=conductor)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Conductor actualizado exitosamente.")
            return redirect('listar_conductores')
    else:
        form = ConductorForm(instance=conductor)
    return render(request, 'gestion/form_conductor.html', {'form': form})


@login_required(login_url='/accounts/login/')
def editar_vehiculo(request, pk):
   
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Vehículo actualizado exitosamente.")
            return redirect('listar_vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'gestion/form_vehiculo.html', {'form': form})


@login_required(login_url='/accounts/login/')
def editar_viaje(request, pk):
    
    viaje = get_object_or_404(Viaje, pk=pk)
    
    if request.method == 'POST':
        form = ViajeForm(request.POST, instance=viaje)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Viaje actualizado exitosamente.")
            return redirect('listar_viajes')
    else:
        form = ViajeForm(instance=viaje)
    return render(request, 'gestion/form_viaje.html', {'form': form})


@login_required(login_url='/accounts/login/')
def editar_pago(request: HttpRequest, pk):
    
    pago = get_object_or_404(Pago, pk=pk)
    
    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Pago actualizado exitosamente.")
            return redirect('listar_pagos')
    else:
        form = PagoForm(instance=pago)

    return render(request, 'gestion/form_pago.html', {'form': form})


@login_required(login_url='/accounts/login/')
def editar_mantencion(request, pk):
    
    mantencion = get_object_or_404(Mantencion, pk=pk)
    
    if request.method == 'POST':
        form = MantencionForm(request.POST, instance=mantencion)
        
        if form.is_valid():

            form.save()
            messages.success(request, "Mantención actualizada exitosamente.")
            return redirect('listar_mantenciones')
    else:
        form = MantencionForm(instance=mantencion)
    return render(request, 'gestion/form_mantencion.html', {'form': form})

# ==========================================
# ELIMINACIÓN DE REGISTROS (con confirmación)
# ==========================================

def _confirmar_eliminacion(request: HttpRequest, objeto, tipo, seccion, url_listado, mensaje_ok, relacionados="") -> HttpResponseRedirect | HttpResponse:

    """GET muestra la pantalla de confirmación; POST elimina el registro."""
    if request.method == 'POST':
        objeto.delete()
        messages.success(request, mensaje_ok)
        return redirect(url_listado)
    
    return render(request, 'gestion/confirmar_eliminar.html', {
        'objeto': objeto,
        'tipo': tipo,
        'seccion': seccion,
        'volver_url': reverse(url_listado),
        'relacionados': relacionados,
    })


def _texto_relacionados(**conteos):

    """Ej: viajes=3, pagos=1 -> '3 viajes y 1 pagos' (solo los que tienen registros)."""
    return " y ".join(f"{n} {nombre}" for nombre, n in conteos.items() if n)


@login_required(login_url='/accounts/login/')
def eliminar_vehiculo(request: HttpRequest, pk) -> HttpResponseRedirect | HttpResponse:

    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    relacionados = _texto_relacionados(
        viajes=vehiculo.viaje_set.count(),
        pagos=Pago.objects.filter(id_viaje__id_vehiculo=vehiculo).count(),
        mantenciones=vehiculo.mantencion_set.count(),
    )
    return _confirmar_eliminacion(request, vehiculo, "vehículo", "Vehículos",
                                  'listar_vehiculos', "Vehículo eliminado.", relacionados)


@login_required(login_url='/accounts/login/')
def eliminar_viaje(request: HttpRequest, pk) -> HttpResponseRedirect | HttpResponse:

    viaje = get_object_or_404(Viaje, pk=pk)
    relacionados = _texto_relacionados(pagos=viaje.pago_set.count())
    return _confirmar_eliminacion(request, viaje, "viaje", "Viajes",
                                  'listar_viajes', "Viaje eliminado.", relacionados)


@login_required(login_url='/accounts/login/')
def eliminar_pago(request: HttpRequest, pk) -> HttpResponseRedirect | HttpResponse:

    pago = get_object_or_404(Pago, pk=pk)
    return _confirmar_eliminacion(request, pago, "pago", "Pagos",
                                  'listar_pagos', "Pago eliminado.")


@login_required(login_url='/accounts/login/')
def eliminar_mantencion(request: HttpRequest, pk) -> HttpResponseRedirect | HttpResponse:

    mantencion = get_object_or_404(Mantencion, pk=pk)
    return _confirmar_eliminacion(request, mantencion, "mantención", "Mantenciones",
                                  'listar_mantenciones', "Mantención eliminada.")