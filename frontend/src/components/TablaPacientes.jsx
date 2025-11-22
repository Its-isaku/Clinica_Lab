//?  imports
import '../styles/TablaPacientes.css';


//? TablaPacientes component
function TablaPacientes({ pacientes, onVerResultados, onEditar, onEliminar }) {
  // Formatear fecha
  const formatearFecha = (fechaISO) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // Calcular edad
  const calcularEdad = (fechaNacimiento) => {
    const hoy = new Date();
    const nacimiento = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad--;
    }
    return edad;
  };

  return (
    <div className="Table_Container">
      <div className="Table_title">
        <h2>Pacientes Registrados</h2>
      </div>
      <div className="Table_Content">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre completo</th>
              <th>Edad</th>
              <th>Sexo</th>
              <th>Estudio</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {pacientes.length === 0 ? (
              <tr>
                <td colSpan="7" className="tabla-vacia">
                  <span className="material-symbols-outlined">person_off</span>
                  <p>No hay pacientes</p>
                </td>
              </tr>
            ) : (
              pacientes.map((paciente) => (
                <tr key={paciente._id}>
                  <td>{paciente._id.slice(-6).toUpperCase()}</td>
                  <td>
                    {paciente.datos_personales.nombre} {paciente.datos_personales.apellido_paterno}
                  </td>
                  <td>{calcularEdad(paciente.datos_personales.fecha_nacimiento)}</td>
                  <td>
                    <span className={`sexo-badge ${paciente.datos_personales.sexo === 'M' ? 'masculino' : 'femenino'}`}>
                      {paciente.datos_personales.sexo === 'M' ? 'Masculino' : 'Femenino'}
                    </span>
                  </td>
                  <td>{paciente.estudio.nombre_estudio}</td>
                  <td>{formatearFecha(paciente.estudio.fecha_creacion)}</td>
                  <td>
                    <div className="ActionBtns">
                      <button 
                        className="SeeBtn"
                        onClick={() => onVerResultados(paciente)}
                        title="Ver resultados"
                      >
                        <span className="material-symbols-outlined">visibility</span>
                      </button>
                      <button 
                        className="EditBtn"
                        onClick={() => onEditar(paciente)}
                        title="Editar paciente"
                      >
                        <span className="material-symbols-outlined">edit</span>
                      </button>
                      <button 
                        className="DeleteBtn"
                        onClick={() => onEliminar(paciente._id)}
                        title="Eliminar paciente"
                      >
                        <span className="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TablaPacientes;