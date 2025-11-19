from django.shortcuts import render, redirect, get_object_or_404 # Funciones comunes para renderizar, redirigir y obtener objetos.
from django.contrib.auth.decorators import login_required, permission_required # Decoradores para requerir autenticación y permisos.
from django.urls import reverse_lazy # Función para obtener URLs de forma perezosa.
from django.contrib.auth.models import Group # Modelo para gestionar grupos/roles de usuarios.
from django.contrib import messages # Módulo para enviar mensajes de notificación al usuario.

# --- INICIO DE CORRECCIONES (IMPORTACIONES) ---

# Importa las funciones de autenticación que estás usando
from django.contrib.auth import authenticate, login, logout
# Importa el formulario de login de Django
from django.contrib.auth.forms import AuthenticationForm 

# Importa TODOS los modelos que usas en tus vistas
from .models import Producto, Categoria, PerfilUsuario, Proveedor, Cliente, Venta, VentaDetalle

# Importa TODOS los formularios que usas en tus vistas
from .forms import ProductoForm, CategoriaForm, ProveedorForm, ClienteForm, ClientePerfilForm, VentaForm, VentaDetalleForm

# Importaciones adicionales para ventas
from django.utils import timezone
from django.utils.formats import date_format
from django.db.models import Sum, Count, Value
from django.db.models.functions import Concat
import datetime
import json

# Función helper para generar username
def generar_username(nombre, apellido):
    """
    Genera un username basado en el primer nombre y primer apellido.
    Ejemplo: "Said Azael" + "Miranda Salcido" -> "Said Miranda"
    """
    primer_nombre = nombre.split()[0] if nombre else ""
    primer_apellido = apellido.split()[0] if apellido else ""
    return f"{primer_nombre} {primer_apellido}".strip()

# NOTA: Se eliminó la importación de LoginView y LogoutView porque 
# creaste tus propias funciones con esos nombres (login_view, logout_view).

# --- FIN DE CORRECCIONES ---


