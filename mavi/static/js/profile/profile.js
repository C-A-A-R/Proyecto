// Funcionalidad para habilitar/deshabilitar campos cuando se presiona "Modificar"
const modifyBtn = document.getElementById('modify-btn');
const profileForm = document.getElementById('profile-form');
const editableFields = ['email', 'sector', 'codigo-operador', 'telefono'];
const nonEditableFields = ['nombre', 'apellidos', 'usuario'];

// Prevenir el envío del formulario si el botón aún dice "Modificar"
profileForm.addEventListener('submit', function (event) {
    if (modifyBtn.textContent === 'Modificar') {
        event.preventDefault(); // Evita el envío si el botón aún está en "Modificar"
    }
});

modifyBtn.addEventListener('click', function () {
    if (modifyBtn.textContent === 'Modificar') {
        // Primer clic: habilitar los campos para editar
        editableFields.forEach(function (fieldId) {
            const field = document.getElementById(fieldId);
            if (field.tagName === 'SELECT') {
                field.disabled = false;
            } else {
                field.readOnly = false;
            }
        });

        nonEditableFields.forEach(function (fieldId) {
            const field = document.getElementById(fieldId);
            field.classList.add('disabled-field');
        });

        // Cambiar el texto del botón a "Guardar", pero mantener el tipo "button"
        modifyBtn.textContent = 'Guardar';

    } else if (modifyBtn.textContent === 'Guardar') {
        // Segundo clic: validar el formulario antes de enviar
        if (validateForm()) {
            // Si la validación es correcta, cambiamos el tipo del botón a "submit"
            modifyBtn.setAttribute('type', 'submit');
            profileForm.submit();  // Enviamos el formulario manualmente
        } else {
            event.preventDefault(); // Prevenir el envío si la validación falla
        }
    }
});

// Función de validación del formulario
function validateForm() {
    let isValid = true;
    
    // Limpiar contenedor de errores
    const errorContainer = document.getElementById('error-container');
    errorContainer.innerHTML = ''; // Limpiar cualquier mensaje previo

    // Validar email
    const email = document.getElementById('email');
    if (!validateEmail(email.value)) {
        const emailError = document.createElement('div');
        emailError.classList.add('error-message');
        emailError.innerText = "El correo debe contener '@' y '.'";
        errorContainer.appendChild(emailError);
        isValid = false;
    }

    // Validar teléfono
    const telefono = document.getElementById('telefono');
    if (!validatePhone(telefono.value)) {
        const telefonoError = document.createElement('div');
        telefonoError.classList.add('error-message');
        telefonoError.innerText = "El número de teléfono solo debe contener números";
        errorContainer.appendChild(telefonoError);
        isValid = false;
    }

    return isValid;
}

// Función para validar el formato de email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Función para validar que el teléfono solo contenga números
function validatePhone(phone) {
    const phoneRegex = /^[0-9]+$/;
    return phoneRegex.test(phone);
}
