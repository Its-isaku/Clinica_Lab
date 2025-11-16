#? <|------------------- Generador de resultados de laboratorio -------------------|>
"""
* Sistema de generación aleatoria de resultados clínicos
* 
* Genera resultados realistas para 3 tipos de estudios:
* - Biometría Hemática Completa (15 parámetros)
* - Química Sanguínea (15 parámetros)
* - Examen General de Orina (15 parámetros)
* 
* Los resultados se generan dentro de rangos médicos reales:
* - 80% probabilidad de valores normales
* - 20% probabilidad de valores anormales (altos o bajos)
* - Rangos específicos por género cuando aplica
* 
* Tipos de parámetros:
* - Cuantitativos: Valores numéricos con rangos (ej: Hemoglobina 13.5 g/dL)
* - Cualitativos: Valores descriptivos (ej: Color "Amarillo claro")
"""

import json
import random
from pathlib import Path


#? <|------------------- Función principal de generación -------------------|>

def generar_resultados(tipo_estudio, sexo='M'):
    """
    * Genera 15 resultados aleatorios basados en rangos médicos reales
    * 
    * Proceso:
    * 1. Carga rangos del archivo JSON correspondiente
    * 2. Para cada parámetro genera un valor aleatorio
    * 3. Aplica rangos específicos por género si corresponde
    * 4. Determina si el valor es normal o anormal
    * 
    * Args:
    *     tipo_estudio (str): 'biometria_hematica', 'quimica_sanguinea', 'examen_orina'
    *     sexo (str): 'M' (Masculino) o 'F' (Femenino) - afecta rangos de algunos parámetros
    * 
    * Returns:
    *     list: Lista de 15 diccionarios con resultados generados
    * 
    * Ejemplo de resultado cuantitativo:
    *     {
    *         'parametro': 'Hemoglobina',
    *         'valor': 13.5,
    *         'unidad': 'g/dL',
    *         'valor_minimo': 13.5,
    *         'valor_maximo': 17.5,
    *         'normal': True,
    *         'tipo': 'cuantitativo'
    *     }
    * 
    * Ejemplo de resultado cualitativo:
    *     {
    *         'parametro': 'Color',
    *         'valor': 'Amarillo claro',
    *         'unidad': '',
    *         'valor_normal': 'Amarillo claro',
    *         'normal': True,
    *         'tipo': 'cualitativo'
    *     }
    """
    
    #* Mapear tipo de estudio a archivo JSON correspondiente
    mapeo_archivos = {
        'biometria_hematica': 'rangos_biometria.json',
        'quimica_sanguinea': 'rangos_quimica.json',
        'examen_orina': 'rangos_orina.json'
    }
    
    #* Obtener nombre de archivo
    nombre_archivo = mapeo_archivos.get(tipo_estudio)
    
    #! ||------------------- Validar tipo de estudio antes de continuar -------------------|| 
    if not nombre_archivo:
        raise ValueError(f"Tipo de estudio inválido: {tipo_estudio}. Tipos válidos: {list(mapeo_archivos.keys())}")
    
    #* Construir ruta absoluta al archivo JSON de rangos
    archivo_json = Path(__file__).parent.parent / 'data' / nombre_archivo
    
    #! ||------------------- Verificar que exista el archivo de rangos -------------------|| 
    if not archivo_json.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo_json}")
    
    #* Cargar rangos desde JSON
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    resultados = []
    
    #* Iterar sobre cada parámetro del estudio
    for parametro in datos['parametros']:
        
        #? <|------------------- Generar valores para parámetros cualitativos -------------------|>
        if parametro.get('tipo') == 'cualitativo':
            #* 80% probabilidad de valor normal, 20% anormal
            if random.random() < 0.8:
                valor = parametro['valor_normal']
                normal = True
            else:
                #* Elegir valor anormal aleatorio de los posibles
                valores_anormales = [v for v in parametro['valores_posibles'] 
                                    if v != parametro['valor_normal']]
                valor = random.choice(valores_anormales)
                normal = False
            
            #* Crear resultado cualitativo
            resultados.append({
                'parametro': parametro['nombre'],
                'valor': valor,
                'unidad': '',
                'valor_minimo': None,
                'valor_maximo': None,
                'valor_normal': parametro['valor_normal'],
                'normal': normal,
                'tipo': 'cualitativo'
            })
        
        #? <|------------------- Generar valores para parámetros cuantitativos -------------------|>
        else:
            #* Determinar rangos según género si el parámetro lo requiere
            if parametro.get('genero_especifico') and sexo:
                if sexo == 'M':
                    rango_min = parametro.get('rango_min_hombre', parametro['rango_min'])
                    rango_max = parametro.get('rango_max_hombre', parametro['rango_max'])
                else:  #* 'F'
                    rango_min = parametro.get('rango_min_mujer', parametro['rango_min'])
                    rango_max = parametro.get('rango_max_mujer', parametro['rango_max'])
            else:
                rango_min = parametro['rango_min']
                rango_max = parametro['rango_max']
            
            #* Calcular variación para valores anormales (20% del rango total)
            variacion = (rango_max - rango_min) * 0.2
            
            #* Generar valor: 80% normal, 20% anormal
            if random.random() < 0.8:
                #* Valor NORMAL (dentro del rango)
                valor = round(random.uniform(rango_min, rango_max), 2)
            else:
                #* Valor ANORMAL (fuera del rango)
                if random.random() < 0.5:
                    #* Valor BAJO (debajo del rango mínimo)
                    valor = round(random.uniform(
                        max(0, rango_min - variacion), 
                        rango_min
                    ), 2)
                else:
                    #* Valor ALTO (arriba del rango máximo)
                    valor = round(random.uniform(
                        rango_max, 
                        rango_max + variacion
                    ), 2)
            
            #* Determinar si el valor está dentro del rango normal
            normal = (rango_min <= valor <= rango_max)
            
            #* Crear resultado cuantitativo
            resultados.append({
                'parametro': parametro['nombre'],
                'valor': valor,
                'unidad': parametro.get('unidad', ''),
                'valor_minimo': rango_min,
                'valor_maximo': rango_max,
                'normal': normal,
                'tipo': 'cuantitativo'
            })
    
    return resultados