# ============ DECORADOR PERSONALIZADO PARA PERMISOS POR ROL ============
def rol_requerido(*roles_permitidos):
    """
    Decorador personalizado que verifica si el usuario tiene uno de los roles permitidos.
    
    Uso:
        @rol_requerido('gerente', 'administrador')
        def mi_vista(request):
            ...
    
    Parámetros:
        *roles_permitidos: Lista de roles que pueden acceder a la vista
                         Opciones: 'vendedor', 'gerente', 'administrador'
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder')
                return redirect('login')
            
            # 2. Si es superusuario, permitir acceso siempre
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # 3. Verificar si el usuario tiene perfil con rol asignado
            try:
                perfil = request.user.perfil  # Obtener perfil del usuario
                # 4. Verificar si su rol está en los roles permitidos
                if perfil.rol in roles_permitidos:
                    return view_func(request, *args, **kwargs)  # Permitir acceso
                else:
                    # Mostrar mensaje de error indicando roles necesarios
                    roles_texto = ', '.join([r.capitalize() for r in roles_permitidos])
                    messages.error(request, f'⚠ Acceso denegado. Se requiere rol: {roles_texto}')
                    return redirect('home')  # Redirigir al home
            # (Ahora PerfilUsuario está importado y esto funciona)
            except PerfilUsuario.DoesNotExist:
                # Si el usuario no tiene perfil asignado
                messages.error(request, '⚠ Tu cuenta no tiene un perfil asignado. Contacta al administrador.')
                return redirect('home')
        
        return _wrapped_view
    return decorator


# ============ VISTA DE LOGIN ============
def login_view(request):
    """Vista para el inicio de sesión de usuarios"""
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    # Si el método es POST, procesamos el formulario de login
    if request.method == 'POST':
        # (Ahora AuthenticationForm está importado)
        form = AuthenticationForm(request, data=request.POST)  # Creamos el formulario con los datos enviados
        if form.is_valid():  # Si el formulario es válido
            username = form.cleaned_data.get('username')  # Obtenemos el nombre de usuario
            password = form.cleaned_data.get('password')  # Obtenemos la contraseña
            # (Ahora authenticate está importado)
            user = authenticate(username=username, password=password)  # Autenticamos al usuario
            if user is not None:  # Si la autenticación fue exitosa
                # (Ahora login está importado)
                login(request, user)  # Iniciamos sesión
                messages.success(request, f'Bienvenido {username}!')  # Mensaje de bienvenida
                return redirect('home')  # Redirigimos al home
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')  # Mensaje de error
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')  # Mensaje de error si el formulario no es válido
    else:
        form = AuthenticationForm()  # Si es GET, creamos un formulario vacío
    
    return render(request, 'tienda/login.html', {'form': form})  # Renderizamos el template de login


# ============ VISTA DE LOGOUT ============
def logout_view(request):
    """Vista para cerrar sesión"""
    # (Ahora logout está importado)
    logout(request)  # Cerramos la sesión del usuario
    messages.info(request, 'Sesión cerrada correctamente')  # Mensaje informativo
    return redirect('login')  # Redirigimos al login


# ============ VISTA PRINCIPAL (HOME) ============
@login_required  # Decorador que requiere autenticación para acceder a esta vista
def home(request):
    """Vista principal que muestra el dashboard con estadísticas"""
    # Contamos los registros de cada modelo
    total_productos = Producto.objects.count()  # Cuenta todos los productos
    total_categorias = Categoria.objects.count()  # Cuenta todas las categorías
    # (Ahora Proveedor y Cliente están importados)
    total_proveedores = Proveedor.objects.count()  # Cuenta todos los proveedores
    total_clientes = Cliente.objects.count()  # Cuenta todos los clientes

    # Obtenemos los últimos 5 productos creados
    productos_recientes = Producto.objects.all()[:5]  # Slice de los primeros 5 productos

    # Estadísticas de ventas del día
    hoy = timezone.now().date()  # Fecha actual
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
    total_ventas_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    cantidad_ventas_hoy = ventas_hoy.count()

    # Creamos un diccionario con los datos que enviaremos al template
    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_proveedores': total_proveedores,
        'total_clientes': total_clientes,
        'productos_recientes': productos_recientes,
        'total_ventas_hoy': total_ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'fecha_hoy': hoy,
    }

    return render(request, 'tienda/dashboard.html', context)  # Renderizamos el template con el contexto


# ============ VISTAS CRUD PARA PRODUCTOS ============
# (Estas vistas ya funcionaban porque Producto y ProductoForm estaban importados)
@login_required
def producto_lista(request):
    """Vista que lista todos los productos"""
    productos = Producto.objects.all()  # Obtenemos todos los productos de la base de datos
    return render(request, 'tienda/producto_lista.html', {'productos': productos})  # Renderizamos template con la lista


@login_required
# ---
# --- ⚠ AQUÍ ESTÁ LA CORRECCIÓN ⚠ ---
# ---
# Se añade el decorador para que 'vendedor1' no pueda crear productos
@rol_requerido('gerente', 'administrador')
def producto_crear(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':  # Si se envió el formulario
        form = ProductoForm(request.POST)  # Creamos el formulario con los datos enviados
        if form.is_valid():  # Si el formulario es válido (todos los campos correctos)
            form.save()  # Guardamos el producto en la base de datos
            messages.success(request, 'Producto creado exitosamente')  # Mensaje de éxito
            return redirect('producto_lista')  # Redirigimos a la lista de productos
    else:
        form = ProductoForm()  # Si es GET, creamos un formulario vacío
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Crear'})  # Renderizamos el formulario


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador pueden editar
def producto_editar(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)  # Obtenemos el producto por su ID (Primary Key), si no existe muestra 404
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)  # Creamos el formulario con los datos del producto existente
        if form.is_valid():
            form.save()  # Guardamos los cambios
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)  # Mostramos el formulario con los datos actuales del producto
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')  # Solo Administrador puede eliminar
def producto_eliminar(request, pk):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)  # Obtenemos el producto
    if request.method == 'POST':  # Confirmación de eliminación debe ser POST por seguridad
        producto.delete()  # Eliminamos el producto de la base de datos
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('producto_lista')
    
    return render(request, 'tienda/producto_eliminar.html', {'producto': producto})  # Mostramos página de confirmación


# ============ VISTAS CRUD PARA CATEGORÍAS ============
@login_required
def categoria_lista(request):
    """Vista que lista todas las categorías"""
    categorias = Categoria.objects.all()
    return render(request, 'tienda/categoria_lista.html', {'categorias': categorias})


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador
def categoria_crear(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        # (Ahora CategoriaForm está importado)
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def categoria_editar(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')  # Solo Administrador
def categoria_eliminar(request, pk):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
        return redirect('categoria_lista')
    
    return render(request, 'tienda/categoria_eliminar.html', {'categoria': categoria})


# ============ VISTAS CRUD PARA PROVEEDORES ============
@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')  # Vendedor NO puede ver proveedores
def proveedor_lista(request):
    """Vista que lista todos los proveedores"""
    # (Ahora Proveedor está importado)
    proveedores = Proveedor.objects.all()
    return render(request, 'tienda/proveedor_lista.html', {'proveedores': proveedores})


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador
def proveedor_crear(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        # (Ahora ProveedorForm está importado)
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm()
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def proveedor_editar(request, pk):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')
def proveedor_eliminar(request, pk):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente')
        return redirect('proveedor_lista')
    
    return render(request, 'tienda/proveedor_eliminar.html', {'proveedor': proveedor})


# ============ VISTAS CRUD PARA CLIENTES ============
@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')
def cliente_lista(request):
    """Vista que lista todos los clientes"""
    # (Ahora Cliente está importado)
    clientes = Cliente.objects.all()
    return render(request, 'tienda/cliente_lista.html', {'clientes': clientes})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_crear(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        # (Ahora ClienteForm está importado)
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Crear el cliente
            cliente = form.save()

            # Crear User asociado con password por defecto
            from django.contrib.auth.models import User
            username = generar_username(cliente.nombre, cliente.apellido)  # Usar la nueva función para generar username
            user = User.objects.create_user(
                username=username,
                email=cliente.email,
                password='cliente123',  # Password por defecto
                first_name=cliente.nombre,
                last_name=cliente.apellido
            )

            # Asociar el User al Cliente
            cliente.user = user
            cliente.save()

            # Crear PerfilUsuario con rol 'cliente'
            PerfilUsuario.objects.create(
                user=user,
                rol='cliente'
            )

            messages.success(request, f'Cliente creado exitosamente. Usuario: {cliente.email}, Password: cliente123')
            return redirect('cliente_lista')
    else:
        form = ClienteForm()

    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_editar(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        # Verificar si se presionó el botón de reset contraseña
        if 'reset_password' in request.POST:
            # Solo administradores pueden resetear contraseña
            if request.user.perfil.rol == 'administrador' or request.user.is_superuser:
                user = cliente.user
                user.set_password('cliente123')
                user.save()
                messages.success(request, f'Contraseña reseteada exitosamente para {cliente.nombre} {cliente.apellido}. Nueva contraseña: cliente123')
                return redirect('cliente_editar', pk=pk)
            else:
                messages.error(request, 'No tienes permisos para resetear contraseñas.')
                return redirect('cliente_editar', pk=pk)

        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)

    # Verificar si el usuario actual es administrador para mostrar el botón
    es_admin = request.user.perfil.rol == 'administrador' or request.user.is_superuser

    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Editar', 'es_admin': es_admin})


@login_required
@rol_requerido('administrador')
def cliente_eliminar(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente')
        return redirect('cliente_lista')

    return render(request, 'tienda/cliente_eliminar.html', {'cliente': cliente})


# ============ VISTAS DE REPORTES ============
@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')  # Solo Gerente y Administrador pueden ver reportes
def reporte_ventas_old(request):
    """Vista que muestra el reporte de ventas con detalles de productos vendidos"""
    tipo_filtro = request.GET.get('tipo', '')  # Obtener el filtro de tipo desde GET

    # Filtrar ventas por tipo si se especifica
    if tipo_filtro:
        ventas = Venta.objects.filter(tipo=tipo_filtro).order_by('-fecha_venta')
    else:
        ventas = Venta.objects.all().order_by('-fecha_venta')  # Todas las ventas, ordenadas por fecha descendente

    total_ventas = ventas.count()  # Número total de ventas
    total_ingresos = sum(venta.total for venta in ventas)  # Suma total de ingresos

    # Estadísticas adicionales
    ventas_con_detalles = []
    for venta in ventas:
        detalles = venta.detalles.all()  # Obtener detalles de la venta
        ventas_con_detalles.append({
            'venta': venta,
            'detalles': detalles,
        })

    context = {
        'ventas_con_detalles': ventas_con_detalles,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'tipo_actual': tipo_filtro,  # Pasar el tipo actual al template
        'tipos_venta': Venta.TIPOS_VENTA,  # Pasar las opciones de tipo al template
    }

    return render(request, 'tienda/reporte_ventas.html', context)


@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')  # Solo Gerente y Administrador pueden ver reportes
def reporte_productos(request):
    """Vista que muestra el reporte de productos"""
    productos = Producto.objects.all().order_by('stock')  # Productos ordenados por stock ascendente
    productos_bajo_stock = productos.filter(stock__lt=10)  # Productos con stock menor a 10
    total_productos = productos.count()  # Número total de productos
    productos_activos = productos.filter(activo=True).count()  # Productos activos

    context = {
        'productos': productos,
        'productos_bajo_stock': productos_bajo_stock,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
    }

    return render(request, 'tienda/reporte_productos.html', context)


# ============ VISTAS PARA VENTAS ============
@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')  # Requiere estar autenticado
def venta_crear(request):
    """Vista para registrar una nueva venta"""
    if request.method == 'POST':  # Si se envió el formulario
        form = VentaForm(request.POST)  # Crear formulario con datos POST
        if form.is_valid():  # Validar formulario
            # Crear la venta
            venta = Venta.objects.create(
                cliente=form.cleaned_data['cliente'],
                vendido_por=request.user
            )

            # Crear el detalle de venta
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            precio_unitario = producto.precio_venta  # Tomar precio actual del producto

            VentaDetalle.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )

            # Calcular el total de la venta
            venta.calcular_total()

            messages.success(request, f'Venta registrada exitosamente - Total: ${venta.total}')
            return redirect('reporte_ventas')  # Redirigir al reporte
    else:
        form = VentaForm()  # Formulario vacío

    return render(request, 'tienda/venta_form.html', {'form': form})


@login_required
@rol_requerido('gerente', 'administrador', 'vendedor', 'cliente')
def reporte_ventas(request):
    """Vista del reporte de ventas con filtros por fecha"""
    # Obtener fechas del filtro GET
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    hoy = timezone.now().date()

    # Si no hay fechas, usar hoy por defecto
    if not start_date_str or not end_date_str:
        start_date = end_date = hoy
    else:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = end_date = hoy

    # Filtrar ventas por período
    ventas_periodo = Venta.objects.filter(
        fecha_venta__date__gte=start_date,
        fecha_venta__date__lte=end_date
    ).select_related('cliente', 'vendido_por').prefetch_related('detalles__producto')

    # Si el usuario es cliente, filtrar solo sus ventas
    if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'cliente':
        try:
            cliente = request.user.cliente_perfil
            ventas_periodo = ventas_periodo.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            ventas_periodo = Venta.objects.none()

    # Calcular total de ventas del período
    total_ventas_periodo = ventas_periodo.aggregate(total=Sum('total'))['total'] or 0

    # Contar cantidad de ventas
    cantidad_ventas_periodo = ventas_periodo.count()

    # Calcular promedio por venta
    promedio_venta = total_ventas_periodo / cantidad_ventas_periodo if cantidad_ventas_periodo > 0 else 0

    # Para compatibilidad, mantener total_ventas_dia si es hoy
    if start_date == end_date == hoy:
        total_ventas_dia = total_ventas_periodo
        ventas_hoy = ventas_periodo
        cantidad_ventas = cantidad_ventas_periodo
    else:
        total_ventas_dia = 0
        ventas_hoy = Venta.objects.none()
        cantidad_ventas = 0

    # Top productos (solo para roles no cliente)
    top_productos = []
    productos_labels = []
    productos_data = []
    if hasattr(request.user, 'perfil') and request.user.perfil.rol != 'cliente':
        top_productos = VentaDetalle.objects.filter(
            venta__fecha_venta__date__gte=start_date,
            venta__fecha_venta__date__lte=end_date
        ).values('producto__nombre').annotate(
            total_cantidad=Sum('cantidad')
        ).order_by('-total_cantidad')[:10]

        # Preparar datos para el gráfico
        productos_labels = [p['producto__nombre'] for p in top_productos]
        productos_data = [p['total_cantidad'] for p in top_productos]

    # Clientes frecuentes
    top_clientes = []
    if hasattr(request.user, 'perfil') and request.user.perfil.rol != 'cliente':
        clientes_frecuentes = Venta.objects.filter(
            fecha_venta__date__gte=start_date,
            fecha_venta__date__lte=end_date
        ).annotate(
            nombre_completo=Concat('cliente__nombre', Value(' '), 'cliente__apellido')
        ).values('nombre_completo').annotate(
            total_compras=Count('id')
        ).order_by('-total_compras')[:10]

        top_clientes = list(clientes_frecuentes)

    # Formatear fecha para display usando Django's date_format para localización
    if start_date == end_date:
        fecha_display = date_format(start_date, r'l, j \d\e F \d\e Y')
    else:
        fecha_display = f"Del {date_format(start_date, 'd/m/Y')} al {date_format(end_date, 'd/m/Y')}"

    context = {
        'ventas_hoy': ventas_hoy,
        'ventas_periodo': ventas_periodo,
        'total_ventas_dia': total_ventas_dia,
        'total_ventas_periodo': total_ventas_periodo,
        'cantidad_ventas': cantidad_ventas,
        'cantidad_ventas_periodo': cantidad_ventas_periodo,
        'promedio_venta': promedio_venta,
        'fecha': fecha_display,
        'fecha_start': start_date,
        'fecha_end': end_date,
        'start_date': start_date,
        'end_date': end_date,
        'top_productos': top_productos,
        'top_clientes': top_clientes,
        'productos_labels': productos_labels,
        'productos_data': productos_data,
    }

    return render(request, 'tienda/reporte_ventas.html', context)


# ============ VISTAS PARA CLIENTES LOGUEADOS ============
@login_required
@rol_requerido('cliente')  # Solo usuarios con rol 'cliente' pueden acceder
def cliente_perfil(request):
    """Vista para que el cliente edite su propio perfil"""
    # Obtener el cliente asociado al usuario logueado
    try:
        cliente = request.user.cliente_perfil  # Accede al cliente a través de la relación OneToOne
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado. Contacta al administrador.')
        return redirect('home')

    if request.method == 'POST':
        # Crear formulario con datos del cliente existente
        form = ClientePerfilForm(request.POST, instance=cliente, user=request.user)
        if form.is_valid():
            # Guardar cambios en Cliente
            cliente = form.save()

            # Actualizar User si cambió nombre o apellido
            user = request.user
            user.first_name = cliente.nombre
            user.last_name = cliente.apellido

            # Regenerar username
            user.username = generar_username(cliente.nombre, cliente.apellido)
            user.save()

            # Cambiar contraseña
            password_nueva = form.cleaned_data.get('password_nueva')
            if password_nueva:
                user.set_password(password_nueva)
                user.save()
                # Re-autenticar al usuario después de cambiar contraseña
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('cliente_perfil')
    else:
        form = ClientePerfilForm(instance=cliente, user=request.user)

    return render(request, 'tienda/cliente_perfil.html', {'form': form})


@login_required
@rol_requerido('cliente')  # Solo usuarios con rol 'cliente' pueden acceder
def cliente_compras(request):
    """Vista para que el cliente vea su historial de compras"""
    # Obtener el cliente asociado al usuario logueado
    try:
        cliente = request.user.cliente_perfil  # Accede al cliente a través de la relación OneToOne
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado. Contacta a un gerete o administrador.')
        return redirect('home')

    # Obtener todas las ventas del cliente, ordenadas por fecha descendente
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta').prefetch_related('detalles__producto')

    context = {
        'ventas': ventas,
        'cliente': cliente,
    }

    return render(request, 'tienda/cliente_compras.html', context)


