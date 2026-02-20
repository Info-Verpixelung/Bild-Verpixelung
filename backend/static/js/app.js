// Main application entry point
import { state, config } from './state.js';
import { initIndexedDB, loadImagesFromIndexedDB, saveImagesToIndexedDB } from './db.js';
import { handleFiles, refreshImagePreviews } from './files.js';
import { drawDetectionsOnImage } from './canvas.js';
import { startLoadingAnimation, completeLoadingAnimation } from './animations.js';
import { setupLightbox } from './lightbox.js';
import { updatePreviewButtonState } from './ui.js';

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const fileInput = document.getElementById("file-input");
    const dropZone = document.querySelector(".drop-zone");
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    const imagePreviewText = document.querySelector("#image-preview-grid .image-preview-text");
    const themeSwitch = document.getElementById("checkbox");
    const anonymizationTypeSelect = document.getElementById("anonymization-type");
    const censorshipSubjectSelect = document.getElementById("censorship-subject");
    const previewButton = document.getElementById("preview-button");
    const processButton = document.getElementById("process-button");
    const downloadButton = document.getElementById("download-button");
    const outputPreviewGrid = document.getElementById("output-preview-grid");
    const outputPreviewText = document.querySelector("#output-preview-grid .image-preview-text");
    const deleteAllButton = document.getElementById("delete-all-button");
    const dragDropOverlay = document.getElementById("drag-drop-overlay");

    // Setup lightbox and get open function
    const { openLightbox } = setupLightbox();
    
    // Store openLightbox globally for files.js to use
    window.openLightboxFunc = openLightbox;

    // Initialize IndexedDB and load images
    initIndexedDB()
        .then(() => loadImagesFromIndexedDB())
        .catch((err) => {
            console.error("Failed to initialize IndexedDB, using session-only mode:", err);
            state.dbAvailable = false;
        })
        .then(() => {
            document.body.classList.add("dark-mode");
            themeSwitch.checked = true;
            console.log("App initialized successfully");
            refreshImagePreviews();
        });

    // Theme switch
    themeSwitch.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode");
    });

    // Drop zone click
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    // Drop zone drag handlers
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.style.backgroundColor = document.body.classList.contains("dark-mode") ? "#3a3a3a" : "#edf6f9";
        state.dragCounter = 0;
        dragDropOverlay.classList.remove("active");
        handleFiles(e.dataTransfer.files);
    });

    // Global drag and drop
    document.body.addEventListener("dragenter", (e) => {
        e.preventDefault();
        state.dragCounter++;
        if (state.dragCounter === 1) {
            dragDropOverlay.classList.add("active");
        }
    });

    document.body.addEventListener("dragleave", (e) => {
        e.preventDefault();
        state.dragCounter--;
        if (state.dragCounter === 0) {
            dragDropOverlay.classList.remove("active");
        }
    });

    document.body.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    document.body.addEventListener("drop", (e) => {
        e.preventDefault();
        state.dragCounter = 0;
        dragDropOverlay.classList.remove("active");
        
        if (!e.target.closest(".drop-zone")) {
            handleFiles(e.dataTransfer.files);
        }
    });

    // Click to upload in empty preview area
    imagePreviewGrid.addEventListener("click", (e) => {
        if (e.target === imagePreviewGrid || e.target === imagePreviewText) {
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", (e) => {
        handleFiles(e.target.files);
    });

    // Preview button handler
    previewButton.addEventListener("click", async () => {
        if (state.uploadedFiles.length === 0) return;

        previewButton.disabled = true;
        const originalText = previewButton.textContent;
        previewButton.textContent = "⏳ Verarbeitung läuft...";
        const subject = censorshipSubjectSelect.value;

        for (const [index, imageObj] of state.uploadedFiles.entries()) {
            try {
                const previewElement = imagePreviewGrid.querySelector(`[data-file-index="${index}"]`);
                if (previewElement) {
                    startLoadingAnimation(previewElement);
                }

                const payload = {
                    subject,
                    image: imageObj.dataURL,
                    filename: imageObj.name,
                    type: imageObj.type
                };

                const response = await fetch(config.detectApiUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    console.error(`Preview request failed for image ${index + 1}:`, response.status);
                    continue;
                }

                const data = await response.json();
                console.log(`Preview response for image ${index + 1}:`, data);

                if (data.objects && data.objects.length > 0) {
                    const imageWithDetections = await drawDetectionsOnImage(imageObj.dataURL, data.objects);
                    
                    if (previewElement) {
                        const imgElement = previewElement.querySelector('img');
                        if (imgElement) {
                            imgElement.src = imageWithDetections;
                        }
                    }
                    
                    imageObj.previewImage = imageWithDetections;
                    imageObj.detections = data.objects;
                }

                if (previewElement) {
                    completeLoadingAnimation(previewElement);
                }
            } catch (error) {
                console.error(`Preview request error for image ${index + 1}:`, error);
            }
        }

        previewButton.textContent = originalText;
        updatePreviewButtonState();
    });

    // Delete all button
    deleteAllButton.addEventListener("click", () => {
        if (state.uploadedFiles.length === 0) return;

        const confirmDelete = confirm(`Möchten Sie wirklich alle ${state.uploadedFiles.length} Bild${state.uploadedFiles.length > 1 ? 'er' : ''} löschen?`);
        
        if (confirmDelete) {
            state.uploadedFiles = [];
            saveImagesToIndexedDB();
            refreshImagePreviews();
            
            Array.from(outputPreviewGrid.children).forEach(child => {
                if (child.classList.contains("image-preview-item")) {
                    outputPreviewGrid.removeChild(child);
                }
            });
            downloadButton.disabled = true;
        }
    });

    // Process button handler
    processButton.addEventListener("click", () => {
        if (state.uploadedFiles.length > 0) {
            Array.from(outputPreviewGrid.children).forEach(child => {
                if (child.classList.contains("image-preview-item")) {
                    outputPreviewGrid.removeChild(child);
                }
            });

            outputPreviewText.style.display = "none";
            downloadButton.disabled = false;

            // Placeholder - actual processing not implemented
            state.uploadedFiles.forEach((imageObj, index) => {
                const anonymizationType = anonymizationTypeSelect.value;
                const censorshipSubject = censorshipSubjectSelect.value;
                console.log(`Processing image ${index + 1} with type: ${anonymizationType}, subject: ${censorshipSubject}`);

                const outputWrapper = document.createElement("div");
                outputWrapper.classList.add("image-preview-item");

                const img = document.createElement("img");
                img.src = "/static/icons/placeholder.png";
                img.alt = "Ausgabevorschau";

                outputWrapper.appendChild(img);
                outputPreviewGrid.appendChild(outputWrapper);
            });
        } else {
            alert("Bitte laden Sie zuerst Bilder hoch, um sie zu verarbeiten.");
        }
    });
});
