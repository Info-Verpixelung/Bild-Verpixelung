document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("file-input");
    const dropZone = document.querySelector(".drop-zone");
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    const imagePreviewText = document.querySelector("#image-preview-grid .image-preview-text");
    const themeSwitch = document.getElementById("checkbox");
    const anonymizationTypeSelect = document.getElementById("anonymization-type");
    const censorshipSubjectSelect = document.getElementById("censorship-subject");
    const processButton = document.getElementById("process-button");
    const downloadButton = document.getElementById("download-button");
    const outputPreviewGrid = document.getElementById("output-preview-grid");
    const outputPreviewText = document.querySelector("#output-preview-grid .image-preview-text");

    let uploadedFiles = []; // To store the files for processing

    // Set dark mode as default
    document.body.classList.add("dark-mode");
    themeSwitch.checked = true;

    themeSwitch.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode");
    });

    fileInput.addEventListener("change", (e) => {
        handleFiles(e.target.files);
    });

    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = document.body.classList.contains("dark-mode") ? "#4a4a4a" : "#e0f7fa";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.backgroundColor = document.body.classList.contains("dark-mode") ? "#3a3a3a" : "#edf6f9";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = document.body.classList.contains("dark-mode") ? "#3a3a3a" : "#edf6f9";
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        uploadedFiles = []; // Clear previous files
        imagePreviewGrid.innerHTML = ""; // Clear previous previews
        outputPreviewGrid.innerHTML = ""; // Clear previous outputs
        downloadButton.disabled = true;

        if (files.length > 0) {
            imagePreviewText.style.display = "none";
            outputPreviewText.style.display = "block"; // Show output text again

            const filesToProcess = Array.from(files).slice(0, 10); // Limit to 10 files

            filesToProcess.forEach(file => {
                uploadedFiles.push(file);
                displayImagePreview(file);
            });
        } else {
            imagePreviewText.style.display = "block";
            outputPreviewText.style.display = "block";
        }
    }

    function displayImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewWrapper = document.createElement("div");
            previewWrapper.classList.add("image-preview-item");

            const img = document.createElement("img");
            img.src = e.target.result;
            img.alt = "Bildvorschau";

            previewWrapper.appendChild(img);
            imagePreviewGrid.appendChild(previewWrapper);
        };
        reader.readAsDataURL(file);
    }

    processButton.addEventListener("click", () => {
        if (uploadedFiles.length > 0) {
            outputPreviewGrid.innerHTML = ""; // Clear previous output previews
            outputPreviewText.style.display = "none";
            downloadButton.disabled = false;

            uploadedFiles.forEach((file, index) => {
                // Simulate processing by showing a placeholder image for each uploaded image
                const anonymizationType = anonymizationTypeSelect.value;
                const censorshipSubject = censorshipSubjectSelect.value;
                console.log(`Processing image ${index + 1} with type: ${anonymizationType}, subject: ${censorshipSubject}`);

                const outputWrapper = document.createElement("div");
                outputWrapper.classList.add("image-preview-item");

                const img = document.createElement("img");
                img.src = `https://via.placeholder.com/400x200.png?text=Anonymisiertes+Bild+${index + 1}`;
                img.alt = "Ausgabevorschau";

                outputWrapper.appendChild(img);
                outputPreviewGrid.appendChild(outputWrapper);
            });
        } else {
            alert("Bitte laden Sie zuerst Bilder hoch, um sie zu verarbeiten.");
        }
    });

    // Initial state check for previews
    if (uploadedFiles.length === 0) {
        imagePreviewText.style.display = "block";
        outputPreviewText.style.display = "block";
    }
});
