function displayFile(input) {
    const uploadHistory = document.getElementById('upload-history');
    const files = input.files;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function (e) {
            const mediaElement = document.createElement(file.type.startsWith('video') ? 'video' : 'img');
            mediaElement.src = e.target.result;
            mediaElement.className = 'upload-item';
            if (file.type.startsWith('video')) {
                mediaElement.controls = true; // Agrega controles de video
            }
            uploadHistory.appendChild(mediaElement);
        };

        reader.readAsDataURL(file);
    }
}
