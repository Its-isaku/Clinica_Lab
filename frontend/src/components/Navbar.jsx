//?  imports
import '../styles/Navbar.css'
import Icon from './Icon';


//? Navbar component
function Navbar() {  
//? variables & states


//? functions & handlers
const handleClick = (e) => {
    const button = e.currentTarget;
    button.classList.remove('pulse');
    //* Force reflow para reiniciar la animación
    void button.offsetWidth;
    button.classList.add('pulse');
};

//? render
    return (
        <>
            <div className="Navbar_Container">
                <div className='Navbar_Left'>
                    <img src="/logo.png" alt="Biogen Logo" />
                    <div className='Left_text'>
                        <h1>Biogen</h1>
                        <p>Laboratorio Clínico</p>
                    </div>
                </div>

                <button className='Navbar_Center' onClick={handleClick}><Icon name="add_circle" size={32} /> Agregar Paciente</button>
                
                <div className='Navbar_Right'>
                    <Icon name="ecg_heart" size={48} />
                    <div className='Right_text'>
                        <h2>Dra. Dannaly</h2>
                        <p>Admin</p>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Navbar
