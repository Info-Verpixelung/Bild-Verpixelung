// Main application entry point
import { state, config } from './state.js';
import { initIndexedDB, loadImagesFromIndexedDB, saveImagesToIndexedDB } from './db.js';
import { handleFiles, refreshImagePreviews } from './files.js';
import { drawDetectionsOnImage } from './canvas.js';
import { startLoadingAnimation, completeLoadingAnimation } from './animations.js';
import { setupLightbox } from './lightbox.js';
import { updatePreviewButtonState, updateProcessButtonState } from './ui.js';

function mapAnonymizationMode(frontendMode) {
    if (frontendMode === "blacken") return "black_bar";
    if (frontendMode === "blur") return "blur";
    return "pixel";
}

function toNumericBoxes(detections = []) {
    return detections.map((detection) => {
        const centerX = Number(detection.x) || 0;
        const centerY = Number(detection.y) || 0;
        const halfWidth = Math.max(1, Math.round((Number(detection.w) || 0) / 2));
        const halfHeight = Math.max(1, Math.round((Number(detection.h) || 0) / 2));
        return [centerX, centerY, halfWidth, halfHeight];
    });
}

function dataUrlToUint8Array(dataUrl) {
    const [, base64Data] = dataUrl.split(",");
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);

    for (let index = 0; index < binaryString.length; index += 1) {
        bytes[index] = binaryString.charCodeAt(index);
    }

    return bytes;
}

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
    const outputDeleteAllButton = document.getElementById("output-delete-all-button");
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
        previewButton.textContent = "Verarbeitung läuft...";
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
        updateProcessButtonState();
        saveImagesToIndexedDB();
    });

    function handleDeleteAllPreview() {
        if (state.uploadedFiles.length === 0) return;

        const confirmDelete = confirm(`Möchten Sie wirklich alle ${state.uploadedFiles.length} Bild${state.uploadedFiles.length > 1 ? 'er' : ''} löschen?`);
        
        if (confirmDelete) {
            state.uploadedFiles = [];
            saveImagesToIndexedDB();
            refreshImagePreviews();
            updateProcessButtonState();
        }
    }

    function handleDeleteAllOutput() {
        if (state.outputFiles.length === 0) return;

        const confirmDelete = confirm(`Möchten Sie wirklich alle ${state.outputFiles.length} anonymisierte${state.outputFiles.length > 1 ? 'n Bilder' : 's Bild'} löschen?`);

        if (confirmDelete) {
            state.outputFiles = [];
            saveImagesToIndexedDB();
            refreshImagePreviews();
            downloadButton.disabled = true;
        }
    }

    if (deleteAllButton) {
        deleteAllButton.addEventListener("click", handleDeleteAllPreview);
    }
    if (outputDeleteAllButton) {
        outputDeleteAllButton.addEventListener("click", handleDeleteAllOutput);
    }

    // Process button handler
    processButton.addEventListener("click", async () => {
        if (state.uploadedFiles.length === 0) {
            alert("Bitte laden Sie zuerst Bilder hoch, um sie zu verarbeiten.");
            return;
        }

        processButton.disabled = true;
        const originalText = processButton.textContent;
        processButton.textContent = "Anonymisierung läuft...";

        Array.from(outputPreviewGrid.children).forEach((child) => {
            if (child.classList.contains("image-preview-item")) {
                outputPreviewGrid.removeChild(child);
            }
        });

        outputPreviewText.style.display = "none";
        downloadButton.disabled = true;

        state.outputFiles = [];

        const mode = mapAnonymizationMode(anonymizationTypeSelect.value);
        let successCount = 0;

        for (const [index, imageObj] of state.uploadedFiles.entries()) {
            const detections = Array.isArray(imageObj.detections) ? imageObj.detections : [];
            const numericBoxes = toNumericBoxes(detections);

            try {
                const payload = {
                    image: imageObj.dataURL,
                    boxes: numericBoxes,
                    mode
                };

                const response = await fetch(config.censorApiUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    console.error(`Censor request failed for image ${index + 1}:`, response.status);
                    continue;
                }

                const data = await response.json();

                if (!data || data.status !== "success" || !data.censored_image) {
                    console.error(`Invalid censor response for image ${index + 1}:`, data);
                    continue;
                }

                state.outputFiles.push({
                    name: imageObj.name,
                    type: "image/png",
                    dataURL: data.censored_image
                });
                successCount += 1;
            } catch (error) {
                console.error(`Censor request error for image ${index + 1}:`, error);
            }
        }

        refreshImagePreviews();

        if (successCount === 0) {
            outputPreviewText.style.display = "block";
            alert("Keine Bilder konnten anonymisiert werden. Bitte prüfen Sie die Backend-Logs.");
        }

        downloadButton.disabled = successCount === 0;
        processButton.textContent = originalText;
        updateProcessButtonState();
        saveImagesToIndexedDB();
    });

    downloadButton.addEventListener("click", () => {
        const processedImages = state.outputFiles;

        if (processedImages.length === 0) {
            alert("Keine anonymisierten Bilder zum Herunterladen vorhanden.");
            return;
        }

        if (!window.JSZip) {
            alert("ZIP-Bibliothek konnte nicht geladen werden.");
            return;
        }

        const originalText = downloadButton.textContent;
        downloadButton.disabled = true;
        downloadButton.textContent = "ZIP wird erstellt...";

        const zip = new window.JSZip();
        const zipFolder = zip.folder("anonymisierte_bilder");

        processedImages.forEach((imageObj, index) => {
            const originalName = imageObj.name || `bild_${index + 1}`;
            const baseName = originalName.includes(".")
                ? originalName.substring(0, originalName.lastIndexOf("."))
                : originalName;

            zipFolder.file(`${baseName}_anonymisiert.png`, dataUrlToUint8Array(imageObj.dataURL));
        });

        zip.generateAsync({ type: "blob" })
            .then((zipBlob) => {
                const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
                const link = document.createElement("a");
                const blobUrl = URL.createObjectURL(zipBlob);

                link.href = blobUrl;
                link.download = `anonymisierte_bilder_${timestamp}.zip`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(blobUrl);
            })
            .catch((error) => {
                console.error("ZIP creation failed:", error);
                alert("ZIP-Datei konnte nicht erstellt werden.");
            })
            .finally(() => {
                downloadButton.textContent = originalText;
                downloadButton.disabled = state.outputFiles.length === 0;
            });
    });
});
