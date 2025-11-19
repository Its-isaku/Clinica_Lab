//?  imports
import '../styles/TablaPacientes.css'
import Icon from './Icon';


//? TablaPacientes component
function TablaPacientes() {  
//? variables & states


//? functions & handlers


//? render
    return (
        <>
            <div className='Table_Container'>
                <div className='Table_title'>
                    <h2>Pacientes Registrados</h2>
                </div>
                <div className='Table_Content'>
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
                            <tr>
                                <td>ID</td>
                                <td>Nombre Completo</td>
                                <td>Edad</td>
                                <td>Sexo</td>
                                <td>Estudio</td>
                                <td>Fecha</td>
                                <td>
                                    <div className='ActionBtns'>
                                        <button className='SeeBtn'><Icon name="Visibility" size={28}/></button>
                                        <button className='EditBtn'><Icon name="edit" size={28}/></button>
                                        <button className='DeleteBtn'><Icon name="Delete" size={28}/></button>
                                    </div>
                                </td>                            
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    )
}

export default TablaPacientes