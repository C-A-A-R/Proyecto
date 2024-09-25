// Función para actualizar el margin-top
function updateMarginTop() {
    var navbarHeight = document.querySelector('.navbar-dark').offsetHeight;
    document.getElementById('Diapositiva').style.marginTop = navbarHeight + 'px';
    document.getElementById('video').style.marginTop = navbarHeight + 'px';
}

// Espera a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", function() {
    // Llama a la función inicialmente
    updateMarginTop();

    // Observa cambios en el tamaño de la navbar
    var navbar = document.querySelector('.navbar-dark');
    var observer = new MutationObserver(updateMarginTop);

    // Configura el observador para detectar cambios en los atributos y el contenido del hijo
    observer.observe(navbar, { attributes: true, childList: true, subtree: true });

    // También puedes agregar un evento de redimensionamiento para manejar cambios en el tamaño de la ventana
    window.addEventListener('resize', updateMarginTop);
});
