var V_max;
var n = 0;
var intervalo;

function getFileExtension(filename) {
    return (/[.]/.exec(filename)) ? /[^.]+$/.exec(filename)[0] : undefined;
}

function esVideo(archivo) {
    var extension = getFileExtension(archivo);
    return (extension == "mp4");
}

function visualizador(vector, id) {
    var idElegido = `#${id}`;
    let galeria = document.querySelector(idElegido);
    var imagenes = galeria.querySelector('.Diapositiva');
    var video = galeria.querySelector('.video');
    var contEle = galeria.querySelector('#contador');

    // Establecer el valor de V_max al inicio
    V_max = vector.length;

    function avanzarImagen() {
        n = (n + 1) % V_max;
        mostrarImagen();
    }

    function mostrarImagen() {
        var cont = `${n + 1}/${V_max}`;
        contEle.textContent = cont;

        if (esVideo(vector[n]) == false) {
            imagenes.style.zIndex = 9;
            video.style.zIndex = 7;
            imagenes.src = vector[n];
        } else {
            video.style.zIndex = 9;
            imagenes.style.zIndex = 7;
            video.src = vector[n];
        }
    }
    
    function iniciarIntervalo() {
        intervalo = setInterval(avanzarImagen, 8000); // Cambio de imagen cada 3 segundos
    }

    iniciarIntervalo();
}
