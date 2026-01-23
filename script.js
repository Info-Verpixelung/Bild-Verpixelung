document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.querySelector('.drop-zone');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewText = document.querySelector('#image-preview-container .image-preview-text');
    const themeSwitch = document.getElementById('checkbox');

    // Set dark mode as default
    document.body.classList.add('dark-mode');
    themeSwitch.checked = true;

    themeSwitch.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode');
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            displayImage(file);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = document.body.classList.contains('dark-mode') ? '#4a4a4a' : '#e0f7fa';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = document.body.classList.contains('dark-mode') ? '#3a3a3a' : '#edf6f9';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = document.body.classList.contains('dark-mode') ? '#3a3a3a' : '#edf6f9';
        const file = e.dataTransfer.files[0];
        if (file) {
            displayImage(file);
        }
    });

    function displayImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            imagePreviewText.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    const processButton = document.getElementById('process-button');
    const downloadButton = document.getElementById('download-button');
    const outputPreview = document.getElementById('output-preview');
    const outputPreviewText = document.querySelector('#output-preview-container .image-preview-text');

    processButton.addEventListener('click', () => {
        if (imagePreview.src && imagePreview.style.display === 'block') {
            // Simulate processing by showing a placeholder image
            outputPreview.src = 'https://via.placeholder.com/400x200.png?text=Anonymisiertes+Bild';
            outputPreview.style.display = 'block';
            outputPreviewText.style.display = 'none';
            downloadButton.disabled = false;
        } else {
            alert('Bitte laden Sie zuerst ein Bild hoch.');
        }
    });
});
