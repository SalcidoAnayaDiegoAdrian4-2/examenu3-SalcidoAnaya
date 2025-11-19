# tienda/urls.py
from django.urls import path # Importa la función path para definir rutas.
from . import views # Importa las vistas de la aplicación actual.
# IMPORTANTE: Se añade RedirectView para redirigir la raíz
from django.views.generic import RedirectView 

urlpatterns = [ # Lista de patrones de URL.
    
    # Autenticación
    path('login/', views.login_view, name='login'), # URL para iniciar sesión.
    path('logout/', views.logout_view, name='logout'), # URL para cerrar sesión.
    
    # --- CORRECCIÓN DE DASHBOARD ---
    # 1. El dashboard ahora vive en /home/
    path('home/', views.home, name='home'), 
    
    # 2. La raíz ('') ahora redirige a /home/
    path('', RedirectView.as_view(url='home/', permanent=True)),
    # --- FIN DE LA CORRECCIÓN ---
    
    # CRUD Productos
    path('productos/', views.producto_lista, name='producto_lista'), # URL para listar productos.
    path('productos/crear/', views.producto_crear, name='producto_crear'), # URL para crear un producto.
    path('productos/editar/<int:pk>/', views.producto_editar, name='producto_editar'), # URL para editar un producto específico (usando su PK).
    path('productos/eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'), # URL para eliminar un producto específico.

    # ============ RUTAS PARA CATEGORÍAS ============
    path('categorias/', views.categoria_lista, name='categoria_lista'),  # Lista todas las categorías
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),  # Crear categoría
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),  # Editar categoría
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),  # Eliminar categoría
    
    # ============ RUTAS PARA PROVEEDORES ============
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),  # Lista todos los proveedores
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),  # Crear proveedor
    path('proveedores/editar/<int:pk>/', views.proveedor_editar, name='proveedor_editar'),  # Editar proveedor
    path('proveedores/eliminar/<int:pk>/', views.proveedor_eliminar, name='proveedor_eliminar'),  # Eliminar proveedor
    
    # ============ RUTAS PARA CLIENTES ============
    path('clientes/', views.cliente_lista, name='cliente_lista'),  # Lista todos los clientes
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),  # Crear cliente
    path('clientes/editar/<int:pk>/', views.cliente_editar, name='cliente_editar'),  # Editar cliente
    path('clientes/eliminar/<int:pk>/', views.cliente_eliminar, name='cliente_eliminar'),  # Eliminar cliente

    # ============ RUTAS PARA REPORTES ============
    path('reportes/productos/', views.reporte_productos, name='reporte_productos'),  # Reporte de productos

    # ============ RUTAS PARA VENTAS ============
    path('ventas/crear/', views.venta_crear, name='venta_crear'),  # Registrar venta
    path('ventas/reporte/', views.reporte_ventas, name='reporte_ventas'),  # Reporte de ventas del día

    # ============ RUTAS PARA CLIENTES LOGUEADOS ============
    path('cliente/perfil/', views.cliente_perfil, name='cliente_perfil'),  # Perfil del cliente
    path('cliente/compras/', views.cliente_compras, name='cliente_compras'),  # Historial de compras del cliente
]