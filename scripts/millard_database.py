import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from urllib.parse import quote

# --- CONFIGURACIÓN ---
BASE_URL = "https://www.millardcatalog.com"
URL_INICIAL = "https://www.millardcatalog.com/es/applications/Venezuela"
CARPETA_IMAGENES = "imagenes_filtros"
ARCHIVO_SALIDA = "catalogo_millard_venezuela_completo.xlsx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": URL_INICIAL
}

# --- FUNCIONES ---

def obtener_marcas_dinamicas():
    print("Conectando con Millard para obtener lista de marcas...")
    try:
        resp = requests.get(URL_INICIAL, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Buscamos el select oculto de marcas
        select_marcas = soup.find('select', {'id': 'ap_selbrand'})
        lista_marcas = []
        
        if select_marcas:
            opciones = select_marcas.find_all('option')
            for opt in opciones:
                texto = opt.text.strip()
                val = opt.get('value')
                # Filtramos vacíos y el texto de instrucción
                if texto and "Seleccione" not in texto and val:
                    lista_marcas.append(texto)
                    
        lista_marcas = sorted(list(set(lista_marcas)))
        print(f"¡Éxito! Se encontraron {len(lista_marcas)} marcas.")
        return lista_marcas

    except Exception as e:
        print(f"Error fatal obteniendo marcas: {e}")
        return []

def limpiar_texto(texto):
    if texto:
        return texto.strip().replace('\n', '').replace('\t', '')
    return ""

def descargar_imagen(url_relativa, nombre_filtro):
    if not url_relativa: return "Sin Imagen"
    
    if not os.path.exists(CARPETA_IMAGENES):
        os.makedirs(CARPETA_IMAGENES)

    url_completa = f"{BASE_URL}/{url_relativa}"
    nombre_archivo = f"{nombre_filtro}.jpg"
    ruta_archivo = os.path.join(CARPETA_IMAGENES, nombre_archivo)
    
    if os.path.exists(ruta_archivo):
        return nombre_archivo

    try:
        r = requests.get(url_completa, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            with open(ruta_archivo, 'wb') as f:
                f.write(r.content)
            return nombre_archivo
    except:
        pass
    return "Error Descarga"

# --- BLOQUE PRINCIPAL ---

def main():
    datos_totales = []
    
    marcas = obtener_marcas_dinamicas()
    
    if not marcas:
        return

    # marcas = ["HONDA", "CHEVROLET"] # Descomenta esto para probar solo con Honda

    for marca in marcas:
        print(f">>> Procesando Marca: {marca}")
        
        marca_encoded = quote(marca)
        url_marca = f"{BASE_URL}/es/applications/Venezuela/{marca_encoded}/allSeries"
        
        try:
            resp = requests.get(url_marca, headers=HEADERS)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # --- CORRECCIÓN AQUÍ ---
            # Buscamos el SELECT real (ap_selmodel) en lugar del dropdown visual
            select_modelos = soup.find('select', {'id': 'ap_selmodel'})
            
            nombres_modelos = []
            
            if select_modelos:
                opciones = select_modelos.find_all('option')
                for opt in opciones:
                    txt = limpiar_texto(opt.text)
                    # Filtramos "Seleccione..." y aseguramos que tenga texto
                    if txt and "Seleccione" not in txt:
                        nombres_modelos.append(txt)
            else:
                # Debug por si acaso falla
                print(f"    [AVISO] No se encontró el selector 'ap_selmodel' para {marca}")
            
            nombres_modelos = list(set(nombres_modelos))
            print(f"    Encontrados {len(nombres_modelos)} modelos.")

            for modelo in nombres_modelos:
                modelo_encoded = quote(modelo)
                url_modelo = f"{url_marca}/{modelo_encoded}"
                
                # time.sleep(0.1) 
                
                try:
                    r_mod = requests.get(url_modelo, headers=HEADERS)
                    s_mod = BeautifulSoup(r_mod.content, 'html.parser')
                    
                    tabla = s_mod.find('table', {'class': 'table-applications'})
                    if not tabla: continue
                        
                    filas = tabla.find('tbody').find_all('tr')
                    
                    for fila in filas:
                        cols = fila.find_all('td')
                        if len(cols) < 5: continue
                        
                        motor = limpiar_texto(cols[0].text)
                        desde = limpiar_texto(cols[4].text)
                        hasta = limpiar_texto(cols[5].text)
                        
                        def get_dat(idx, prefijo):
                            if idx >= len(cols): return "", ""
                            celda = cols[idx]
                            link = celda.find('a')
                            if not link: return "", ""
                            
                            span = celda.find('span', style=lambda s: s and 'font-size: 10pt' in s)
                            if span: code = span.text.strip()
                            else: code = link.text.replace(prefijo, '').replace('-', '').strip()
                            
                            img_tag = link.find('img')
                            img = img_tag['src'] if img_tag else ""
                            return code, img

                        ml_code, ml_img = get_dat(6, "ML")
                        mf_code, mf_img = get_dat(7, "MF")
                        mk_code, mk_img = get_dat(8, "MK")
                        mc_code, mc_img = get_dat(9, "MC")

                        f_ml = descargar_imagen(ml_img, f"ML-{ml_code}") if ml_code else ""
                        f_mf = descargar_imagen(mf_img, f"MF-{mf_code}") if mf_code else ""
                        f_mk = descargar_imagen(mk_img, f"MK-{mk_code}") if mk_code else ""
                        f_mc = descargar_imagen(mc_img, f"MC-{mc_code}") if mc_code else ""

                        datos_totales.append({
                            "Marca": marca,
                            "Modelo": modelo,
                            "Motor": motor,
                            "Año_Inicio": desde,
                            "Año_Fin": hasta,
                            "Filtro_Aceite": f"ML-{ml_code}" if ml_code else "",
                            "Img_Aceite": f_ml,
                            "Filtro_Aire": f"MK-{mk_code}" if mk_code else "",
                            "Img_Aire": f_mk,
                            "Filtro_Combustible": f"MF-{mf_code}" if mf_code else "",
                            "Img_Combustible": f_mf,
                            "Filtro_Cabina": f"MC-{mc_code}" if mc_code else "",
                            "Img_Cabina": f_mc
                        })
                        
                except Exception as e:
                    print(f"    Error en modelo {modelo}: {e}")

        except Exception as e:
            print(f"Error en marca {marca}: {e}")
            
        pd.DataFrame(datos_totales).to_excel(ARCHIVO_SALIDA, index=False)

    print("=== PROCESO TERMINADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()