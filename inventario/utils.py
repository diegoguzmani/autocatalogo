from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from decimal import Decimal

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