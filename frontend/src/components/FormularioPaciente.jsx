//?  imports
import '../styles/FormularioPaciente.css'
import { useState, useEffect } from 'react';
import { obtenerInfoCodigoPostal } from '../services/api';

//? FormularioPaciente component
function FormularioPaciente({ paciente, modoEdicion, onGuardar, onCancelar }) {
    //? variables & states
    // 📝 ESTADOS DEL FORMULARIO
    const [formData, setFormData] = useState({
        nombre: '',
        apellido_paterno: '',
        fecha_nacimiento: '',
        sexo: 'M',
        codigo_postal: '',
        colonia: '',
        tipo_estudio: 'biometria_hematica'
    });

    const [colonias, setColonias] = useState([]);
    const [municipio, setMunicipio] = useState('');
    const [estado, setEstado] = useState('');
    const [cargandoCP, setCargandoCP] = useState(false);

    // 🔄 CARGAR DATOS SI ES EDICIÓN
    useEffect(() => {
        if (modoEdicion && paciente) {
            setFormData({
                nombre: paciente.datos_personales.nombre,
                apellido_paterno: paciente.datos_personales.apellido_paterno,
                fecha_nacimiento: paciente.datos_personales.fecha_nacimiento,
                sexo: paciente.datos_personales.sexo,
                codigo_postal: paciente.direccion.codigo_postal,
                colonia: paciente.direccion.colonia,
                tipo_estudio: paciente.estudio.tipo
            });
            setMunicipio(paciente.direccion.municipio);
            setEstado(paciente.direccion.estado);
            if (paciente.direccion.codigo_postal) {
                buscarCodigoPostal(paciente.direccion.codigo_postal);
            }
        }
    }, [paciente, modoEdicion]);

    // 📍 BUSCAR CÓDIGO POSTAL
    const buscarCodigoPostal = async (cp) => {
        if (cp.length !== 5) return;
        try {
            setCargandoCP(true);
            const data = await obtenerInfoCodigoPostal(cp);
            setColonias(data.colonias);
            setMunicipio(data.municipio);
            setEstado(data.estado);
            if (data.colonias.length > 0 && !formData.colonia) {
                setFormData(prev => ({ ...prev, colonia: data.colonias[0] }));
            }
        } catch (error) {
            console.error('Error al buscar CP:', error);
            alert('No se encontró información para este código postal');
            setColonias([]);
            setMunicipio('');
            setEstado('');
        } finally {
            setCargandoCP(false);
        }
    };

    // 🔄 MANEJAR CAMBIOS EN INPUTS
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (name === 'codigo_postal' && value.length === 5) {
            buscarCodigoPostal(value);
        }
    };

    // 💾 ENVIAR FORMULARIO
    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.nombre || !formData.apellido_paterno || !formData.fecha_nacimiento) {
            alert('Por favor completa todos los campos obligatorios');
            return;
        }
        if (!formData.codigo_postal || !formData.colonia) {
            alert('Por favor ingresa un código postal válido y selecciona una colonia');
            return;
        }
        const datosPaciente = {
            datos_personales: {
                nombre: formData.nombre,
                apellido_paterno: formData.apellido_paterno,
                fecha_nacimiento: formData.fecha_nacimiento,
                sexo: formData.sexo
            },
            direccion: {
                codigo_postal: formData.codigo_postal,
                colonia: formData.colonia,
                municipio: municipio,
                estado: estado
            },
            tipo_estudio: formData.tipo_estudio
        };
        onGuardar(datosPaciente);
    };

    //? render
    return (
        <div className="formulario-modal">
            {/* HEADER */}
            <div className="formulario-header">
                <h2>{modoEdicion ? 'Editar Paciente' : 'Formulario Nuevo Paciente'}</h2>
                <button className="btn-cerrar" onClick={onCancelar} type="button">
                    <span className="material-symbols-outlined">close</span>
                </button>
            </div>

            {/* FORMULARIO */}
            <form onSubmit={handleSubmit} className="formulario">
                {/* DATOS PERSONALES */}
                <div className="seccion-formulario">
                    <h3>Datos personales</h3>
                    <div className="formulario-grid">
                        <div className="form-group">
                            <label>Nombre *</label>
                            <input
                                type="text"
                                name="nombre"
                                value={formData.nombre}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Apellido Paterno *</label>
                            <input
                                type="text"
                                name="apellido_paterno"
                                value={formData.apellido_paterno}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Fecha de Nacimiento *</label>
                            <input
                                type="date"
                                name="fecha_nacimiento"
                                value={formData.fecha_nacimiento}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Sexo *</label>
                            <select
                                name="sexo"
                                value={formData.sexo}
                                onChange={handleChange}
                                required
                            >
                                <option value="M">Masculino</option>
                                <option value="F">Femenino</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* DIRECCIÓN */}
                <div className="seccion-formulario">
                    <h3>Dirección</h3>
                    <div className="formulario-grid">
                        <div className="form-group">
                            <label>Código Postal</label>
                            <input
                                type="text"
                                name="codigo_postal"
                                value={formData.codigo_postal}
                                onChange={handleChange}
                                maxLength="5"
                                pattern="[0-9]{5}"
                            />
                            {cargandoCP && <small className="loading-text">Buscando...</small>}
                        </div>

                        <div className="form-group">
                            <label>Colonia *</label>
                            <select
                                name="colonia"
                                value={formData.colonia}
                                onChange={handleChange}
                                disabled={colonias.length === 0}
                                required
                            >
                                <option value="">Selecciona una colonia</option>
                                {colonias.map((col, idx) => (
                                    <option key={idx} value={col}>{col}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Municipio</label>
                            <input
                                type="text"
                                value={municipio}
                                disabled
                                placeholder="Se llenará automáticamente"
                            />
                        </div>

                        <div className="form-group">
                            <label>Estado</label>
                            <input
                                type="text"
                                value={estado}
                                disabled
                                placeholder="Se llenará automáticamente"
                            />
                        </div>
                    </div>
                </div>

                {/* TIPO DE ESTUDIO */}
                <div className="seccion-formulario">
                    <h3>Tipo de Estudio</h3>
                    <div className="form-group">
                        <label>Estudio a Realizar</label>
                        <select
                            name="tipo_estudio"
                            value={formData.tipo_estudio}
                            onChange={handleChange}
                            required
                        >
                            <option value="biometria_hematica">Biometría Hemática</option>
                            <option value="quimica_sanguinea">Química Sanguínea</option>
                            <option value="examen_orina">Examen General de Orina</option>
                        </select>
                    </div>
                </div>

                {/* BOTONES */}
                <div className="formulario-footer">
                    <button type="button" className="btn-secondary" onClick={onCancelar}>
                        Cancelar
                    </button>
                    <button type="submit" className="btn-primary">
                        {modoEdicion ? 'Actualizar' : 'Guardar'}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default FormularioPaciente
