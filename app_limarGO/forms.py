from django import forms
from .models import Cliente, Conductor, Vehiculo, Viaje, Pago, Mantencion, Usuario

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = '__all__'

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'

class ViajeForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = '__all__'

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'

class MantencionForm(forms.ModelForm):
    class Meta:
        model = Mantencion
        fields = '__all__'