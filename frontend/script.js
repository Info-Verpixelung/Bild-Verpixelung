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

    let uploadedFiles = []; // To store the files (as {name, type, dataURL} objects) for processing
    let localStorageAvailable = true; // Track if localStorage is working
    let userWarnedAboutStorage = false; // Only warn once per session

    // Local storage functions
    function saveImagesToLocalStorage() {
        if (!localStorageAvailable) {
            return; // Skip saving if localStorage is full/unavailable
        }

        try {
            const dataToSave = JSON.stringify(uploadedFiles);
            localStorage.setItem("uploadedImages", dataToSave);
        } catch (e) {
            console.error("Error saving to local storage:", e);
            
            // Check if it's a quota exceeded error
            if (e.name === 'QuotaExceededError' || e.code === 22) {
                localStorageAvailable = false;
                
                // Warn user once
                if (!userWarnedAboutStorage) {
                    userWarnedAboutStorage = true;
                    alert("Warnung: Der Browser-Speicher ist voll. Ihre Bilder bleiben nur für diese Sitzung erhalten und gehen beim Neuladen verloren.\n\nTipp: Verarbeiten Sie die aktuellen Bilder und laden Sie dann neue hoch.");
                }
                
                // Try to clear old data to make room
                try {
                    localStorage.removeItem("uploadedImages");
                    // Try saving again with current files
                    localStorage.setItem("uploadedImages", JSON.stringify(uploadedFiles));
                    localStorageAvailable = true;
                    console.log("Successfully cleared old data and saved new images");
                } catch (retryError) {
                    console.error("Could not save even after clearing:", retryError);
                }
            }
        }
    }

    function loadImagesFromLocalStorage() {
        try {
            const savedImages = localStorage.getItem("uploadedImages");
            if (savedImages) {
                uploadedFiles = JSON.parse(savedImages);
                refreshImagePreviews(); // Display loaded images and update visibility
            }
        } catch (e) {
            console.error("Error loading from local storage:", e);
            uploadedFiles = []; // Clear corrupted data
            // Try to clear corrupted data
            try {
                localStorage.removeItem("uploadedImages");
            } catch (clearError) {
                console.error("Could not clear corrupted data:", clearError);
            }
        }
        // updatePlaceholderVisibility(); // Not needed here anymore
    }

    // Initial load from local storage
    loadImagesFromLocalStorage();

    // Set dark mode as default
    document.body.classList.add("dark-mode");
    themeSwitch.checked = true;

    themeSwitch.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode");
    });

    // Existing click for drop zone
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    // Drop zone specific drag and drop handlers
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.style.backgroundColor = document.body.classList.contains("dark-mode") ? "#3a3a3a" : "#edf6f9";
        handleFiles(e.dataTransfer.files);
    });

    // Global drag and drop for the entire website (except drop-zone, handled above)
    document.body.addEventListener("dragover", (e) => {
        e.preventDefault(); // Prevent default to allow drop
    });

    document.body.addEventListener("drop", (e) => {
        e.preventDefault();
        // Only handle if NOT dropped on drop-zone (drop-zone has its own handler)
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

    function handleFiles(files) {
        // Clear only output preview items, leave placeholder text intact
        Array.from(outputPreviewGrid.children).forEach(child => {
            if (child.classList.contains("image-preview-item")) {
                outputPreviewGrid.removeChild(child);
            }
        });
        downloadButton.disabled = true;

        const filesToAdd = Array.from(files).slice(0, 10 - uploadedFiles.length);

        filesToAdd.forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedFiles.push({ name: file.name, type: file.type, dataURL: e.target.result });
                saveImagesToLocalStorage(); // Save after each new file is read
                refreshImagePreviews(); // Re-render all previews after adding a new one
            };
            reader.readAsDataURL(file);
        });

        // If no files were processed (e.g., all slots full), ensure visibility is updated
        // updatePlaceholderVisibility(); // Not needed here anymore
    }

    // Modified to accept dataURL directly
    function displayImagePreview(imageObj, index) {
        const previewWrapper = document.createElement("div");
        previewWrapper.classList.add("image-preview-item");
        previewWrapper.dataset.fileIndex = index; // Store index for deletion

        const img = document.createElement("img");
        img.src = imageObj.dataURL;
        img.alt = "Bildvorschau";

        const deleteButton = document.createElement("span");
        deleteButton.classList.add("delete-image-button");
        deleteButton.innerHTML = "&times;"; // \"x\" icon
        deleteButton.title = "Bild entfernen";
        deleteButton.addEventListener("click", () => {
            removeImagePreview(index);
        });

        previewWrapper.appendChild(img);
        previewWrapper.appendChild(deleteButton);
        imagePreviewGrid.appendChild(previewWrapper);
    }

    function removeImagePreview(index) {
        uploadedFiles.splice(index, 1); // Remove file from array
        saveImagesToLocalStorage(); // Save after removal
        refreshImagePreviews(); // Re-render previews to update indices and display
        // outputPreviewGrid.innerHTML = ""; // Not needed here anymore as refreshPreviews handles it
        downloadButton.disabled = true;
    }

    function refreshImagePreviews() {
        // Clear only image preview items, leave placeholder text intact
        Array.from(imagePreviewGrid.children).forEach(child => {
            if (child.classList.contains("image-preview-item")) {
                imagePreviewGrid.removeChild(child);
            }
        });

        // Clear only output preview items, leave placeholder text intact
        Array.from(outputPreviewGrid.children).forEach(child => {
            if (child.classList.contains("image-preview-item")) {
                outputPreviewGrid.removeChild(child);
            }
        });

        uploadedFiles.forEach((imageObj, index) => {
            displayImagePreview(imageObj, index);
        });

        // Update visibility based on actual content of the grids
        imagePreviewText.style.display = imagePreviewGrid.querySelectorAll(".image-preview-item").length === 0 ? "block" : "none";
        outputPreviewText.style.display = outputPreviewGrid.querySelectorAll(".image-preview-item").length === 0 ? "block" : "none";
    }

    processButton.addEventListener("click", () => {
        if (uploadedFiles.length > 0) {
            // Clear only output preview items, leave placeholder text intact
            Array.from(outputPreviewGrid.children).forEach(child => {
                if (child.classList.contains("image-preview-item")) {
                    outputPreviewGrid.removeChild(child);
                }
            });

            outputPreviewText.style.display = "none"; // Hide output placeholder text during processing
            downloadButton.disabled = false;

            uploadedFiles.forEach((imageObj, index) => {
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

    // Initial state check for previews (redundant due to loadImagesFromLocalStorage and updatePlaceholderVisibility)
    // if (uploadedFiles.length === 0) {
    //     imagePreviewText.style.display = "block";
    //     outputPreviewText.style.display = "block";
    // }
});
