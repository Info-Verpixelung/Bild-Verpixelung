// File handling functions
import { state, config } from './state.js';
import { saveImagesToIndexedDB } from './db.js';
import { updateDeleteAllButtonVisibility, updatePreviewButtonState } from './ui.js';

export function handleFiles(files) {
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    const outputPreviewGrid = document.getElementById("output-preview-grid");
    const downloadButton = document.getElementById("download-button");
    
    if (!imagePreviewGrid || !outputPreviewGrid || !downloadButton) return;

    // Clear output preview items
    Array.from(outputPreviewGrid.children).forEach(child => {
        if (child.classList.contains("image-preview-item")) {
            outputPreviewGrid.removeChild(child);
        }
    });
    downloadButton.disabled = true;

    const filesToAdd = Array.from(files).slice(0, config.maxFiles - state.uploadedFiles.length);

    filesToAdd.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            state.uploadedFiles.push({ 
                name: file.name, 
                type: file.type, 
                dataURL: e.target.result 
            });
            updatePreviewButtonState();
            saveImagesToIndexedDB();
            refreshImagePreviews();
        };
        reader.readAsDataURL(file);
    });
}

export function displayImagePreview(imageObj, index) {
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    if (!imagePreviewGrid) return;

    const openLightbox = window.openLightboxFunc;
    
    const previewWrapper = document.createElement("div");
    previewWrapper.classList.add("image-preview-item");
    previewWrapper.dataset.fileIndex = index;

    const img = document.createElement("img");
    img.src = imageObj.dataURL;
    img.alt = "Bildvorschau";
    img.style.cursor = "pointer";
    img.title = "Klicken für große Ansicht";
    
    img.addEventListener("click", () => {
        if (openLightbox) openLightbox(index);
    });

    const deleteButton = document.createElement("span");
    deleteButton.classList.add("delete-image-button");
    deleteButton.innerHTML = "&times;";
    deleteButton.title = "Bild entfernen";
    deleteButton.addEventListener("click", () => {
        removeImagePreview(index);
    });

    const loadingBarContainer = document.createElement("div");
    loadingBarContainer.classList.add("loading-bar-container");
    loadingBarContainer.style.display = "none";
    
    const loadingBar = document.createElement("div");
    loadingBar.classList.add("loading-bar-fill");
    loadingBarContainer.appendChild(loadingBar);
    
    const checkmarkOverlay = document.createElement("div");
    checkmarkOverlay.classList.add("checkmark-overlay");
    checkmarkOverlay.innerHTML = "✓";
    checkmarkOverlay.style.display = "none";

    previewWrapper.appendChild(img);
    previewWrapper.appendChild(loadingBarContainer);
    previewWrapper.appendChild(checkmarkOverlay);
    previewWrapper.appendChild(deleteButton);
    imagePreviewGrid.appendChild(previewWrapper);
}

export function removeImagePreview(index) {
    const downloadButton = document.getElementById("download-button");
    
    state.uploadedFiles.splice(index, 1);
    saveImagesToIndexedDB();
    refreshImagePreviews();
    if (downloadButton) downloadButton.disabled = true;
}

export function refreshImagePreviews() {
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    const outputPreviewGrid = document.getElementById("output-preview-grid");
    const imagePreviewText = document.querySelector("#image-preview-grid .image-preview-text");
    const outputPreviewText = document.querySelector("#output-preview-grid .image-preview-text");
    
    if (!imagePreviewGrid || !outputPreviewGrid) return;

    // Clear image preview items
    Array.from(imagePreviewGrid.children).forEach(child => {
        if (child.classList.contains("image-preview-item")) {
            imagePreviewGrid.removeChild(child);
        }
    });

    // Clear output preview items
    Array.from(outputPreviewGrid.children).forEach(child => {
        if (child.classList.contains("image-preview-item")) {
            outputPreviewGrid.removeChild(child);
        }
    });

    state.uploadedFiles.forEach((imageObj, index) => {
        displayImagePreview(imageObj, index);
    });

    if (imagePreviewText) {
        imagePreviewText.style.display = imagePreviewGrid.querySelectorAll(".image-preview-item").length === 0 ? "block" : "none";
    }
    if (outputPreviewText) {
        outputPreviewText.style.display = outputPreviewGrid.querySelectorAll(".image-preview-item").length === 0 ? "block" : "none";
    }
    
    updateDeleteAllButtonVisibility();
    updatePreviewButtonState();
}
