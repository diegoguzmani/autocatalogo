from django.db import models

# 1. Ponemos Configuración DE PRIMERO para que el Producto pueda leerla
class Configuracion(models.Model):
    tasa_dolar = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    # --- CAMPO NUEVO ---
    tasa_euro = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    # -------------------
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dolar: {self.tasa_dolar} | Euro: {self.tasa_euro}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, primary_key=True)
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
    # Precios
    precio_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_base_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Campo opcional si volvemos a usar existencia
    existencia = models.IntegerField(default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    # --- LA SOLUCIÓN MÁGICA ---
    # Creamos una "propiedad" que calcula el precio automáticamente
    @property
    def precio_en_bs(self):
        # El producto busca la configuración actual él mismo
        config = Configuracion.objects.first()
        tasa = config.tasa_dolar if config else 0
        return self.precio_base_bs * tasa