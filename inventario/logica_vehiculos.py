import pandas as pd
import os
from django.conf import settings
from .models import Vehiculo

def cargar_base_datos_vehiculos():
    # 1. Ruta del archivo
    ruta_archivo = os.path.join(settings.BASE_DIR, 'documentos', 'vehiculos.xlsx')
    
    if not os.path.exists(ruta_archivo):
        return "ERROR: No se encuentra el archivo 'documentos/vehiculos.xlsx'."

    try:
        # 2. Leer Excel
        df = pd.read_excel(ruta_archivo)
        
        # Limpiar espacios en nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Rellenar celdas vacías con string vacío para evitar errores de 'nan'
        df = df.fillna('')

        nuevos = 0
        actualizados = 0

        for index, row in df.iterrows():
            # --- LIMPIEZA DE DATOS ---
            marca = str(row.get('Marca', '')).strip().upper()
            modelo = str(row.get('Modelo', '')).strip().upper()
            motor = str(row.get('Motor', '')).strip().upper()
            
            # Si no hay marca o modelo, saltamos
            if not marca or not modelo:
                continue

            # Manejo de Años (Excel a veces los lee como float 1999.0)
            def limpiar_anio(valor):
                s_val = str(valor).replace('.0', '').strip()
                return s_val if s_val else '-'

            anio_inicio_str = limpiar_anio(row.get('Año_Inicio', 0))
            anio_fin_str = limpiar_anio(row.get('Año_Fin', '-'))
            
            # Intentar convertir inicio a entero, si falla ponemos 0
            try:
                anio_inicio = int(anio_inicio_str)
            except ValueError:
                anio_inicio = 0

            # --- CAMPOS DE FILTROS ---
            filtros = {
                'filtro_aceite': str(row.get('Filtro_Aceite', '')).strip(),
                'filtro_aire': str(row.get('Filtro_Aire', '')).strip(),
                'filtro_combustible': str(row.get('Filtro_Combustible', '')).strip(),
                'filtro_cabina': str(row.get('Filtro_Cabina', '')).strip(),
            }

            # --- GUARDAR EN BASE DE DATOS ---
            # Buscamos por la combinación única de vehículo
            vehiculo_data = {
                'marca': marca,
                'modelo': modelo,
                'motor': motor,
                'anio_inicio': anio_inicio,
                'anio_fin': anio_fin_str,
            }

            # Si el vehículo existe, actualizamos sus filtros. Si no, lo creamos.
            obj, created = Vehiculo.objects.update_or_create(
                **vehiculo_data, # Desempaqueta marca, modelo, etc como criterios de búsqueda
                defaults=filtros # Estos son los campos que se actualizan/crean
            )

            if created:
                nuevos += 1
            else:
                actualizados += 1
        
        return f"ÉXITO: Vehículos procesados. {nuevos} nuevos, {actualizados} actualizados."

    except Exception as e:
        return f"ERROR CRÍTICO procesando vehículos: {str(e)}"