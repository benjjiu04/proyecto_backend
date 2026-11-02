from typing import Any

from django import forms
from django.forms import ValidationError
from .models import Cliente, Conductor, Vehiculo, Viaje, Pago, Mantencion, Usuario

class ClienteForm(forms.ModelForm):

    def clean_nombre(self):

        usuario: str | None = self.cleaned_data.get("usuario")
        tiene_numeros = 0

        if usuario is not None:

            for char in usuario:
                if char.isdecimal:
                    tiene_numeros += 1
                    
            if tiene_numeros >= 1:
                raise ValidationError("el nombre no puede contener caracteres numericos.")
            
        


    
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