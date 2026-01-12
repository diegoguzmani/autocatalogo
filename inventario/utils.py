from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from decimal import Decimal
import re

def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/glosario/cambio-oficial"
    tasas = {'dolar': Decimal(0), 'euro': Decimal(0)}
    
    try:
        response = curl_requests.get(url, verify=False, impersonate="chrome")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar Dólar
        div_dolar = soup.find('div', id='dolar')
        if div_dolar and div_dolar.find('strong'):
            texto = div_dolar.find('strong').get_text(strip=True).replace(',', '.')
            tasas['dolar'] = Decimal(texto)

        # Buscar Euro
        div_euro = soup.find('div', id='euro')
        if div_euro and div_euro.find('strong'):
            texto = div_euro.find('strong').get_text(strip=True).replace(',', '.')
            tasas['euro'] = Decimal(texto)
            
        return tasas

    except Exception as e:
        print(f"Error BCV: {e}")
        return None

def extraer_numero_filtro(codigo_completo):
    """
    Convierte 'ML-3593' o 'PH3593' en '3593'.
    Elimina letras y guiones, dejando la secuencia numérica principal.
    """
    if not codigo_completo:
        return ""
    
    # Expresión regular: Busca todos los números
    # Ejemplo: "ML-3593" -> "3593"
    numeros = re.findall(r'\d+', str(codigo_completo))
    
    if numeros:
        # Devolvemos el grupo numérico más largo (por si hay códigos tipo A1-555)
        return max(numeros, key=len)
    return ""