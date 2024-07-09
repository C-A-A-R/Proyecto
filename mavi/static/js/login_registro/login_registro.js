const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Evento para abrir form de registro
signUpButton.addEventListener('click', () =>
  container.classList.add('right-panel-active')
);

// Evento para regresar al form de iniciar sesión
signInButton.addEventListener('click', () =>
  container.classList.remove('right-panel-active')
);

// function mensaje(message) {
//   alert(message);
// }

function mostrarAlertaConPlantilla(mensaje, rutaPlantilla) {
  // Obtener la plantilla HTML
  fetch(rutaPlantilla)
    .then(respuesta => respuesta.text())
    .then(codigoHTML => {
      // Crear un contenedor temporal para la plantilla
      const contenedorPlantilla = document.createElement('div');
      contenedorPlantilla.innerHTML = codigoHTML;

      // Buscar el elemento párrafo dentro de la plantilla
      const elementoParrafo = contenedorPlantilla.querySelector('p');

      // Insertar el texto del mensaje en el párrafo
      elementoParrafo.textContent = mensaje;

      // Agregar el contenido de la plantilla al cuerpo
      document.body.appendChild(contenedorPlantilla);

      // Agregar una clase al contenedor de la plantilla para el estilo
      contenedorPlantilla.classList.add('alerta');

      // Opcionalmente, agrega un botón de cierre o funcionalidad para ocultar la alerta
      // ...

      // Mostrar la alerta
      contenedorPlantilla.style.display = 'block';
    })
    .catch(error => console.error('Error al obtener la plantilla:', error));
}
