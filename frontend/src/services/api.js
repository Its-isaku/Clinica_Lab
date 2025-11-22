import axios from 'axios';

//? Configuración base de Axios
const api = axios.create({
    baseURL: 'http://localhost:5000/api', //* URL de tu backend Flask
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, //* 10 segundos
});

//? Funciones para cada endpoint del backend

//? ESTADÍSTICAS
export const obtenerEstadisticas = async () => {
    const response = await api.get('/estadisticas');
    return response.data;
};

//? PACIENTES - LISTAR
export const obtenerPacientes = async () => {
    const response = await api.get('/pacientes');
    return response.data;
};

//? PACIENTE - OBTENER UNO
export const obtenerPaciente = async (id) => {
    const response = await api.get(`/pacientes/${id}`);
    return response.data;
};

//? PACIENTE - CREAR
export const crearPaciente = async (datosPaciente) => {
    const response = await api.post('/pacientes', datosPaciente);
    return response.data;
};

//? PACIENTE - ACTUALIZAR
export const actualizarPaciente = async (id, datosPaciente) => {
    const response = await api.put(`/pacientes/${id}`, datosPaciente);
    return response.data;
};

//? PACIENTE - ELIMINAR
export const eliminarPaciente = async (id) => {
    const response = await api.delete(`/pacientes/${id}`);
    return response.data;
};

//? API EXTERNA - CÓDIGO POSTAL
export const obtenerInfoCodigoPostal = async (codigoPostal) => {
    // Usar endpoint relativo para acceder correctamente a /api-externa
    const response = await api.get(`/../api-externa/cp/${codigoPostal}`);
    return response.data;
};

export default api;