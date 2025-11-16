//?  imports
import Icon from './Icon';
import '../styles/TarjetasEstadisticas.css'


//? TarjetasEstadisticas component
function TarjetasEstadisticas() {  
//? variables & states


//? functions & handlers


//? render
    return (
        <>
            <div className='Cards_Container'>
                <div className='Welcome_text'>
                    <h2>Bienvenido de nuevo, Dra. Dannaly Astorga</h2>
                    <p>Aquí tienes un resumen de la actividad reciente en el laboratorio.</p>
                </div>
                
                <div className='Cards_Content'>
                    <div className='Card'>
                        <div className='Card_top'>
                            <div className='Card_icon Card_icon_primary'>
                                <Icon name="person" size={32} filled={false} />
                            </div>
                            <div className='Card_Percentage Good_Percentage'>+12%</div>
                        </div>
                        <div className='Card_bottom'>
                            <p>Total Pacientes</p>
                            <h2>1,247</h2>
                        </div>
                    </div>

                    <div className='Card'>
                        <div className='Card_top'>
                            <div className='Card_icon Card_icon_warning'>
                                <Icon name="assignment" size={32} filled={false} />
                            </div>
                            <div className='Card_Percentage Bad_Percentage'>-5%</div>
                        </div>
                        <div className='Card_bottom'>
                            <p>Estudios Pendientes</p>
                            <h2>23</h2>
                        </div>
                    </div>

                    <div className='Card'>
                        <div className='Card_top'>
                            <div className='Card_icon Card_icon_success'>
                                <Icon name="description" size={32} filled={false} />
                            </div>
                            <div className='Card_Percentage Good_Percentage'>+18%</div>
                        </div>
                        <div className='Card_bottom'>
                            <p>Completados hoy</p>
                            <h2>47</h2>
                        </div>
                    </div>

                    <div className='Card'>
                        <div className='Card_top'>
                            <div className='Card_icon Card_icon_info'>
                                <Icon name="monitor_heart" size={32} filled={false} />
                            </div>
                            <div className='Card_Percentage Good_Percentage'>En Tiempo</div>
                        </div>
                        <div className='Card_bottom'>
                            <p>En Proceso</p>
                            <h2>8</h2>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default TarjetasEstadisticas
