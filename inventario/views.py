# inventario/views.py
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Producto, Configuracion
from .forms import TasaForm
from .logica_excel import procesar_excel
from .utils import obtener_tasa_bcv, es_superuser
from .models import Vehiculo # Importa el nuevo modelo
from .utils import extraer_numero_filtro
from .logica_vehiculos import cargar_base_datos_vehiculos  # <--- AGREGAR ESTO

@login_required
def buscador_vehiculos(request):
    config, _ = Configuracion.objects.get_or_create(id=1)
    
    # 1. Obtener listas para los Selects (Marcas disponibles)
    marcas = Vehiculo.objects.values_list('marca', flat=True).distinct().order_by('marca')
    
    resultados_aceite = []
    resultados_aire = []
    vehiculo_seleccionado = None

    if request.method == 'GET' and 'vehiculo_id' in request.GET:
        vehiculo_id = request.GET.get('vehiculo_id')
        if vehiculo_id:
            vehiculo_seleccionado = Vehiculo.objects.get(id=vehiculo_id)
            
            # --- BUSCAR FILTRO DE ACEITE ---
            if vehiculo_seleccionado.filtro_aceite:
                clave = extraer_numero_filtro(vehiculo_seleccionado.filtro_aceite)
                # Buscamos en tu inventario productos que contengan ese número (ej: 3593)
                # Y que sean de la categoría Filtros (opcional, si quieres ser estricto)
                if clave:
                    resultados_aceite = Producto.objects.filter(
                        Q(codigo__icontains=clave) | Q(nombre__icontains=clave)
                    )

            # --- BUSCAR FILTRO DE AIRE ---
            if vehiculo_seleccionado.filtro_aire:
                clave = extraer_numero_filtro(vehiculo_seleccionado.filtro_aire)
                if clave:
                    resultados_aire = Producto.objects.filter(
                        Q(codigo__icontains=clave) | Q(nombre__icontains=clave)
                    )

    return render(request, 'inventario/buscador_vehiculos.html', {
        'marcas': marcas,
        'vehiculo': vehiculo_seleccionado,
        'filtros_aceite': resultados_aceite,
        'filtros_aire': resultados_aire,
        'config': config
    })

# API PEQUEÑA PARA LLENAR LOS COMBOS CON JAVASCRIPT
from django.http import JsonResponse
def api_modelos(request):
    marca = request.GET.get('marca')
    modelos = Vehiculo.objects.filter(marca=marca).values('id', 'modelo', 'motor', 'anio_inicio', 'anio_fin').order_by('modelo')
    return JsonResponse(list(modelos), safe=False)

# inventario/views.py
@login_required
def lista_precios(request):
    config, _ = Configuracion.objects.get_or_create(id=1)
    
    # Lógica del botón BCV (se mantiene igual)
    if request.method == 'POST' and 'btn_actualizar_bcv' in request.POST:
        tasas_nuevas = obtener_tasa_bcv()
        
        if tasas_nuevas and tasas_nuevas['dolar'] > 0:
            config.tasa_dolar = tasas_nuevas['dolar']
            config.tasa_euro = tasas_nuevas['euro'] # Guardamos el Euro
            config.save()
            messages.success(request, f"Tasas actualizadas: $ {config.tasa_dolar} | € {config.tasa_euro}")
        else:
            messages.error(request, "Error conectando con el BCV.")
        return redirect('inicio')

    # --- NUEVO BUSCADOR INTELIGENTE ---
    query = request.GET.get('q')
    productos = Producto.objects.all()

    if query:
        # 1. Separamos la frase en palabras (ej: "Valvoline 15w40" -> ["Valvoline", "15w40"])
        palabras = query.split()
        
        # 2. Filtramos iterativamente
        for palabra in palabras:
            productos = productos.filter(
                Q(codigo__icontains=palabra) |
                Q(nombre__icontains=palabra) |
                Q(marca__icontains=palabra) |
                Q(categoria__nombre__icontains=palabra)
            )
    else:
        # Si no busca nada, mostramos solo los primeros 20 para no saturar
        productos = productos[:20]

    return render(request, 'inventario/lista.html', {
        'productos': productos,
        'config': config,
        'busqueda': query
    })

@login_required
@user_passes_test(es_superuser)
def panel_carga(request):
    config, _ = Configuracion.objects.get_or_create(id=1)

    if request.method == 'POST':
        
        # --- OPCIÓN 1: TASA MANUAL (ESTO ES LO QUE ESTAMOS ARREGLANDO) ---
        if 'btn_tasa_manual' in request.POST:
            form_tasa = TasaForm(request.POST, instance=config)
            if form_tasa.is_valid():
                form_tasa.save()
                messages.success(request, '✅ Tasas actualizadas manualmente.')
        
        # --- OPCIÓN 2: CARGA EXCEL ---
        elif 'btn_excel_local' in request.POST:
            resultado = procesar_excel()
            if "ERROR" in resultado:
                messages.error(request, resultado)
            else:
                messages.success(request, resultado)

        elif 'btn_carga_vehiculos' in request.POST:
            resultado = cargar_base_datos_vehiculos()
            if "ERROR" in resultado:
                messages.error(request, resultado)
            else:
                messages.success(request, resultado)
        
        # --- OPCIÓN 3: ACTUALIZAR AUTO (Opcional) ---
        elif 'btn_actualizar_bcv' in request.POST:
            # (Tu código de scraping aquí...)
            pass

        return redirect('panel_carga')

    else:
        # Cargamos el formulario con los datos actuales
        form_tasa = TasaForm(instance=config)

    return render(request, 'inventario/carga.html', {
        'form_tasa': form_tasa,
        'tasa_actual': config.tasa_dolar
    })

@login_required
def calculadora_divisas(request):
    # Obtenemos las tasas
    config, _ = Configuracion.objects.get_or_create(id=1)
    
    return render(request, 'inventario/calculadora.html', {
        'config': config
    })