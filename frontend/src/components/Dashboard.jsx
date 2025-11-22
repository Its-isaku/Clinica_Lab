import { useState } from 'react';
import '../styles/Dashboard.css';
import TarjetasEstadisticas from './TarjetasEstadisticas';
import TablaPacientes from './TablaPacientes';
import Modal from './Modal';
import ModalResultados from './ModalResultados';
import FormularioPaciente from './FormularioPaciente';
import { eliminarPaciente, crearPaciente, actualizarPaciente } from '../services/api';

function Dashboard({
    pacientes,
    estadisticas,
    cargando,
    onRecargar,
    modalFormularioAbierto,
    setModalFormularioAbierto,
}) {
    //? ESTADOS LOCALES DE MODALES
    const [modalResultadosAbierto, setModalResultadosAbierto] = useState(false);
    const [pacienteSeleccionado, setPacienteSeleccionado] = useState(null);
    const [modoEdicion, setModoEdicion] = useState(false);

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
                alert('Paciente actualizado correctamente');
            } else {
                await crearPaciente(datosPaciente);
                alert('Paciente creado correctamente');
            }
            setModalFormularioAbierto(false);
            setPacienteSeleccionado(null);
            setModoEdicion(false);
            onRecargar(); //* Recargar datos desde App.jsx
        } catch (error) {
            console.error('Error al guardar:', error);
            alert('Error al guardar el paciente: ' + error.message);
        }
    };

    //? ELIMINAR PACIENTE
    const handleEliminar = async (id) => {
        if (
            !window.confirm(
                '¿Estás seguro de eliminar este paciente? Esta acción no se puede deshacer.'
            )
        )
            return;

        try {
            await eliminarPaciente(id);
            onRecargar();
            alert('Paciente eliminado correctamente');
        } catch (error) {
            console.error('Error al eliminar:', error);
            alert('Error al eliminar el paciente: ' + error.message);
        }
    };

    //? CERRAR MODAL FORMULARIO
    const handleCerrarFormulario = () => {
        setModalFormularioAbierto(false);
        setPacienteSeleccionado(null);
        setModoEdicion(false);
    };

    if (cargando) {
        return (
            <div className="dashboard">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Cargando datos...</p>
                </div>
            </div>
        );
    }

    return (
        <>
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
                <Modal onClose={handleCerrarFormulario}>
                    <FormularioPaciente
                        paciente={pacienteSeleccionado}
                        modoEdicion={modoEdicion}
                        onGuardar={handleGuardarPaciente}
                        onCancelar={handleCerrarFormulario}
                    />
                </Modal>
            )}

            {modalResultadosAbierto && (
                <ModalResultados
                    paciente={pacienteSeleccionado}
                    onCerrar={() => setModalResultadosAbierto(false)}
                />
            )}
        </>
    );
}

export default Dashboard;