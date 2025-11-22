//? Imports
import { useState } from 'react';
import '../styles/Dashboard.css';
import TarjetasEstadisticas from './TarjetasEstadisticas';
import TablaPacientes from './TablaPacientes';
import ModalFormulario from './Modal';
import ModalResultados from './ModalResultados';
import { eliminarPaciente, crearPaciente, actualizarPaciente } from '../services/api';

function Dashboard({ pacientes, estadisticas, cargando, onRecargar }) {
    //? ESTADOS LOCALES DE MODALES
    const [modalFormularioAbierto, setModalFormularioAbierto] = useState(false);
    const [modalResultadosAbierto, setModalResultadosAbierto] = useState(false);
    const [pacienteSeleccionado, setPacienteSeleccionado] = useState(null);
    const [modoEdicion, setModoEdicion] = useState(false);

    //? ABRIR MODAL CREAR NUEVO
    const handleAbrirNuevo = () => {
        setPacienteSeleccionado(null);
        setModoEdicion(false);
        setModalFormularioAbierto(true);
    };

    //? ABRIR MODAL EDITAR
    const handleAbrirEditar = (paciente) => {
        setPacienteSeleccionado(paciente);
        setModoEdicion(true);
        setModalFormularioAbierto(true);
    };

    //? ABRIR MODAL VER RESULTADOS
    const handleVerResultados = (paciente) => {
        setPacienteSeleccionado(paciente);
        setModalResultadosAbierto(true);
    };

    //? GUARDAR PACIENTE (CREAR O EDITAR)
    const handleGuardarPaciente = async (datosPaciente) => {
        try {
            if (modoEdicion) {
                await actualizarPaciente(pacienteSeleccionado._id, datosPaciente);
            } else {
                await crearPaciente(datosPaciente);
            }
            setModalFormularioAbierto(false);
            onRecargar(); //* Recargar datos desde App.jsx
            alert('Paciente guardado correctamente');
        } catch (error) {
            console.error('Error al guardar:', error);
            alert('Error al guardar el paciente');
        }
    };

    //? ELIMINAR PACIENTE
    const handleEliminar = async (id) => {
        if (!confirm('¿Eliminar este paciente?')) return;

        try {
            await eliminarPaciente(id);
            onRecargar();
            alert('Paciente eliminado');
        } catch (error) {
            console.error('Error al eliminar:', error);
            alert('Error al eliminar');
        }
    };

    if (cargando) {
        return <div className="loading">Cargando...</div>;
    }

    return (
        <div className="dashboard">

            {/* //? ESTADÍSTICAS */}
            <TarjetasEstadisticas estadisticas={estadisticas} />

            {/* //? TABLA */}
            <TablaPacientes
                pacientes={pacientes}
                onVerResultados={handleVerResultados}
                onEditar={handleAbrirEditar}
                onEliminar={handleEliminar}
            />

            {/* //? MODALES */}
            {modalFormularioAbierto && (
                <ModalFormulario
                    paciente={pacienteSeleccionado}
                    modoEdicion={modoEdicion}
                    onGuardar={handleGuardarPaciente}
                    onCancelar={() => setModalFormularioAbierto(false)}
                />
            )}

            {modalResultadosAbierto && (
                <ModalResultados
                    paciente={pacienteSeleccionado}
                    onCerrar={() => setModalResultadosAbierto(false)}
                />
            )}
        </div>
    );
}

export default Dashboard;