//?  imports
import '../styles/Icon.css';

/**
 ** Componente Icon para usar Material Symbols de Google
 ** 
 ** @param {string} name - Nombre del ícono (ej: "add", "person", "delete")
 ** @param {number} size - Tamaño en píxeles (default: 24)
 ** @param {boolean} filled - Si el ícono debe estar relleno (default: false)
 ** @param {string} className - Clases CSS adicionales
 ** 
 ** Ejemplos de uso:
 ** <Icon name="add" />
 ** <Icon name="person" size={32} />
 ** <Icon name="favorite" filled />
 ** <Icon name="delete" className="custom-class" />
 */

const Icon = ({ name, size = 24, filled = false, className = '' }) => {
const iconClass = filled ? 'material-symbols-outlined filled' : 'material-symbols-outlined';

    return (
        <span 
        className={`${iconClass} ${className}`}
        style={{ fontSize: `${size}px` }}
        >
        {name}
        </span>
    );
};

export default Icon;