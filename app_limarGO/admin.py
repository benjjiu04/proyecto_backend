from django.contrib import admin
from .models import Usuario, Cliente, Conductor, Vehiculo, Viaje, Pago, Mantencion

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Conductor)
admin.site.register(Vehiculo)
admin.site.register(Viaje)
admin.site.register(Pago)
admin.site.register(Mantencion)