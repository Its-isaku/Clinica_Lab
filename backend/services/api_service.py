import requests
from typing import Dict, List, Optional


class APIException(Exception):
    """Excepción personalizada para errores de API"""
    pass


def obtener_info_codigo_postal(cp: str) -> Dict:
    """
    Consulta la API de Copomex para obtener información del código postal mexicano.
    
    Args:
        cp (str): Código postal de 5 dígitos
    
    Returns:
        dict: Diccionario con colonias, municipio y estado
        
        Ejemplo de retorno:
        {
            'colonias': ['Centro', 'Zona Norte', 'Hidalgo'],
            'municipio': 'Tijuana',
            'estado': 'Baja California'
        }
        
    Raises:
        APIException: Si el código postal es inválido o no se encuentra
    
    Ejemplo de uso:
        >>> info = obtener_info_codigo_postal('22000')
        >>> print(info['municipio'])
        Tijuana
    """
    
    # Validar formato de CP
    if not cp or len(cp) != 5 or not cp.isdigit():
        raise APIException(f"Código postal inválido: {cp}. Debe ser de 5 dígitos.")
    
    # Construir URL
    url = f"https://api.copomex.com/query/info_cp/{cp}?token=pruebas"
    
    try:
        # Hacer request con timeout de 5 segundos
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lanza error si status != 200
        data = response.json()
        
        # La API puede retornar lista directamente o diccionario con 'error'
        # Si es diccionario y tiene error
        if isinstance(data, dict) and (data.get('error') or not data.get('response')):
            raise APIException(f"Código postal no encontrado: {cp}")
        
        # Si es lista vacía
        if isinstance(data, list) and len(data) == 0:
            raise APIException(f"Código postal no encontrado: {cp}")
        
        # Extraer información
        colonias = []
        municipio = ''
        estado = ''
        
        # Si la respuesta es una lista directamente (formato común de Copomex)
        if isinstance(data, list):
            colonias_data = data
            if colonias_data and len(colonias_data) > 0:
                primer_colonia = colonias_data[0]
                municipio = primer_colonia.get('response', {}).get('municipio', '')
                estado = primer_colonia.get('response', {}).get('estado', '')
                
                # Extraer nombres de colonias
                colonias = [item.get('response', {}).get('asentamiento', '') 
                        for item in colonias_data]
        
        # Si la respuesta es un diccionario con 'response'
        elif isinstance(data, dict) and 'response' in data:
            # Extraer colonias
            if 'colonia' in data['response']:
                colonias = [col for col in data['response']['colonia']]
            
            # Extraer municipio y estado (es el mismo para todas las colonias)
            if colonias and len(colonias) > 0:
                primer_colonia = colonias[0]
                municipio = primer_colonia.get('municipio', '')
                estado = primer_colonia.get('estado', '')
            
            # Extraer solo los nombres de las colonias
            colonias = [col.get('nombre', col) if isinstance(col, dict) else col 
                       for col in colonias]
        
        return {
            'colonias': colonias,
            'municipio': municipio,
            'estado': estado
        }
    
    except requests.Timeout:
        raise APIException("Timeout al consultar API de códigos postales. Intenta de nuevo.")
    
    except requests.RequestException as e:
        raise APIException(f"Error al consultar API: {str(e)}")


# ========== FUNCIÓN DE PRUEBA ==========
if __name__ == '__main__':
    """
    Prueba el servicio con códigos postales de México
    """
    print("📮 PROBANDO API DE CÓDIGOS POSTALES\n")
    
    # Códigos postales de prueba
    codigos_prueba = [
        '22000',  # Tijuana, Baja California
        '64000',  # Monterrey, Nuevo León
        '06000',  # Ciudad de México
        '44100',  # Guadalajara, Jalisco
        '12345',  # Código inválido (para probar error)
    ]
    
    for cp in codigos_prueba:
        print(f"{'='*60}")
        print(f"Código Postal: {cp}")
        print(f"{'='*60}")
        
        try:
            info = obtener_info_codigo_postal(cp)
            
            print(f"✓ Estado: {info['estado']}")
            print(f"✓ Municipio: {info['municipio']}")
            print(f"✓ Colonias encontradas: {len(info['colonias'])}")
            
            # Mostrar primeras 5 colonias
            if info['colonias']:
                print(f"\n📍 Primeras colonias:")
                for i, colonia in enumerate(info['colonias'][:5], 1):
                    print(f"   {i}. {colonia}")
                
                if len(info['colonias']) > 5:
                    print(f"   ... y {len(info['colonias']) - 5} colonias más")
            
        except APIException as e:
            print(f"✗ Error: {e}")
        
        print()