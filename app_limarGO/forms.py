import re
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils import timezone

from .models import (
    Cliente, Conductor, Vehiculo, Viaje, Pago, Mantencion, TARIFA_POR_KM,
)

LETRAS = r"A-Za-zÁÉÍÓÚÜÑáéíóúüñ"


# ==========================================
# FUNCIONES DE VALIDACIÓN REUTILIZABLES
# ==========================================
def limpiar_texto(valor, etiqueta, minimo=3, permitir_numeros=False):
    """Quita espacios sobrantes y valida largo mínimo y caracteres permitidos."""
    valor = re.sub(r"\s+", " ", valor or "").strip()
    if not valor:
        return valor
    if len(valor) < minimo:
        raise ValidationError(f"{etiqueta} debe tener al menos {minimo} caracteres.")
    permitidos = LETRAS + (r"0-9&" if permitir_numeros else "") + r" .,'\-"
    if not re.fullmatch(f"[{permitidos}]+", valor):
        raise ValidationError(f"{etiqueta} contiene caracteres no permitidos.")
    return valor


def limpiar_telefono(valor):
    """Acepta teléfonos chilenos (9 dígitos, con o sin +56) y los deja normalizados."""
    valor = (valor or "").strip()
    if not valor:
        return ""
    digitos = re.sub(r"[\s\-().]", "", valor)
    m = re.fullmatch(r"(?:\+?56)?([2-9]\d{8})", digitos)
    if not m:
        raise ValidationError("Ingresa un teléfono chileno válido, por ejemplo +56 9 1234 5678.")
    n = m.group(1)
    return f"+56 {n[0]} {n[1:5]} {n[5:]}"


def limpiar_rut(valor):
    """Valida el RUT con módulo 11 y lo devuelve con formato 12.345.678-5."""
    rut = re.sub(r"[.\-\s]", "", valor or "").upper()
    if not re.fullmatch(r"\d{7,8}[0-9K]", rut):
        raise ValidationError("Ingresa un RUT válido, por ejemplo 12.345.678-5.")
    cuerpo, dv = rut[:-1], rut[-1]
    suma, factor = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - suma % 11
    esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
    if dv != esperado:
        raise ValidationError("El RUT no es válido: el dígito verificador no coincide.")
    return f"{int(cuerpo):,}".replace(",", ".") + "-" + dv


def limpiar_patente(valor):
    """Patentes chilenas: AA1234 (antigua) o BBBB12 (actual, sin vocales)."""
    patente = re.sub(r"[\s.\-]", "", valor or "").upper()
    antigua = re.fullmatch(r"[A-Z]{2}\d{4}", patente)
    nueva = re.fullmatch(r"[B-DF-HJ-LP-TV-Z]{4}\d{2}", patente)
    if not (antigua or nueva):
        raise ValidationError("Patente inválida. Usa el formato AB1234 o BCDF12.")
    return patente


def clp(numero):
    """Formatea un número como pesos chilenos: 12500 -> $12.500"""
    return "$" + f"{Decimal(numero):,.0f}".replace(",", ".")


# ==========================================
# BASE: estilos y marcado de errores
# ==========================================
class EstiloFormMixin:
    required_css_class = "required"
    error_css_class = "has-error"
    campos_anchos = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, campo in self.fields.items():
            clase = "form-check" if isinstance(campo.widget, forms.CheckboxInput) else "form-control"
            campo.widget.attrs.setdefault("class", clase)
            campo.full_width = isinstance(campo.widget, forms.Textarea) or nombre in self.campos_anchos

    def full_clean(self):
        super().full_clean()
        # Marca como inválidos (aria-invalid) los campos con error para estilos y accesibilidad
        for nombre in (self._errors or {}):
            if nombre in self.fields:
                self.fields[nombre].widget.attrs["aria-invalid"] = "true"


