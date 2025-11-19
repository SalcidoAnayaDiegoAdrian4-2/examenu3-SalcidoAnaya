import os
import django

# --- CÓDIGO DE CONEXIÓN DE DJANGO ---
# 1. Ajusta 'sistema_tienda.settings' si el nombre de tu proyecto es otro
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_tienda.settings')
# 2. Carga la configuración de Django
django.setup()
# --- FIN DE LA CONEXIÓN ---

# AHORA sí podemos importar los modelos
from django.contrib.auth.models import User
from tienda.models import PerfilUsuario

# Datos de los usuarios a crear
usuarios_a_crear = [
    {
        'username': 'vendedor1',
        'password': 'vendedor123',
        'email': 'vendedor1@tienda.com',
        'rol': 'vendedor',
        'is_staff': False
    },
    {
        'username': 'gerente1',
        'password': 'gerente123',
        'email': 'gerente1@tienda.com',
        'rol': 'gerente',
        'is_staff': True  # El gerente SÍ puede entrar al /admin
    },
    {
        'username': 'admin1',
        'password': 'admin123',
        'email': 'admin1@tienda.com',
        'rol': 'administrador',
        'is_superuser': True  # 'admin1' será un Superusuario
    },
    {
        'username': 'cliente',
        'password': 'cliente123',
        'email': 'cliente@tienda.com',
        'rol': 'cliente',
        'is_staff': False
    }
]

print("Iniciando la creación de usuarios y perfiles...")

for data in usuarios_a_crear:
    
    username = data['username']
    
    # 1. Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"El usuario '{username}' ya existe. Saltando...")
        continue
    
    try:
        # 2. Crear el Usuario (User)
        if data.get('is_superuser', False):
            # Crear un Superusuario
            user = User.objects.create_superuser(
                username=username,
                email=data['email'],
                password=data['password']
            )
        else:
            # Crear un usuario estándar
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password']
            )
            # Asignar permiso de staff (para 'gerente1')
            user.is_staff = data.get('is_staff', False)
            user.save()

        # 3. Crear el Perfil (PerfilUsuario) y enlazarlo
        PerfilUsuario.objects.create(
            user=user,
            rol=data['rol']
        )
        
        print(f"ÉXITO: Usuario '{username}' (Rol: {data['rol']}) creado.")

    except Exception as e:
        print(f"ERROR al crear a '{username}': {e}")

print("\nProceso finalizado.")