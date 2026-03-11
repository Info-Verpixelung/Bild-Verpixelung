// UI state management functions
import { state } from './state.js';

export function updateDeleteAllButtonVisibility() {
    const deleteAllButton = document.getElementById("delete-all-button");
    const outputDeleteAllButton = document.getElementById("output-delete-all-button");
    
    if (!deleteAllButton && !outputDeleteAllButton) return;

    if (deleteAllButton) {
        if (state.uploadedFiles.length > 0) {
            deleteAllButton.classList.add("visible");
        } else {
            deleteAllButton.classList.remove("visible");
        }
    }

    if (outputDeleteAllButton) {
        if (state.outputFiles.length > 0) {
            outputDeleteAllButton.classList.add("visible");
        } else {
            outputDeleteAllButton.classList.remove("visible");
        }
    }
}

export function updatePreviewButtonState() {
    const previewButton = document.getElementById("preview-button");
    if (!previewButton) return;
    
    previewButton.disabled = state.uploadedFiles.length === 0;
}

export function updateProcessButtonState() {
    const processButton = document.getElementById("process-button");
    if (!processButton) return;

    processButton.disabled = state.uploadedFiles.length === 0;
}

export function refreshImagePreviews() {
    // Placeholder - actual refresh is done in files.js
}
