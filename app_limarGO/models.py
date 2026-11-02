from django.db import models
from decimal import Decimal

# Tarifa que se cobra por kilómetro recorrido (ida + vuelta)
TARIFA_POR_KM = Decimal(900)


class Usuario(models.Model):

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    rol = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Usuarios'


class Cliente(models.Model):

    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    frecuencia = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Clientes'


class Conductor(models.Model):

    id_conductor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    tipo = models.CharField(max_length=20, blank=True)  # Fijo o Externo
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Conductores'


class Vehiculo(models.Model):

    id_vehiculo = models.AutoField(primary_key=True)
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=50, blank=True)
    km_actual = models.DecimalField(default=Decimal(0))
    estado = models.CharField(max_length=20, default='Activo')

    def __str__(self):
        detalle = f"{self.marca} {self.modelo}".strip()
        return f"{self.patente} - {detalle}" if detalle else self.patente

    class Meta:
        db_table = 'Vehiculos'


class Viaje(models.Model):

    id_viaje = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    id_conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, db_column='id_conductor')
    id_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, db_column='id_vehiculo')
    fecha = models.DateField()
    hora = models.TimeField()
    destino = models.CharField(max_length=200, blank=True)
    km_ida = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    km_vuelta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    estado = models.CharField(max_length=20, default='Programado')

    def save(self, *args, **kwargs):
        # El costo siempre se calcula a partir de los kilómetros
        self.costo = (self.km_ida + self.km_vuelta) * TARIFA_POR_KM
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.id_viaje} - {self.fecha:%d/%m/%Y} - {self.id_cliente.nombre} - {self.destino}"

    class Meta:
        db_table = 'Viajes'


class Pago(models.Model):

    id_pago = models.AutoField(primary_key=True)
    id_viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, db_column='id_viaje')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(null=True, blank=True)
    metodo = models.CharField(max_length=30, blank=True)
    estado = models.CharField(max_length=20, default='Pendiente')

    def __str__(self):
        return f"Pago #{self.id_pago} - ${self.monto:,.0f}"

    class Meta:
        db_table = 'Pagos'


class Mantencion(models.Model):

    id_mantencion = models.AutoField(primary_key=True)
    id_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, db_column='id_vehiculo')
    fecha = models.DateField()
    km_mantencion = models.IntegerField(null=True, blank=True)
    piezas_cambiadas = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Mantención #{self.id_mantencion} - {self.id_vehiculo.patente} - {self.fecha:%d/%m/%Y}"

    class Meta:
        db_table = 'Mantenciones'