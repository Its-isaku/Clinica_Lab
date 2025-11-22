#? <|------------------- Integración con API externa de códigos postales -------------------|>
"""
* Servicio para consultar códigos postales mexicanos
* 
* Consume la API de Copomex para obtener:
* - Lista de colonias
* - Municipio
* - Estado
* 
* API utilizada: https://api.copomex.com
"""
#! ||------------------- Requiere conexión a internet para funcionar -------------------||

import requests
from typing import Dict, List, Optional
from config import Config


#? <|------------------- Excepción personalizada -------------------|>

class APIException(Exception):
    """
    * Excepción personalizada para errores relacionados con la API externa
    * 
    * Se lanza cuando:
    * - El código postal es inválido
    * - No se encuentra el código postal
    * - La API externa está caída
    * - Hay problemas de conexión
    """
    pass


#? <|------------------- Función principal de consulta -------------------|>

#? <|------------------- Función principal de consulta -------------------|>

def obtener_info_codigo_postal(cp: str) -> Dict:
    """
    * Consulta la API de Copomex para obtener información del código postal mexicano
    * 
    * Proceso:
    * 1. Valida formato del código postal (5 dígitos)
    * 2. Hace request a la API de Copomex
    * 3. Procesa la respuesta (puede venir en diferentes formatos)
    * 4. Extrae colonias, municipio y estado
    * 
    * Args:
    *     cp (str): Código postal de 5 dígitos
    * 
    * Returns:
    *     dict: Diccionario con la información del código postal
    *     
    * Estructura de retorno:
    *     {
    *         'colonias': ['Centro', 'Zona Norte', 'Hidalgo'],
    *         'municipio': 'Tijuana',
    *         'estado': 'Baja California'
    *     }
    *     
    * Raises:
    *     APIException: Si el código postal es inválido, no se encuentra, o hay error de conexión
    * 
    * Ejemplo:
    *     >>> info = obtener_info_codigo_postal('22000')
    *     >>> print(info['municipio'])
    *     Tijuana
    """
    #! ||------------------- Timeout de 5 segundos configurado -------------------||
    #! ||------------------- Validación estricta del formato de CP -------------------||
    if not cp or len(cp) != 5 or not cp.isdigit():
        raise APIException(f"Código postal inválido: {cp}. Debe ser de 5 dígitos.")
    
    #* Construir URL de la API con el código postal y token
    url = f"https://api.copomex.com/query/info_cp/{cp}?token={Config.API_CP_TOKEN}"
    
    try:
        #* Hacer request HTTP con timeout de 5 segundos
        response = requests.get(url, timeout=5)
        
        response.raise_for_status()  #* Lanza error si status != 200
        data = response.json()        #* Validar que la respuesta contenga datos válidos
        #* La API puede retornar lista directamente o diccionario con 'error'
        
        #! ||------------------- Validar estructura de respuesta de la API -------------------||
        if isinstance(data, dict) and (data.get('error') or not data.get('response')):
            raise APIException(f"Código postal no encontrado: {cp}")
        
        if isinstance(data, list) and len(data) == 0:
            raise APIException(f"Código postal no encontrado: {cp}")
        
        #* Inicializar variables para almacenar información extraída
        colonias = []
        municipio = ''
        estado = ''
        
        #? <|------------------- Procesar respuesta tipo lista -------------------|>
        #* Si la respuesta es una lista directamente (formato común de Copomex)
        if isinstance(data, list):
            colonias_data = data
            if colonias_data and len(colonias_data) > 0:
                primer_colonia = colonias_data[0]
                municipio = primer_colonia.get('response', {}).get('municipio', '')
                estado = primer_colonia.get('response', {}).get('estado', '')
                
                #* Extraer nombres de todas las colonias
                colonias = [item.get('response', {}).get('asentamiento', '') 
                        for item in colonias_data]
        
        #? <|------------------- Procesar respuesta tipo diccionario -------------------|>
        #* Si la respuesta es un diccionario con 'response'
        elif isinstance(data, dict) and 'response' in data:
            #* Extraer lista de colonias del diccionario
            if 'colonia' in data['response']:
                colonias = [col for col in data['response']['colonia']]
            
            #* Extraer municipio y estado de la primera colonia
            if colonias and len(colonias) > 0:
                primer_colonia = colonias[0]
                municipio = primer_colonia.get('municipio', '')
                estado = primer_colonia.get('estado', '')
            
            #* Extraer solo los nombres si las colonias son diccionarios
            colonias = [col.get('nombre', col) if isinstance(col, dict) else col 
                       for col in colonias]
        
        #* Retornar información estructurada
        return {
            'colonias': colonias,
            'municipio': municipio,
            'estado': estado
        }
    
    #! ||------------------- Manejo de errores de conexión -------------------||
    except requests.Timeout:
        raise APIException("Timeout al consultar API de códigos postales. Intenta de nuevo.")
    
    except requests.RequestException as e:
        raise APIException(f"Error al consultar API: {str(e)}")


#? <|------------------- Sección de testing -------------------|>

if __name__ == '__main__':
    """
    * Prueba el servicio con códigos postales reales de México
    * 
    * Ejecutar: python services/api_service.py
    """
    #! ||------------------- Requiere conexión a internet -------------------||
    print("📮 PROBANDO API DE CÓDIGOS POSTALES\n")
    
    #* Códigos postales de prueba de diferentes ciudades mexicanas
    codigos_prueba = [
        '22000',  #* Tijuana, Baja California
        '64000',  #* Monterrey, Nuevo León
        '06000',  #* Ciudad de México
        '44100',  #* Guadalajara, Jalisco
        '12345',  #* Código inválido (para probar manejo de errores)
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
            
            #* Mostrar primeras 5 colonias como ejemplo
            if info['colonias']:
                print(f"\n📍 Primeras colonias:")
                for i, colonia in enumerate(info['colonias'][:5], 1):
                    print(f"   {i}. {colonia}")
                
                if len(info['colonias']) > 5:
                    print(f"   ... y {len(info['colonias']) - 5} colonias más")
            
        except APIException as e:
            print(f"✗ Error: {e}")
        
        print()