import json
import random
from pathlib import Path


def generar_resultados(tipo_estudio, sexo='M'):
    """
    Genera resultados aleatorios basados en rangos médicos reales.
    
    Args:
        tipo_estudio (str): 'biometria_hematica', 'quimica_sanguinea', 'examen_orina'
        sexo (str): 'M' (Masculino) o 'F' (Femenino) - afecta rangos de algunos parámetros
    
    Returns:
        list: Lista de diccionarios con resultados generados
    
    Ejemplo de resultado:
        [
            {
                'parametro': 'Hemoglobina',
                'valor': 13.5,
                'unidad': 'g/dL',
                'valor_minimo': 13.5,
                'valor_maximo': 17.5,
                'normal': True,
                'tipo': 'cuantitativo'
            },
            ...
        ]
    """
    
    # Mapear tipo de estudio a nombre de archivo
    mapeo_archivos = {
        'biometria_hematica': 'rangos_biometria.json',
        'quimica_sanguinea': 'rangos_quimica.json',
        'examen_orina': 'rangos_orina.json'
    }
    
    # Obtener nombre de archivo
    nombre_archivo = mapeo_archivos.get(tipo_estudio)
    
    if not nombre_archivo:
        raise ValueError(f"Tipo de estudio inválido: {tipo_estudio}. Tipos válidos: {list(mapeo_archivos.keys())}")
    
    # Cargar JSON correspondiente
    archivo_json = Path(__file__).parent.parent / 'data' / nombre_archivo
    
    if not archivo_json.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo_json}")
    
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    resultados = []
    
    for parametro in datos['parametros']:
        
        # ========== PARÁMETROS CUALITATIVOS ==========
        if parametro.get('tipo') == 'cualitativo':
            # 80% probabilidad de valor normal, 20% anormal
            if random.random() < 0.8:
                valor = parametro['valor_normal']
                normal = True
            else:
                # Elegir valor anormal aleatorio
                valores_anormales = [v for v in parametro['valores_posibles'] 
                                    if v != parametro['valor_normal']]
                valor = random.choice(valores_anormales)
                normal = False
            
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
        
        # ========== PARÁMETROS CUANTITATIVOS ==========
        else:
            # Determinar rangos según género si aplica
            if parametro.get('genero_especifico') and sexo:
                if sexo == 'M':
                    rango_min = parametro.get('rango_min_hombre', parametro['rango_min'])
                    rango_max = parametro.get('rango_max_hombre', parametro['rango_max'])
                else:  # 'F'
                    rango_min = parametro.get('rango_min_mujer', parametro['rango_min'])
                    rango_max = parametro.get('rango_max_mujer', parametro['rango_max'])
            else:
                rango_min = parametro['rango_min']
                rango_max = parametro['rango_max']
            
            # Calcular variación (20% del rango para valores anormales)
            variacion = (rango_max - rango_min) * 0.2
            
            # 80% probabilidad de valor normal
            if random.random() < 0.8:
                # Valor NORMAL (dentro del rango)
                valor = round(random.uniform(rango_min, rango_max), 2)
            else:
                # 20% probabilidad de valor ANORMAL
                if random.random() < 0.5:
                    # Valor BAJO (debajo del rango mínimo)
                    valor = round(random.uniform(
                        max(0, rango_min - variacion), 
                        rango_min
                    ), 2)
                else:
                    # Valor ALTO (arriba del rango máximo)
                    valor = round(random.uniform(
                        rango_max, 
                        rango_max + variacion
                    ), 2)
            
            # Determinar si el valor es normal
            normal = (rango_min <= valor <= rango_max)
            
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


def obtener_nombre_estudio(tipo_estudio):
    """
    Retorna el nombre completo del tipo de estudio
    
    Args:
        tipo_estudio (str): Código del estudio
    
    Returns:
        str: Nombre completo del estudio
    """
    nombres = {
        'biometria_hematica': 'Biometría Hemática Completa',
        'quimica_sanguinea': 'Química Sanguínea (Perfil Metabólico)',
        'examen_orina': 'Examen General de Orina'
    }
    return nombres.get(tipo_estudio, tipo_estudio)


# ========== FUNCIÓN DE PRUEBA ==========
if __name__ == '__main__':
    """
    Prueba el generador con los 3 tipos de estudios
    """
    print("🧪 PROBANDO GENERADOR DE RESULTADOS\n")
    
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
            
            # Mostrar los primeros 5 resultados como ejemplo
            for i, resultado in enumerate(resultados[:5], 1):
                estado = "✓ NORMAL" if resultado['normal'] else "⚠ ANORMAL"
                
                if resultado['tipo'] == 'cualitativo':
                    print(f"{i}. {resultado['parametro']}: {resultado['valor']} {estado}")
                else:
                    print(f"{i}. {resultado['parametro']}: {resultado['valor']} {resultado['unidad']} "
                        f"(Rango: {resultado['valor_minimo']}-{resultado['valor_maximo']}) {estado}")
            
            if len(resultados) > 5:
                print(f"   ... y {len(resultados) - 5} parámetros más")
            
            # Estadísticas
            normales = sum(1 for r in resultados if r['normal'])
            anormales = len(resultados) - normales
            print(f"\n📊 Estadísticas: {normales} normales, {anormales} anormales "
                f"({round(normales/len(resultados)*100)}% normales)")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()