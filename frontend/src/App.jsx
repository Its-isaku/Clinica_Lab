//? Imports
import { useState, useEffect } from 'react';
import './styles/App.css';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import { obtenerPacientes, obtenerEstadisticas } from './services/api';

function App() {
  //? ESTADOS GLOBALES
  const [pacientes, setPacientes] = useState([]);
  const [estadisticas, setEstadisticas] = useState({
    total_pacientes: 0,
    estudios_hoy: 0,
    por_tipo_estudio: {}
  });
  const [cargando, setCargando] = useState(true);
  const [modalFormularioAbierto, setModalFormularioAbierto] = useState(false);

  //? ARGAR DATOS AL INICIAR
  useEffect(() => {
    cargarDatos();
  }, []);

  //? FUNCIÓN PARA RECARGAR DATOS
  const cargarDatos = async () => {
    try {
      setCargando(true);
      const [statsData, pacientesData] = await Promise.all([
        obtenerEstadisticas(),
        obtenerPacientes()
      ]);
      
      setEstadisticas(statsData);
      setPacientes(pacientesData.pacientes);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      alert('Error al cargar datos. Verifica que el backend esté corriendo en http://localhost:5000');
    } finally {
      setCargando(false);
    }
  };

  //? ABRIR MODAL DESDE NAVBAR
  const handleAbrirModalNuevo = () => {
    setModalFormularioAbierto(true);
  };

  return (
    <div className="App">
      <Navbar onAgregarPaciente={handleAbrirModalNuevo} />
      
      <Dashboard 
        pacientes={pacientes}
        estadisticas={estadisticas}
        cargando={cargando}
        onRecargar={cargarDatos}
        modalFormularioAbierto={modalFormularioAbierto}
        setModalFormularioAbierto={setModalFormularioAbierto}
      />
    </div>
  );
}

export default App;