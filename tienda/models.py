# tienda/models.py
from django.db import models # Importa el módulo base de modelos de Django.
from django.contrib.auth.models import User # Importa el modelo de Usuario predeterminado de Django.

# ============ MODELO PERFIL DE USUARIO ============
class PerfilUsuario(models.Model):
    ROLES = (
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente'),
        ('administrador', 'Administrador'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    fecha_contratacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"
    
    # --- INICIO DE CORRECCIÓN ---
    # Los métodos deben ir aquí, al mismo nivel que __str__
    
    # Métodos para verificar roles
    def es_vendedor(self):
        return self.rol == 'vendedor'
    
    def es_gerente(self):
        return self.rol == 'gerente'
    
    def es_administrador(self):
        return self.rol == 'administrador'
    
    def tiene_permiso_lectura(self):
        # Todos pueden leer
        return True
    
    def tiene_permiso_escritura(self):
        # Gerente y Administrador pueden escribir
        return self.rol in ['gerente', 'administrador']
    
    def tiene_permiso_eliminacion(self):
        # Solo Administrador puede eliminar
        return self.rol == 'administrador'
    
    # --- FIN DE CORRECCIÓN ---

    class Meta:
        # La clase Meta solo debe contener opciones del modelo
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        
        # (Los métodos que estaban aquí fueron movidos arriba)


# ============ MODELO CATEGORÍA ============
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

# Modelo 2: Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=150) # Nombre del proveedor.
    contacto = models.CharField(max_length=100, blank=True) # Nombre del contacto, opcional.
    telefono = models.CharField(max_length=15, blank=True) # Número de teléfono, opcional.

    def __str__(self):
        return self.nombre # Representación en string del objeto.

# Modelo 3: Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2) # Campo decimal para el precio (máx. 10 dígitos, 2 decimales).
    stock = models.IntegerField(default=0) # Cantidad en inventario, valor predeterminado 0.
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE) # Relación uno a muchos con Categoria (si se borra la categoría, se borran los productos).
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True) # Relación con Proveedor (opcional, si se borra el proveedor, se establece a NULL).
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='productos_creados') # Usuario que creó el producto (opcional, si se borra el usuario, se establece a NULL).
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación (se establece automáticamente al crear).
    activo = models.BooleanField(default=True) # Campo booleano para eliminación lógica (determina si está activo o desactivado).

    def __str__(self):
        return self.nombre # Representación en string del objeto.

# Modelo 4: Cliente
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_perfil', blank=True, null=True)  # Usuario asociado (opcional para clientes sin login)
    nombre = models.CharField(max_length=100)  # Nombre del cliente
    apellido = models.CharField(max_length=100)  # Apellido del cliente
    email = models.EmailField(max_length=191, unique=True)  # Email único (no puede repetirse) - max 191 para MySQL utf8mb4
    telefono = models.CharField(max_length=15)  # Teléfono del cliente
    direccion = models.TextField()  # Dirección de entrega
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de registro automática
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"  # Muestra nombre completo
    
    # Propiedad que concatena nombre completo
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']  # Ordena por apellido y luego por nombre


# Modelo 5: Venta (Transacción)
class Venta(models.Model):
    TIPOS_VENTA = (
        ('venta', 'Venta'),
        ('devolucion', 'Devolución'),
    )

    fecha_venta = models.DateTimeField(auto_now_add=True) # Fecha y hora de la venta.
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Total de la venta, calculado automáticamente.
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True) # Cliente asociado (opcional, SET_NULL al eliminar cliente).
    vendido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Usuario que realizó la venta (opcional, SET_NULL al eliminar usuario).
    tipo = models.CharField(max_length=20, choices=TIPOS_VENTA, default='venta') # Tipo de transacción: venta o devolución.

    def __str__(self):
        return f"Venta #{self.id} - Total: {self.total}" # Representación en string con ID y total.

    def calcular_total(self):
        """Calcula el total de la venta basado en los detalles."""
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()

# Modelo 6: Detalle de Venta
class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles') # Relación con Venta.
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) # Producto vendido.
    cantidad = models.IntegerField(default=1) # Cantidad vendida.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio unitario al momento de la venta.
    subtotal = models.DecimalField(max_digits=10, decimal_places=2) # Subtotal (cantidad * precio_unitario).

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Subtotal: {self.subtotal}"

    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar."""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualiza el total de la venta
        self.venta.calcular_total()
