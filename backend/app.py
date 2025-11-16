from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_collection
from services import generar_resultados, obtener_nombre_estudio, obtener_info_codigo_postal, APIException
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para React

# Lazy load collection when needed
collection = None

def get_db_collection():
    """Get database collection with lazy initialization"""
    global collection
    if collection is None:
        collection = get_collection()
    return collection


# ============ UTILIDADES ============

def serialize_paciente(paciente):
    """
    Convierte ObjectId de MongoDB a string para JSON
    
    Args:
        paciente (dict): Documento de paciente de MongoDB
    
    Returns:
        dict: Paciente con _id como string
    """
    if paciente:
        paciente['_id'] = str(paciente['_id'])
    return paciente


# ============ ENDPOINTS PACIENTES ============

@app.route('/api/pacientes', methods=['GET'])
def get_pacientes():
    """
    GET - Obtener todos los pacientes activos
    
    Returns:
        JSON con lista de pacientes y total
        
    Ejemplo de respuesta:
        {
            "pacientes": [...],
            "total": 5
        }
    """
    try:
        # Buscar solo pacientes activos
        pacientes = list(get_db_collection().find({'activo': True}))
        
        # Serializar ObjectIds
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
    GET - Obtener un paciente específico por ID
    
    Args:
        id (str): ID del paciente
    
    Returns:
        JSON con datos del paciente
    """
    try:
        # Validar que el ID sea válido
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        # Buscar paciente
        paciente = get_db_collection().find_one({'_id': ObjectId(id)})
        
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        return jsonify(serialize_paciente(paciente)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pacientes', methods=['POST'])
def create_paciente():
    """
    POST - Crear nuevo paciente y generar resultados automáticamente
    
    Request Body:
        {
            "datos_personales": {...},
            "direccion": {...},
            "estudio": {
                "tipo": "biometria_hematica" | "quimica_sanguinea" | "examen_orina",
                "notas": "..."
            }
        }
    
    Returns:
        JSON con paciente creado (incluye 15 resultados generados)
    """
    try:
        datos = request.json
        
        # Validar datos requeridos
        if not datos:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        if 'datos_personales' not in datos:
            return jsonify({'error': 'Faltan datos personales'}), 400
        
        if 'estudio' not in datos or 'tipo' not in datos['estudio']:
            return jsonify({'error': 'Falta tipo de estudio'}), 400
        
        # Calcular edad a partir de fecha de nacimiento
        fecha_nac_str = datos['datos_personales'].get('fecha_nacimiento')
        if fecha_nac_str:
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nac).days // 365
            datos['datos_personales']['edad'] = edad
        
        # Obtener tipo de estudio y sexo
        tipo_estudio = datos['estudio']['tipo']
        sexo = datos['datos_personales'].get('sexo', 'M')
        
        # Generar resultados según tipo de estudio
        resultados = generar_resultados(tipo_estudio, sexo)
        
        # Agregar nombre completo del estudio
        datos['estudio']['nombre'] = obtener_nombre_estudio(tipo_estudio)
        datos['estudio']['fecha_creacion'] = datetime.now().isoformat()
        
        # Agregar resultados al documento
        datos['resultados'] = resultados
        datos['fecha_registro'] = datetime.now().isoformat()
        datos['activo'] = True
        
        # Insertar en MongoDB
        result = get_db_collection().insert_one(datos)
        
        # Retornar paciente creado
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
    PUT - Actualizar paciente existente
    
    Args:
        id (str): ID del paciente
    
    Request Body:
        Campos a actualizar (datos_personales, direccion, etc.)
    
    Returns:
        JSON con paciente actualizado
    """
    try:
        # Validar ID
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        datos = request.json
        
        if not datos:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        # Recalcular edad si cambió fecha de nacimiento
        if 'datos_personales' in datos and 'fecha_nacimiento' in datos['datos_personales']:
            fecha_nac_str = datos['datos_personales']['fecha_nacimiento']
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nac).days // 365
            datos['datos_personales']['edad'] = edad
        
        # Actualizar fecha de modificación
        datos['fecha_modificacion'] = datetime.now().isoformat()
        
        # Actualizar en MongoDB
        result = get_db_collection().update_one(
            {'_id': ObjectId(id)},
            {'$set': datos}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        # Retornar paciente actualizado
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
    DELETE - Eliminar paciente (soft delete)
    
    Args:
        id (str): ID del paciente
    
    Returns:
        JSON con mensaje de confirmación
    """
    try:
        # Validar ID
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'ID de paciente inválido'}), 400
        
        # Soft delete: marcar como inactivo en lugar de eliminar
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


# ============ ENDPOINT ESTADÍSTICAS ============

@app.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    """
    GET - Obtener estadísticas para el dashboard
    
    Returns:
        JSON con estadísticas:
        - total_pacientes: Cantidad total de pacientes activos
        - estudios_hoy: Estudios realizados hoy
        - por_tipo_estudio: Cantidad por cada tipo de estudio
    """
    try:
        # Total de pacientes activos
        total_pacientes = get_db_collection().count_documents({'activo': True})
        
        # Estudios completados hoy
        hoy = datetime.now().date().isoformat()
        estudios_hoy = get_db_collection().count_documents({
            'activo': True,
            'estudio.fecha_creacion': {'$regex': f'^{hoy}'}
        })
        
        # Contar por tipo de estudio
        pipeline = [
            {'$match': {'activo': True}},
            {'$group': {
                '_id': '$estudio.tipo',
                'cantidad': {'$sum': 1}
            }}
        ]
        por_tipo = list(get_db_collection().aggregate(pipeline))
        
        # Formatear conteo por tipo
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


# ============ ENDPOINT API EXTERNA ============

@app.route('/api-externa/cp/<codigo>', methods=['GET'])
def api_codigo_postal(codigo):
    """
    GET - Consultar código postal en API externa (Copomex)
    
    Args:
        codigo (str): Código postal de 5 dígitos
    
    Returns:
        JSON con colonias, municipio y estado
        
    Ejemplo:
        GET /api-externa/cp/22000
        
        {
            "colonias": ["Centro", "Zona Norte", ...],
            "municipio": "Tijuana",
            "estado": "Baja California"
        }
    """
    try:
        info = obtener_info_codigo_postal(codigo)
        return jsonify(info), 200
        
    except APIException as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ RUTA RAÍZ ============

@app.route('/', methods=['GET'])
def home():
    """Ruta raíz - información de la API"""
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
    """Endpoint de prueba para verificar que la API funciona"""
    from database import test_connection
    
    return jsonify({
        'message': 'API funcionando correctamente',
        'status': 'ok',
        'database': 'Conectado' if test_connection() else 'Desconectado'
    }), 200


# ============ MANEJO DE ERRORES ============

@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor"""
    return jsonify({'error': 'Error interno del servidor'}), 500


# ============ EJECUTAR APP ============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 INICIANDO API DE LABORATORIO CLÍNICO")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("🔗 Prueba: http://localhost:5000/api/test")
    print("📋 Endpoints disponibles: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)