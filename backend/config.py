class Config:
    """Configuración general del backend"""
    
    # MongoDB Atlas
    MONGO_URI = "mongodb+srv://admin_lab:c5erSRziaQm0N9Dw@labclinico.uvdy1ub.mongodb.net/?appName=LabClinico"
    DATABASE_NAME = "laboratorio_clinico"
    COLLECTION_NAME = "pacientes"
    
    # API Externa - Copomex (Códigos Postales de México)
    API_CP_BASE_URL = "https://api.copomex.com/query/info_cp"
    API_CP_TOKEN = "pruebas"