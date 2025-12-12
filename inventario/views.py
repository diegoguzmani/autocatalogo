# inventario/views.py
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Producto, Configuracion
from .forms import TasaForm
from .logica_excel import procesar_excel
from .utils import obtener_tasa_bcv # Tu script

# inventario/views.py

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

def panel_carga(request):
    config, _ = Configuracion.objects.get_or_create(id=1)

    # CHIVATO 1: Ver si entra a la vista
    print("--- Entrando a la vista panel_carga ---")

    if request.method == 'POST':
        # CHIVATO 2: Ver qué datos envió el formulario
        print("--- Es una solicitud POST ---")
        print("DATOS RECIBIDOS:", request.POST)

        if 'btn_tasa' in request.POST:
            print(">>> Se detectó botón TASA")
            form_tasa = TasaForm(request.POST, instance=config)
            if form_tasa.is_valid():
                form_tasa.save()
                messages.success(request, 'Tasa actualizada manualmente.')

        # AQUI ES DONDE DEBERIA ENTRAR
        elif 'btn_excel_local' in request.POST:
            print(">>> Se detectó botón EXCEL LOCAL. Ejecutando función...")
            resultado = procesar_excel() 
            print(">>> Resultado de la función:", resultado)
            
            if "ERROR" in resultado:
                messages.error(request, resultado)
            else:
                messages.success(request, resultado)
        
        elif 'btn_actualizar_bcv' in request.POST:
            print(">>> Se detectó botón BCV")
            # Logica bcv...
            pass 
        
        else:
            print(">>> ALERTA: Llegó un POST pero no reconozco el botón.")

        return redirect('panel_carga')

    else:
        form_tasa = TasaForm(instance=config)

    return render(request, 'inventario/carga.html', {
        'form_tasa': form_tasa,
        'tasa_actual': config.tasa_dolar
    })

def calculadora_divisas(request):
    # Obtenemos las tasas
    config, _ = Configuracion.objects.get_or_create(id=1)
    
    return render(request, 'inventario/calculadora.html', {
        'config': config
    })