//? Imports
import { useState, useEffect } from 'react';
import './styles/App.css';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import { obtenerPacientes, obtenerEstadisticas } from './services/api';

//? App component 
function App() {

  //? ESTADOS GLOBALES
  const [pacientes, setPacientes] = useState([]);
  const [estadisticas, setEstadisticas] = useState({
    total_pacientes: 0,
    estudios_hoy: 0,
    por_tipo_estudio: {}
  });
  const [cargando, setCargando] = useState(true);

  //? CARGAR DATOS AL INICIAR
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
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="App">
      <Navbar />
      <Dashboard 
        pacientes={pacientes}
        estadisticas={estadisticas}
        cargando={cargando}
        onRecargar={cargarDatos}
      />
    </div>
  );
}

export default App;