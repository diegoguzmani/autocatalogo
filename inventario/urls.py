# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_precios, name='inicio'),
    path('calculadora/', views.calculadora_divisas, name='calculadora'), # <--- NUEVA
    path('admin-panel/', views.panel_carga, name='panel_carga'),
    path('buscador-vehiculos/', views.buscador_vehiculos, name='buscador_vehiculos'),
    path('api/modelos/', views.api_modelos, name='api_modelos'),
]