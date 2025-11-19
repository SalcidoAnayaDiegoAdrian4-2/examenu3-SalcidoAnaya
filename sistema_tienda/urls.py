# sistema_tienda/urls.py
from django.contrib import admin # Importa el módulo de administración de Django.
from django.urls import path, include # Importa path y include.

urlpatterns = [
    path('admin/', admin.site.urls), # Mapea la URL '/admin/' al panel de administración de Django.
    path('', include('tienda.urls')), # <-- Incluye todas las URLs definidas en 'tienda/urls.py' bajo la ruta raíz ('/').
]