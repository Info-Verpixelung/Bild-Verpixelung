// UI state management functions
import { state } from './state.js';

export function updateDeleteAllButtonVisibility() {
    const deleteAllButton = document.getElementById("delete-all-button");
    if (!deleteAllButton) return;
    
    if (state.uploadedFiles.length > 0) {
        deleteAllButton.classList.add("visible");
    } else {
        deleteAllButton.classList.remove("visible");
    }
}

export function updatePreviewButtonState() {
    const previewButton = document.getElementById("preview-button");
    if (!previewButton) return;
    
    previewButton.disabled = state.uploadedFiles.length === 0;
}

export function refreshImagePreviews() {
    // Placeholder - actual refresh is done in files.js
}
