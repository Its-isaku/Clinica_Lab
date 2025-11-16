#? <|------------------- Configuración global del sistema -------------------|>
"""
* Archivo de configuración centralizado
* 
* Contiene:
* - Credenciales de MongoDB Atlas
* - Configuración de API externa (Copomex)
* - Variables de entorno del sistema
"""
#! ||------------------- CREDENCIALES SENSIBLES - No versionar en producción -------------------||


class Config:
    """
    * Clase de configuración para toda la aplicación
    * 
    * MongoDB Atlas:
    *     - Conexión a cluster en la nube
    *     - Base de datos: laboratorio_clinico
    *     - Colección: pacientes
    * 
    * API Externa:
    *     - Copomex: API de códigos postales de México
    *     - Token: pruebas (usar token real en producción)
    """
    #* Configuración de MongoDB y APIs externas
    
    #? <|------------------- Configuración de MongoDB Atlas -------------------|>
    
    #! ||------------------- Usuario y contraseña en URI - Usar variables de entorno -------------------||
    MONGO_URI = "mongodb+srv://admin_lab:c5erSRziaQm0N9Dw@labclinico.uvdy1ub.mongodb.net/?appName=LabClinico"
    
    #* Nombre de la base de datos en MongoDB
    DATABASE_NAME = "laboratorio_clinico"
    
    #* Nombre de la colección donde se almacenan pacientes
    COLLECTION_NAME = "pacientes"
    
    #? <|------------------- Configuración de API Externa (Copomex) -------------------|>
    
    #* URL base de la API de códigos postales
    API_CP_BASE_URL = "https://api.copomex.com/query/info_cp"
    
    #! ||------------------- Token de pruebas - Usar token real en producción -------------------||
    API_CP_TOKEN = "pruebas"