import pandas as pd
import os
from django.conf import settings
from .models import Producto, Categoria

def procesar_excel():
    ruta_archivo = os.path.join(settings.BASE_DIR, 'documentos', 'lista_precios.xlsx')
    
    if not os.path.exists(ruta_archivo):
        return "ERROR: No se encuentra el archivo en 'documentos/lista_precios.xlsx'."

    try:
        # 1. Leer el Excel
        df = pd.read_excel(ruta_archivo)
        
        # Limpiar nombres de columnas (elimina espacios al principio o final de los títulos)
        df.columns = df.columns.str.strip()

        # Usaremos una categoría por defecto ya que no está en tu nuevo Excel
        categoria_general, _ = Categoria.objects.get_or_create(nombre="GENERAL")

        nuevos = 0
        actualizados = 0

        for index, row in df.iterrows():
            # Obtener y limpiar el código
            codigo = str(row.get('Código', '')).strip()
            
            # Saltamos filas vacías o si el código es el título
            if not codigo or codigo.lower() == 'nan' or codigo == 'Código':
                continue

            # --- CONVERSIÓN DE PRECIOS ---
            def limpiar_monto(valor):
                if pd.isna(valor): return 0.0
                # Quitamos símbolos de moneda, comas y espacios por si acaso
                s = str(valor).replace('$', '').replace('Bs', '').replace(',', '').strip()
                try:
                    return float(s)
                except ValueError:
                    return 0.0

            precio_cash = limpiar_monto(row.get('Precio $', 0))
            precio_bs_ref = limpiar_monto(row.get('Precio BS', 0))

            # --- GUARDAR EN BASE DE DATOS ---
            # Nota: Como tu Excel nuevo no tiene 'Existencia', 
            # el sistema mantendrá la que ya tenga o pondrá 0 si es nuevo.
            
            defaults = {
                'nombre': str(row.get('Descripcion', '')).strip(),
                'marca': str(row.get('Marca', '')).strip(),
                'categoria': categoria_general,
                'precio_cash': precio_cash,
                'precio_base_bs': precio_bs_ref,
            }

            obj, created = Producto.objects.update_or_create(
                codigo=codigo,
                defaults=defaults
            )

            if created:
                nuevos += 1
            else:
                actualizados += 1
        
        return f"ÉXITO: Se procesó la lista. {nuevos} nuevos, {actualizados} actualizados."

    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"