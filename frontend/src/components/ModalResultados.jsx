//?  imports
import '../styles/ModalResultados.css';

function ModalResultados({ paciente, onCerrar }) {
    if (!paciente) return null;

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

    // Formatear fecha
    const formatearFecha = (fechaISO) => {
        const fecha = new Date(fechaISO);
        return fecha.toLocaleDateString('es-MX', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // Contar resultados normales y anormales
    const contarResultados = () => {
        const resultados = paciente.estudio.resultados;
        const normales = resultados.filter(r => r.estado === 'Normal').length;
        const total = resultados.length;
        const porcentaje = Math.round((normales / total) * 100);
        return { normales, total, porcentaje };
    };

    const { normales, total, porcentaje } = contarResultados();

    return (
        <div className="modal-overlay" onClick={onCerrar}>
            <div className="modal-resultados" onClick={(e) => e.stopPropagation()}>
                {/* HEADER */}
                <div className="modal-header">
                    <h2>Resultados de Laboratorio</h2>
                    <button className="btn-cerrar" onClick={onCerrar}>
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                {/* INFO PACIENTE Y RESUMEN */}
                <div className="info-grid">
                    {/* INFO PACIENTE */}
                    <div className="info-paciente">
                        <h3 className="nombre-paciente">
                            {paciente.datos_personales.nombre} {paciente.datos_personales.apellido_paterno}
                        </h3>
                        <div className="detalles-paciente">
                            <span>
                                <strong>Edad:</strong> {calcularEdad(paciente.datos_personales.fecha_nacimiento)} años
                            </span>
                            <span>
                                <strong>Sexo:</strong> {paciente.datos_personales.sexo === 'M' ? 'Masculino' : 'Femenino'}
                            </span>
                            <span>
                                <strong>ID:</strong> #{paciente._id.slice(-6).toUpperCase()}
                            </span>
                        </div>
                        <div className="detalles-estudio">
                            <span>
                                <strong>Estudio:</strong> {paciente.estudio.nombre_estudio}
                            </span>
                            <span>
                                <strong>Fecha:</strong> {formatearFecha(paciente.estudio.fecha_creacion)}
                            </span>
                        </div>
                    </div>

                    {/* RESUMEN */}
                    <div className="resumen-card">
                        <h4>Resumen</h4>
                        <p className="resumen-texto">
                            {normales} de {total} parámetros están en rango normal ({porcentaje}%)
                        </p>
                    </div>
                </div>

                {/* TÍTULO TABLA */}
                <h3 className="titulo-seccion">Pacientes Registrados</h3>

                {/* TABLA DE RESULTADOS */}
                <div className="tabla-wrapper">
                    <table className="tabla-resultados">
                        <thead>
                            <tr>
                                <th>Parámetro</th>
                                <th>Valor</th>
                                <th>Unidad</th>
                                <th>Rango Normal</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paciente.estudio.resultados.map((resultado, index) => (
                                <tr
                                    key={index}
                                    className={resultado.estado === 'Normal' ? 'fila-normal' : 'fila-anormal'}
                                >
                                    <td className="parametro-nombre">{resultado.parametro}</td>
                                    <td className="parametro-valor">{resultado.valor}</td>
                                    <td className="parametro-unidad">{resultado.unidad}</td>
                                    <td className="parametro-rango">{resultado.rango_normal}</td>
                                    <td>
                                        <span className={`estado-badge ${resultado.estado === 'Normal' ? 'normal' : 'anormal'}`}>
                                            {resultado.estado === 'Normal' ? (
                                                <>
                                                    <span className="material-symbols-outlined">check_circle</span>
                                                    Normal
                                                </>
                                            ) : (
                                                <>
                                                    <span className="material-symbols-outlined">warning</span>
                                                    {resultado.estado}
                                                </>
                                            )}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* FOOTER */}
                <div className="modal-footer">
                    <button className="btn-cerrar-footer" onClick={onCerrar}>
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ModalResultados;
