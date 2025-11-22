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

    // Contar resultados normales y anormales usando la lógica real
    const contarResultados = () => {
        const resultados = paciente.resultados || [];
        let normales = 0;
        resultados.forEach(r => {
            if (r.tipo === 'cuantitativo') {
                if (r.normal) normales++;
            } else if (r.tipo === 'cualitativo') {
                if (r.normal) normales++;
            }
        });
        const total = resultados.length;
        const porcentaje = total > 0 ? Math.round((normales / total) * 100) : 0;
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
                {/* CONTENIDO SCROLLEABLE */}
                <div className="modal-scroll-content">
                    {/* INFO PACIENTE Y RESUMEN */}
                    <div className="info-grid">
                        {/* INFO PACIENTE */}
                        <div className="info-paciente">
                                <div className="card-paciente-content">
                                    <div className="card-paciente-nombre">
                                        {paciente.datos_personales.nombre} {paciente.datos_personales.apellido_paterno}
                                    </div>
                                    <div className="card-paciente-datos">
                                        <span><strong>Edad:</strong> {calcularEdad(paciente.datos_personales.fecha_nacimiento)} años</span>
                                        <span><strong>Sexo:</strong> {paciente.datos_personales.sexo === 'M' ? 'Masculino' : 'Femenino'}</span>
                                        <span><strong>ID:</strong> #{paciente._id.slice(-6).toUpperCase()}</span>
                                        <span><strong>Estudio:</strong> {paciente.estudio?.nombre || paciente.estudio?.tipo || 'Sin estudio'}</span>
                                        <span><strong>Fecha:</strong> {formatearFecha(paciente.estudio.fecha_creacion)}</span>
                                    </div>
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
                                {(paciente.resultados || []).map((resultado, index) => {
                                    // Determinar rango normal
                                    let rangoNormal = '';
                                    if (resultado.tipo === 'cuantitativo' && resultado.valor_minimo != null && resultado.valor_maximo != null) {
                                        rangoNormal = `${resultado.valor_minimo} - ${resultado.valor_maximo}`;
                                    } else if (resultado.tipo === 'cualitativo' && resultado.valor_normal) {
                                        rangoNormal = resultado.valor_normal;
                                    }

                                    // Determinar estado
                                    let estado = '';
                                    let esNormal = resultado.normal;
                                    if (resultado.tipo === 'cuantitativo') {
                                        if (esNormal) {
                                            estado = 'Normal';
                                        } else if (resultado.valor < resultado.valor_minimo) {
                                            estado = 'Bajo';
                                        } else if (resultado.valor > resultado.valor_maximo) {
                                            estado = 'Alto';
                                        } else {
                                            estado = 'Anormal';
                                        }
                                    } else if (resultado.tipo === 'cualitativo') {
                                        estado = esNormal ? 'Normal' : 'Anormal';
                                    }

                                    return (
                                        <tr
                                            key={index}
                                            className={esNormal ? 'fila-normal' : 'fila-anormal'}
                                        >
                                            <td className="parametro-nombre">{resultado.parametro}</td>
                                            <td className="parametro-valor">{resultado.valor}</td>
                                            <td className="parametro-unidad">{resultado.unidad ? resultado.unidad : '-'}</td>
                                            <td className="parametro-rango">{rangoNormal}</td>
                                            <td>
                                                <span className={`estado-badge ${esNormal ? 'normal' : 'anormal'}`}
                                                    style={{display: 'inline-flex', justifyContent: 'center', alignItems: 'center', minWidth: 70}}>
                                                    {estado}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
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
