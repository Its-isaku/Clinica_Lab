#? <|------------------- API REST para Sistema de Laboratorio Clínico -------------------|>
"""
* Sistema de gestión de pacientes y resultados de estudios clínicos
* 
* Funcionalidades principales:
* - CRUD completo de pacientes
* - Generación automática de resultados de laboratorio
* - Consulta de códigos postales (API externa Copomex)
* - Estadísticas y dashboard
* 
* Tipos de estudios soportados:
* - Biometría Hemática Completa (15 parámetros)
* - Química Sanguínea (15 parámetros)
* - Examen General de Orina (15 parámetros)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_collection
from services import generar_resultados, obtener_nombre_estudio, obtener_info_codigo_postal, APIException
from bson import ObjectId
from datetime import datetime

#? <|------------------- Configuración de la aplicación Flask -------------------|>
app = Flask(__name__)
CORS(app)  #* Habilitar CORS para React

#* Variable global para lazy loading de la colección de MongoDB
collection = None

def get_db_collection():
    """
    * Obtiene la colección de MongoDB con inicialización lazy
    * 
    * Returns:
    *     Collection: Colección de pacientes de MongoDB
    """
    global collection
    if collection is None:
        collection = get_collection()
    return collection


#? <|------------------- Utilidades y funciones auxiliares -------------------|>

def serialize_paciente(paciente):
    """
    * Serializa documentos de MongoDB convirtiendo ObjectId a string
    * 
    * MongoDB almacena IDs como ObjectId, pero JSON requiere strings
    * Esta función convierte el _id para poder retornarlo en respuestas JSON
    * 
    * Args:
    *     paciente (dict): Documento de paciente de MongoDB
    * 
    * Returns:
    *     dict: Paciente con _id como string compatible con JSON
    """
    if paciente:
        paciente['_id'] = str(paciente['_id'])
    return paciente


#? <|------------------- Endpoints para gestión de pacientes -------------------|> de pacientes -------------------|>

@app.route('/api/pacientes', methods=['GET'])
def get_pacientes():
    """
    * GET - Obtener todos los pacientes activos del sistema
    * 
    * Retorna solo pacientes con activo=True (no eliminados)
    * 
    * Returns:
    *     JSON: Lista de pacientes y cantidad total
    *     
    * Ejemplo de respuesta:
    *     {
    *         "pacientes": [...],
    *         "total": 5
    *     }
    """
    try:
        #* Buscar solo pacientes activos (soft delete)
        pacientes = list(get_db_collection().find({'activo': True}))
        
        #* Convertir ObjectIds a strings para compatibilidad JSON
        pacientes = [serialize_paciente(p) for p in pacientes]
        
        return jsonify({
            'pacientes': pacientes,
            'total': len(pacientes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pacientes/<id>', methods=['GET'])
def get_paciente(id):
    """
    * GET - Obtener los datos completos de un paciente específico
    * 
    * Args:
    *     id (str): ID del paciente en formato MongoDB ObjectId
    * 
    * Returns:
    *     JSON: Datos completos del paciente incluyendo resultados
    *     
    * Códigos de respuesta:
    *     - 200: Paciente encontrado exitosamente
    *     - 400: ID inválido (formato incorrecto)
    *     - 404: Paciente no encontrado
    """
    try:
        #! ||------------------- Validar formato de ObjectId antes de consultar -------------------|| 
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        #* Buscar paciente por ID
        paciente = get_db_collection().find_one({'_id': ObjectId(id)})
        
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        return jsonify(serialize_paciente(paciente)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pacientes', methods=['POST'])
def create_paciente():
    """
    * POST - Crear nuevo paciente y generar resultados de laboratorio automáticamente
    * 
    * Esta función:
    * 1. Valida los datos del paciente
    * 2. Calcula la edad a partir de fecha de nacimiento
    * 3. Genera 15 resultados según el tipo de estudio
    * 4. Inserta el paciente completo en MongoDB
    * 
    * Request Body:
    *     {
    *         "datos_personales": {...},
    *         "direccion": {...},
    *         "estudio": {
    *             "tipo": "biometria_hematica" | "quimica_sanguinea" | "examen_orina",
    *             "notas": "..."
    *         }
    *     }
    * 
    * Returns:
    *     JSON: Paciente creado con 15 resultados generados
    *     
    * Códigos de respuesta:
    *     - 201: Paciente creado exitosamente
    *     - 400: Datos faltantes o inválidos
    """
    try:
        datos = request.json
        
        #! ||------------------- Validación de datos requeridos -------------------|| 
        if not datos:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        if 'datos_personales' not in datos:
            return jsonify({'error': 'Faltan datos personales'}), 400
        
        if 'estudio' not in datos or 'tipo' not in datos['estudio']:
            return jsonify({'error': 'Falta tipo de estudio'}), 400
        
        #* Calcular edad automáticamente desde fecha de nacimiento
        fecha_nac_str = datos['datos_personales'].get('fecha_nacimiento')
        if fecha_nac_str:
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nac).days // 365
            datos['datos_personales']['edad'] = edad
        
        #* Obtener tipo de estudio y sexo para generar resultados
        tipo_estudio = datos['estudio']['tipo']
        sexo = datos['datos_personales'].get('sexo', 'M')
        
        #* Generar 15 resultados según tipo de estudio y sexo
        resultados = generar_resultados(tipo_estudio, sexo)
        
        #* Agregar metadatos del estudio
        datos['estudio']['nombre'] = obtener_nombre_estudio(tipo_estudio)
        datos['estudio']['fecha_creacion'] = datetime.now().isoformat()
        
        #* Agregar resultados y metadatos al documento
        datos['resultados'] = resultados
        datos['fecha_registro'] = datetime.now().isoformat()
        datos['activo'] = True
        
        #* Insertar documento completo en MongoDB
        result = get_db_collection().insert_one(datos)
        
        #* Retornar paciente creado
        paciente = get_db_collection().find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Paciente creado exitosamente',
            'paciente': serialize_paciente(paciente)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pacientes/<id>', methods=['PUT'])
def update_paciente(id):
    """
    * PUT - Actualizar datos de un paciente existente
    * 
    * Permite actualizar:
    * - Datos personales
    * - Dirección
    * - Información del estudio
    * 
    * Si cambia la fecha de nacimiento, recalcula edad automáticamente
    * 
    * Args:
    *     id (str): ID del paciente a actualizar
    * 
    * Request Body:
    *     Campos a actualizar (parcial o completo)
    * 
    * Returns:
    *     JSON: Paciente actualizado con todos sus datos
    """
    try:
        #! ||------------------- Validar formato de ID antes de actualizar -------------------|| 
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        datos = request.json
        
        if not datos:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        #* Recalcular edad si cambió fecha de nacimiento
        if 'datos_personales' in datos and 'fecha_nacimiento' in datos['datos_personales']:
            fecha_nac_str = datos['datos_personales']['fecha_nacimiento']
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nac).days // 365
            datos['datos_personales']['edad'] = edad
        
        #* Registrar fecha de última modificación
        datos['fecha_modificacion'] = datetime.now().isoformat()
        
        #* Actualizar documento en MongoDB usando $set
        result = get_db_collection().update_one(
            {'_id': ObjectId(id)},
            {'$set': datos}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        #* Retornar paciente actualizado
        paciente = get_db_collection().find_one({'_id': ObjectId(id)})
        
        return jsonify({
            'message': 'Paciente actualizado exitosamente',
            'paciente': serialize_paciente(paciente)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pacientes/<id>', methods=['DELETE'])
def delete_paciente(id):
    """
    * DELETE - Eliminar paciente del sistema (soft delete)
    * 
    * No elimina físicamente el registro, solo lo marca como inactivo
    * Esto permite mantener historial y recuperar datos si es necesario
    * 
    * Args:
    *     id (str): ID del paciente a eliminar
    * 
    * Returns:
    *     JSON: Mensaje de confirmación
    *     
    *! ||------------------- Soft Delete: No elimina, marca activo=False -------------------|| 
    """
    try:
        #! ||------------------- Validar ID antes de eliminar -------------------|| 
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        #* Soft delete: marcar como inactivo en lugar de eliminar permanentemente
        result = get_db_collection().update_one(
            {'_id': ObjectId(id)},
            {'$set': {'activo': False, 'fecha_eliminacion': datetime.now().isoformat()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        return jsonify({
            'message': 'Paciente eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#? <|------------------- Endpoint de estadísticas para Dashboard -------------------|>

@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    """
    * GET - Obtener estadísticas generales para el dashboard
    * 
    * Calcula:
    * - Total de pacientes activos
    * - Estudios realizados hoy
    * - Distribución por tipo de estudio
    * 
    * Returns:
    *     JSON:
    *     {
    *         "total_pacientes": int,
    *         "estudios_hoy": int,
    *         "por_tipo_estudio": {
    *             "biometria_hematica": int,
    *             "quimica_sanguinea": int,
    *             "examen_orina": int
    *         }
    *     }
    """
    try:
        #* Contar total de pacientes activos
        total_pacientes = get_db_collection().count_documents({'activo': True})
        
        #* Contar estudios creados hoy usando regex en fecha
        hoy = datetime.now().date().isoformat()
        estudios_hoy = get_db_collection().count_documents({
            'activo': True,
            'estudio.fecha_creacion': {'$regex': f'^{hoy}'}
        })
        
        #* Usar agregación de MongoDB para contar por tipo de estudio
        pipeline = [
            {'$match': {'activo': True}},
            {'$group': {
                '_id': '$estudio.tipo',
                'cantidad': {'$sum': 1}
            }}
        ]
        por_tipo = list(get_db_collection().aggregate(pipeline))
        
        #* Formatear resultados en estructura predefinida
        conteo_tipos = {
            'biometria_hematica': 0,
            'quimica_sanguinea': 0,
            'examen_orina': 0
        }
        
        for item in por_tipo:
            if item['_id'] in conteo_tipos:
                conteo_tipos[item['_id']] = item['cantidad']
        
        return jsonify({
            'total_pacientes': total_pacientes,
            'estudios_hoy': estudios_hoy,
            'por_tipo_estudio': conteo_tipos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#? <|------------------- Integración con API externa (Copomex) -------------------|>

@app.route('/api-externa/cp/<codigo>', methods=['GET'])
def api_codigo_postal(codigo):
    """
    * GET - Consultar información de código postal mexicano
    * 
    * Consume la API de Copomex para obtener:
    * - Lista de colonias
    * - Municipio
    * - Estado
    * 
    * Args:
    *     codigo (str): Código postal de 5 dígitos
    * 
    * Returns:
    *     JSON:
    *     {
    *         "colonias": ["Centro", "Zona Norte", ...],
    *         "municipio": "Tijuana",
    *         "estado": "Baja California"
    *     }
    *     
    * Ejemplo:
    *     GET /api-externa/cp/22000
    *     
    *! ||------------------- Depende de API externa (puede fallar) -------------------|| 
    """
    try:
        info = obtener_info_codigo_postal(codigo)
        return jsonify(info), 200
        
    except APIException as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#? <|------------------- Rutas auxiliares y endpoints de utilidad -------------------|>

@app.route('/', methods=['GET'])
def home():
    """
    * Ruta raíz - Información general de la API
    * 
    * Muestra versión y lista de endpoints disponibles
    """
    return jsonify({
        'api': 'Laboratorio Clínico API',
        'version': '1.0',
        'endpoints': [
            'GET  /api/pacientes - Lista todos los pacientes',
            'GET  /api/pacientes/<id> - Obtiene un paciente',
            'POST /api/pacientes - Crea paciente + genera resultados',
            'PUT  /api/pacientes/<id> - Actualiza paciente',
            'DELETE /api/pacientes/<id> - Elimina paciente',
            'GET  /api/estadisticas - Estadísticas del dashboard',
            'GET  /api-externa/cp/<codigo> - Consulta código postal'
        ]
    }), 200


@app.route('/api/test', methods=['GET'])
def test():
    """
    * Endpoint de prueba para verificar estado de la API
    * 
    * Verifica:
    * - API en funcionamiento
    * - Conexión a MongoDB
    """
    from database import test_connection
    
    return jsonify({
        'message': 'API funcionando correctamente',
        'status': 'ok',
        'database': 'Conectado' if test_connection() else 'Desconectado'
    }), 200


#? <|------------------- Manejadores globales de errores HTTP -------------------|>

@app.errorhandler(404)
def not_found(error):
    """
    * Manejo personalizado de rutas no encontradas (404)
    """
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """
    * Manejo personalizado de errores internos del servidor (500)
    """
    return jsonify({'error': 'Error interno del servidor'}), 500


#? <|------------------- Punto de entrada principal -------------------|>

if __name__ == '__main__':
    #* Banner informativo al iniciar el servidor
    print("\n" + "="*60)
    print("🚀 INICIANDO API DE LABORATORIO CLÍNICO")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("🔗 Prueba: http://localhost:5000/api/test")
    print("📋 Endpoints disponibles: http://localhost:5000")
    print("="*60 + "\n")
    
    #! ||------------------- Modo DEBUG activado - No usar en producción -------------------||
    app.run(debug=True, port=5000)