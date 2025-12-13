from django import template

register = template.Library()

@register.filter
def color_marca(valor):
    """
    Recibe el nombre de la marca y devuelve una clase de color de Bootstrap.
    """
    if not valor:
        return 'secondary'
    
    # Lista de colores SOLIDOS y FUERTES.
    # Eliminamos 'light' y 'white' para evitar fondos blancos.
    colores = [
        'primary',      # Azul
        'success',      # Verde
        'danger',       # Rojo
        'warning',      # Amarillo (Requiere texto negro)
        'info',         # Cian (Requiere texto negro)
        'dark',         # Negro
        'secondary',    # Gris Oscuro
    ]
    
    # Algoritmo para elegir color
    suma_letras = sum(ord(letra) for letra in str(valor))
    indice = suma_letras % len(colores)
    
    return colores[indice]

@register.filter
def texto_color(bg_class):
    """
    Define el color de la letra según el fondo.
    """
    # Si el fondo es Amarillo (warning) o Cian (info), la letra DEBE ser negra.
    colores_claros = ['warning', 'info']
    
    if bg_class in colores_claros:
        return 'text-dark' # Letras negras
    
    # Para Azul, Rojo, Verde, Negro y Gris, la letra blanca se ve bien.
    return 'text-white'

@register.filter
def formato_ve(valor):
    """
    Convierte un número a formato venezolano:
    Ejemplo: 1455.99 -> 1.455,99
    """
    try:
        valor = float(valor)
        # Primero formateamos estilo gringo: 1,455.99
        texto = "{:,.2f}".format(valor)
        
        # Hacemos el truco de cambiar los signos
        # 1. La coma de miles (,) la volvemos un guion bajo temporal (_)
        # 2. El punto decimal (.) lo volvemos coma (,)
        # 3. El guion bajo (_) lo volvemos punto (.)
        return texto.replace(',', '_').replace('.', ',').replace('_', '.')
    except (ValueError, TypeError):
        return valor
    
@register.filter
def es_aceite_litro(nombre_producto):
    """
    Detecta si es aceite buscando:
    1. Que tenga indicación de viscosidad (W) Y indicación de litro (LT, LITRO, 1L).
    2. O palabras clave específicas.
    """
    nombre = nombre_producto.upper()
    
    # Palabras que indican volumen de 1 litro
    indicadores_litro = ["LT", "LITRO", "1L", "1 L"]
    
    # Palabras que indican aceite de motor
    indicadores_tipo = ["MINERAL", "SINTETICO", "SEMISINTETICO", "SEMI-SINTETICO", "SEMI SINTETICO" "20W50", "15W40", "10W30", "10W40", "5W30", "5W40", "25W60"]

    # Lógica: Debe tener al menos UN indicador de litro Y al menos UN indicador de tipo
    tiene_litro = any(i in nombre for i in indicadores_litro)
    tiene_tipo = any(i in nombre for i in indicadores_tipo)

    return tiene_litro and tiene_tipo