#? <|------------------- Función auxiliar para nombres de estudios -------------------|>

def obtener_nombre_estudio(tipo_estudio):
    """
    * Retorna el nombre completo y legible del tipo de estudio
    * 
    * Args:
    *     tipo_estudio (str): Código del estudio
    * 
    * Returns:
    *     str: Nombre completo del estudio para mostrar al usuario
    """
    nombres = {
        'biometria_hematica': 'Biometría Hemática Completa',
        'quimica_sanguinea': 'Química Sanguínea (Perfil Metabólico)',
        'examen_orina': 'Examen General de Orina'
    }
    return nombres.get(tipo_estudio, tipo_estudio)


#? <|------------------- Sección de testing y pruebas -------------------|>

if __name__ == '__main__':
    """
    * Prueba el generador con los 3 tipos de estudios
    * 
    * Ejecutar: python services/generador_resultados.py
    """
    print("🧪 PROBANDO GENERADOR DE RESULTADOS\n")
    
    #* Casos de prueba: cada tipo de estudio con diferente género
    estudios = [
        ('biometria_hematica', 'M'),
        ('quimica_sanguinea', 'F'),
        ('examen_orina', 'M')
    ]
    
    for tipo, sexo in estudios:
        print(f"{'='*60}")
        print(f"📋 {obtener_nombre_estudio(tipo)}")
        print(f"👤 Sexo: {'Masculino' if sexo == 'M' else 'Femenino'}")
        print(f"{'='*60}\n")
        
        try:
            resultados = generar_resultados(tipo, sexo)
            
            print(f"✓ Se generaron {len(resultados)} parámetros\n")
            
            #* Mostrar los primeros 5 resultados como ejemplo
            for i, resultado in enumerate(resultados[:5], 1):
                estado = "✓ NORMAL" if resultado['normal'] else "⚠ ANORMAL"
                
                if resultado['tipo'] == 'cualitativo':
                    print(f"{i}. {resultado['parametro']}: {resultado['valor']} {estado}")
                else:
                    print(f"{i}. {resultado['parametro']}: {resultado['valor']} {resultado['unidad']} "
                        f"(Rango: {resultado['valor_minimo']}-{resultado['valor_maximo']}) {estado}")
            
            if len(resultados) > 5:
                print(f"   ... y {len(resultados) - 5} parámetros más")
            
            #* Calcular estadísticas de normalidad
            normales = sum(1 for r in resultados if r['normal'])
            anormales = len(resultados) - normales
            print(f"\n📊 Estadísticas: {normales} normales, {anormales} anormales "
                f"({round(normales/len(resultados)*100)}% normales)")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()