# ==========================================
# CLIENTE
# ==========================================
class ClienteForm(EstiloFormMixin, forms.ModelForm):
    campos_anchos = ("nombre", "direccion")

    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "direccion", "frecuencia"]
        labels = {"frecuencia": "Frecuencia de uso"}
        help_texts = {
            "telefono": "Opcional. Ejemplo: +56 9 1234 5678",
            "frecuencia": "Ejemplo: Semanal, Mensual u Ocasional",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre o razón social", "minlength": 3}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 1234 5678", "inputmode": "tel"}),
            "direccion": forms.TextInput(attrs={"placeholder": "Calle, número y comuna"}),
            "frecuencia": forms.TextInput(attrs={"placeholder": "Semanal"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].required = True

    def clean_nombre(self):
        return limpiar_texto(self.cleaned_data["nombre"], "El nombre", permitir_numeros=True)

    def clean_telefono(self):
        return limpiar_telefono(self.cleaned_data.get("telefono"))

    def clean_direccion(self):
        return re.sub(r"\s+", " ", self.cleaned_data.get("direccion") or "").strip()

    def clean_frecuencia(self):
        return re.sub(r"\s+", " ", self.cleaned_data.get("frecuencia") or "").strip()

    def clean(self):
        datos = super().clean()
        nombre, telefono = datos.get("nombre"), datos.get("telefono")
        if nombre and telefono:
            repetido = (Cliente.objects.filter(nombre__iexact=nombre, telefono=telefono)
                        .exclude(pk=self.instance.pk).exists())
            if repetido:
                raise ValidationError("Ya existe un cliente con el mismo nombre y teléfono.")
        return datos


# ==========================================
# CONDUCTOR
# ==========================================
class ConductorForm(EstiloFormMixin, forms.ModelForm):
    TIPOS = [("", "Selecciona un tipo"), ("Fijo", "Fijo"), ("Externo", "Externo")]
    tipo = forms.ChoiceField(choices=TIPOS, label="Tipo de conductor")
    campos_anchos = ("nombre",)

    class Meta:
        model = Conductor
        fields = ["nombre", "rut", "telefono", "tipo", "activo"]
        labels = {"rut": "RUT", "activo": "Conductor activo"}
        help_texts = {
            "rut": "Con o sin puntos y guion. Se valida el dígito verificador.",
            "telefono": "Opcional. Ejemplo: +56 9 1234 5678",
            "activo": "Solo los conductores activos se pueden asignar a viajes nuevos.",
        }
        error_messages = {"rut": {"unique": "Ya existe un conductor con este RUT."}}
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre completo", "minlength": 3}),
            "rut": forms.TextInput(attrs={"placeholder": "12.345.678-5", "maxlength": 12}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 1234 5678", "inputmode": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].required = True
        self.fields["rut"].required = True

    def clean_nombre(self):
        return limpiar_texto(self.cleaned_data["nombre"], "El nombre")

    def clean_rut(self):
        return limpiar_rut(self.cleaned_data.get("rut"))

    def clean_telefono(self):
        return limpiar_telefono(self.cleaned_data.get("telefono"))


# ==========================================
# VEHÍCULO
# ==========================================
class VehiculoForm(EstiloFormMixin, forms.ModelForm):
    ESTADOS = [("Activo", "Activo"), ("En mantención", "En mantención"), ("Inactivo", "Inactivo")]
    estado = forms.ChoiceField(choices=ESTADOS)

    class Meta:
        model = Vehiculo
        fields = ["patente", "marca", "modelo", "km_actual", "estado"]
        labels = {"km_actual": "Kilometraje actual"}
        help_texts = {
            "patente": "Formato AB1234 o BCDF12.",
            "km_actual": "En kilómetros. No puede ser menor al ya registrado.",
        }
        error_messages = {"patente": {"unique": "Ya existe un vehículo con esta patente."}}
        widgets = {
            "patente": forms.TextInput(attrs={"placeholder": "BCDF12", "maxlength": 8,
                                               "style": "text-transform:uppercase"}),
            "marca": forms.TextInput(attrs={"placeholder": "Toyota"}),
            "modelo": forms.TextInput(attrs={"placeholder": "Hiace"}),
            "km_actual": forms.NumberInput(attrs={"min": 0, "step": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marca"].required = True
        self.fields["modelo"].required = True

    def clean_patente(self):
        return limpiar_patente(self.cleaned_data.get("patente"))

    def clean_marca(self):
        return limpiar_texto(self.cleaned_data["marca"], "La marca", minimo=2, permitir_numeros=True)

    def clean_modelo(self):
        return limpiar_texto(self.cleaned_data["modelo"], "El modelo", minimo=1, permitir_numeros=True)

    def clean_km_actual(self):
        km = self.cleaned_data["km_actual"]
        if km < 0:
            raise ValidationError("El kilometraje no puede ser negativo.")
        if self.instance.pk and km < self.instance.km_actual:
            raise ValidationError(
                f"El kilometraje no puede ser menor al registrado ({self.instance.km_actual} km).")
        return km


# ==========================================
# VIAJE
# ==========================================
class ViajeForm(EstiloFormMixin, forms.ModelForm):
    TARIFA_KM = TARIFA_POR_KM
    ESTADOS = [("Programado", "Programado"), ("En curso", "En curso"),
               ("Completado", "Completado"), ("Cancelado", "Cancelado")]
    estado = forms.ChoiceField(choices=ESTADOS)
    campos_anchos = ("id_cliente", "destino")

    class Meta:
        model = Viaje
        fields = ["id_cliente", "id_conductor", "id_vehiculo", "fecha", "hora",
                  "destino", "km_ida", "km_vuelta", "estado"]
        labels = {
            "id_cliente": "Cliente", "id_conductor": "Conductor", "id_vehiculo": "Vehículo",
            "hora": "Hora de salida", "km_ida": "Kilómetros de ida", "km_vuelta": "Kilómetros de vuelta",
        }
        help_texts = {"km_ida": "El costo se calcula automáticamente según los kilómetros."}
        widgets = {
            "fecha": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "hora": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "destino": forms.TextInput(attrs={"placeholder": "Ciudad o dirección de destino"}),
            "km_ida": forms.NumberInput(attrs={"min": 0, "step": "0.1"}),
            "km_vuelta": forms.NumberInput(attrs={"min": 0, "step": "0.1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destino"].required = True
        self.fields["id_cliente"].empty_label = "Selecciona un cliente"
        self.fields["id_conductor"].empty_label = "Selecciona un conductor"
        self.fields["id_vehiculo"].empty_label = "Selecciona un vehículo"
        # Solo conductores activos y vehículos disponibles (más el ya asignado si se edita)
        self.fields["id_conductor"].queryset = Conductor.objects.filter(
            Q(activo=True) | Q(pk=self.instance.id_conductor_id)).order_by("nombre")
        self.fields["id_vehiculo"].queryset = Vehiculo.objects.filter(
            Q(estado="Activo") | Q(pk=self.instance.id_vehiculo_id)).order_by("patente")

    def clean_destino(self):
        return limpiar_texto(self.cleaned_data["destino"], "El destino", permitir_numeros=True)

    def clean_km_ida(self):
        km = self.cleaned_data["km_ida"]
        if km < 0:
            raise ValidationError("Los kilómetros no pueden ser negativos.")
        return km

    def clean_km_vuelta(self):
        km = self.cleaned_data["km_vuelta"]
        if km < 0:
            raise ValidationError("Los kilómetros no pueden ser negativos.")
        return km

    def clean(self):
        datos = super().clean()
        fecha, hora, estado = datos.get("fecha"), datos.get("hora"), datos.get("estado")
        conductor, vehiculo = datos.get("id_conductor"), datos.get("id_vehiculo")
        ida, vuelta = datos.get("km_ida"), datos.get("km_vuelta")

        if ida is not None and vuelta is not None and ida + vuelta <= 0:
            self.add_error("km_ida", "Indica los kilómetros del viaje (ida o vuelta mayor a 0).")

        # Un viaje pendiente no puede quedar en una fecha pasada
        if fecha and estado in ("Programado", "En curso"):
            es_nuevo_o_cambio = not self.instance.pk or "fecha" in self.changed_data
            if es_nuevo_o_cambio and fecha < timezone.localdate():
                self.add_error("fecha", "La fecha ya pasó. Si el viaje se realizó, cambia el estado a Completado.")

        # Un conductor o vehículo no puede tener dos viajes a la misma fecha y hora
        if fecha and hora and estado != "Cancelado":
            mismos = (Viaje.objects.filter(fecha=fecha, hora=hora)
                      .exclude(estado="Cancelado").exclude(pk=self.instance.pk))
            if conductor and mismos.filter(id_conductor=conductor).exists():
                self.add_error("id_conductor", "Este conductor ya tiene un viaje a esa fecha y hora.")
            if vehiculo and mismos.filter(id_vehiculo=vehiculo).exists():
                self.add_error("id_vehiculo", "Este vehículo ya tiene un viaje a esa fecha y hora.")
        return datos


# ==========================================
# PAGO
# ==========================================
class PagoForm(EstiloFormMixin, forms.ModelForm):
    METODOS = [("", "Selecciona un método"), ("Efectivo", "Efectivo"), ("Transferencia", "Transferencia"),
               ("Tarjeta de débito", "Tarjeta de débito"), ("Tarjeta de crédito", "Tarjeta de crédito")]
    ESTADOS = [("Pendiente", "Pendiente"), ("Pagado", "Pagado"), ("Anulado", "Anulado")]
    metodo = forms.ChoiceField(choices=METODOS, required=False, label="Método de pago")
    estado = forms.ChoiceField(choices=ESTADOS)
    campos_anchos = ("id_viaje",)

    class Meta:
        model = Pago
        fields = ["id_viaje", "monto", "fecha_pago", "metodo", "estado"]
        labels = {"id_viaje": "Viaje", "monto": "Monto (CLP)", "fecha_pago": "Fecha de pago"}
        help_texts = {
            "monto": "No puede superar el saldo pendiente del viaje.",
            "fecha_pago": "Obligatoria si el pago está en estado Pagado.",
        }
        widgets = {
            "monto": forms.NumberInput(attrs={"min": 1, "step": "1", "placeholder": "25000"}),
            "fecha_pago": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_viaje"].empty_label = "Selecciona un viaje"
        self.fields["id_viaje"].queryset = (
            Viaje.objects.select_related("id_cliente")
            .filter(Q(pk=self.instance.id_viaje_id) | ~Q(estado="Cancelado"))
            .order_by("-fecha", "-hora"))
        self.fields["fecha_pago"].widget.attrs["max"] = timezone.localdate().isoformat()

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise ValidationError("El monto debe ser mayor a 0.")
        return monto

    def clean_fecha_pago(self):
        fecha = self.cleaned_data.get("fecha_pago")
        if fecha and fecha > timezone.localdate():
            raise ValidationError("La fecha de pago no puede ser futura.")
        return fecha

    def clean(self):
        datos = super().clean()
        estado, viaje, monto = datos.get("estado"), datos.get("id_viaje"), datos.get("monto")

        if estado == "Pagado":
            if not datos.get("fecha_pago") and "fecha_pago" not in self.errors:
                self.add_error("fecha_pago", "Indica la fecha en que se realizó el pago.")
            if not datos.get("metodo"):
                self.add_error("metodo", "Selecciona el método de pago.")

        if viaje and monto and estado != "Anulado" and viaje.costo > 0:
            pagado = (Pago.objects.filter(id_viaje=viaje).exclude(estado="Anulado")
                      .exclude(pk=self.instance.pk).aggregate(total=Sum("monto"))["total"] or Decimal(0))
            saldo = viaje.costo - pagado
            if monto > saldo:
                self.add_error("monto", f"El monto supera el saldo pendiente del viaje ({clp(max(saldo, 0))}).")
        return datos


# ==========================================
# MANTENCIÓN
# ==========================================
class MantencionForm(EstiloFormMixin, forms.ModelForm):
    campos_anchos = ("id_vehiculo",)

    class Meta:
        model = Mantencion
        fields = ["id_vehiculo", "fecha", "km_mantencion", "piezas_cambiadas", "observaciones"]
        labels = {
            "id_vehiculo": "Vehículo", "km_mantencion": "Kilometraje de la mantención",
            "piezas_cambiadas": "Piezas cambiadas",
        }
        help_texts = {"km_mantencion": "No puede superar el kilometraje actual del vehículo."}
        widgets = {
            "fecha": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "km_mantencion": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "piezas_cambiadas": forms.Textarea(attrs={"rows": 3, "placeholder": "Filtro de aceite, pastillas de freno..."}),
            "observaciones": forms.Textarea(attrs={"rows": 3, "placeholder": "Detalles del trabajo realizado"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_vehiculo"].empty_label = "Selecciona un vehículo"
        self.fields["id_vehiculo"].queryset = Vehiculo.objects.order_by("patente")
        self.fields["fecha"].widget.attrs["max"] = timezone.localdate().isoformat()

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha > timezone.localdate():
            raise ValidationError("La fecha de la mantención no puede ser futura.")
        return fecha

    def clean(self):
        datos = super().clean()
        vehiculo, km = datos.get("id_vehiculo"), datos.get("km_mantencion")
        if km is not None and km < 0:
            self.add_error("km_mantencion", "El kilometraje no puede ser negativo.")
        elif vehiculo and km is not None and km > vehiculo.km_actual:
            self.add_error("km_mantencion",
                           f"No puede superar el kilometraje actual del vehículo ({vehiculo.km_actual} km).")
        if not (datos.get("piezas_cambiadas") or "").strip() and not (datos.get("observaciones") or "").strip():
            raise ValidationError("Indica las piezas cambiadas o agrega una observación.")
        return datos