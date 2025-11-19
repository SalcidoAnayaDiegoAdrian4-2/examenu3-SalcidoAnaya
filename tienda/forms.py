# tienda/forms.py
# Importamos forms de Django para crear formularios
from django import forms
# CORRECCIÓN: Se añade 'Venta' a la importación
from .models import Producto, Categoria, Proveedor, Cliente, Venta, VentaDetalle


# ============ FORMULARIO PARA PRODUCTOS ============
class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos"""
    
    # Meta clase define la configuración del formulario
    class Meta:
        model = Producto  # El modelo que usará este formulario
        
        # CORRECCIÓN: Se cambió 'precio' por 'precio_venta' para coincidir con el models.py
        fields = ['nombre', 'descripcion', 'precio_venta', 'stock', 'categoria', 'proveedor', 'activo']
        
        # Widgets: personalización de cómo se muestran los campos en HTML
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',  # Clase de Bootstrap para estilos
                'placeholder': 'Ingrese el nombre del producto'  # Texto de ayuda en el campo
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # Altura del textarea en filas
                'placeholder': 'Ingrese una descripción del producto'
            }),
            # CORRECCIÓN: El widget debe apuntar a 'precio_venta'
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',  # Permite decimales de 2 dígitos
                'min': '0',  # Valor mínimo
                'placeholder': '0.00'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            # Select para la categoría (combobox con las opciones de categorías)
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            # Select para la categoría (combobox con las opciones de categorías)
            'proveedor': forms.Select(attrs={
                'class': 'form-control'
            }),
            # Checkbox para el campo activo
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        # Labels: etiquetas personalizadas para cada campo
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            # CORRECCIÓN: La etiqueta debe ser para 'precio_venta'
            'precio_venta': 'Precio ($)',
            'stock': 'Cantidad en Stock',
            'categoria': 'Categoría',
            'proveedor': 'Proveedor',
            'activo': '¿Producto Activo?',
        }


# ============ FORMULARIO PARA CATEGORÍAS ============
class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']  # Solo nombre y descripción
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese una descripción (opcional)'
            }),
        }
        
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
        }


# ============ FORMULARIO PARA PROVEEDORES ============
class ProveedorForm(forms.ModelForm):
    """Formulario para crear y editar proveedores"""
    
    class Meta:
        model = Proveedor
        # CORRECCIÓN: Se ajustan los campos a los del modelo: nombre, contacto, telefono
        fields = ['nombre', 'contacto', 'telefono']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa proveedora'
            }),
            # CORRECCIÓN: Se añade el campo 'contacto' que faltaba
            'contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la persona de contacto'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            # CORRECCIÓN: Se eliminan widgets para campos que no existen
            # ('empresa', 'email', 'direccion')
        }
        
        labels = {
            # CORRECCIÓN: Se ajustan las etiquetas a los campos reales
            'nombre': 'Nombre del Proveedor',
            'contacto': 'Persona de Contacto',
            'telefono': 'Teléfono',
        }


# ============ FORMULARIO PARA CLIENTES ============
class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección de entrega'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }


# ============ FORMULARIO PARA PERFIL DE CLIENTE ============
class ClientePerfilForm(forms.ModelForm):
    """Formulario para que el cliente edite su perfil, incluyendo cambio de contraseña"""

    # Campos adicionales para cambio de contraseña
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña actual'
        }),
        label='Contraseña Actual',
        required=False
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nueva contraseña'
        }),
        label='Nueva Contraseña',
        required=False
    )
    password_confirmar = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu nueva contraseña'
        }),
        label='Confirmar Nueva Contraseña',
        required=False
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección de entrega'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmar = cleaned_data.get('password_confirmar')

        # Si se intenta cambiar contraseña, validar
        if password_nueva or password_confirmar:
            if not password_actual:
                raise forms.ValidationError('Debes ingresar tu contraseña actual para cambiarla.')

            if not self.user.check_password(password_actual):
                raise forms.ValidationError('La contraseña actual es incorrecta.')

            if password_nueva != password_confirmar:
                raise forms.ValidationError('Las nuevas contraseñas no coinciden.')

            if len(password_nueva) < 8:
                raise forms.ValidationError('La nueva contraseña debe tener al menos 8 caracteres.')

        return cleaned_data
    

# Formulario de Venta (Simplificado)
class VentaForm(forms.ModelForm):
    # Campos adicionales para el formulario
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Producto'
    )
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '1000'}),
        label='Cantidad'
    )

    class Meta:
        model = Venta  # Esto ahora funciona gracias a la importación corregida
        fields = ['cliente'] # Define los campos esenciales para registrar una venta.

# Formulario para Detalle de Venta
class VentaDetalleForm(forms.ModelForm):
    class Meta:
        model = VentaDetalle
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
