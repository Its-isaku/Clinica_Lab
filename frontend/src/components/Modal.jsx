//?  imports
import '../styles/Modal.css';


//? Modal component
function Modal({ children, onClose }) {  
//? variables & states


//? functions & handlers


//? render
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-contenido" onClick={(e) => e.stopPropagation()}>
                {children}
            </div>
        </div>
    )
}

export default Modal
