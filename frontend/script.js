document.addEventListener("DOMContentLoaded", () => {
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

    let uploadedFiles = []; // To store the files (as {name, type, dataURL} objects) for processing
    let dbAvailable = true; // Track if IndexedDB is working
    let userWarnedAboutStorage = false; // Only warn once per session
    let dragCounter = 0; // Track drag enter/leave to handle nested elements
    let db = null; // IndexedDB reference
    const detectApiUrl = "http://localhost:5001/api/v1/detect";

    // IndexedDB setup
    function initIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open("ImageAnonymizer", 1);
            
            request.onerror = () => {
                console.error("IndexedDB initialization failed:", request.error);
                dbAvailable = false;
                reject(request.error);
            };
            
            request.onsuccess = () => {
                db = request.result;
                console.log("IndexedDB initialized successfully");
                resolve(db);
            };
            
            request.onupgradeneeded = (event) => {
                const database = event.target.result;
                // Create object store if it doesn't exist
                if (!database.objectStoreNames.contains("uploadedImages")) {
                    // Don't use keyPath, let us manage the array structure ourselves
                    database.createObjectStore("uploadedImages");
                    console.log("Object store created");
                }
            };
        });
    }

    // IndexedDB functions
    function saveImagesToIndexedDB() {
        if (!dbAvailable || !db) {
            return Promise.resolve(); // Skip if DB unavailable
        }

        return new Promise((resolve) => {
            try {
                const transaction = db.transaction(["uploadedImages"], "readwrite");
                const store = transaction.objectStore("uploadedImages");
                
                // Clear old data first
                const clearRequest = store.clear();
                
                clearRequest.onsuccess = () => {
                    // Store the entire array as a single object with key "images"
                    const putRequest = store.put(uploadedFiles, "images");
                    
                    putRequest.onerror = () => {
                        console.error("Put error:", putRequest.error);
                        
                        // Check if it's a quota exceeded error
                        if (putRequest.error && putRequest.error.name === 'QuotaExceededError') {
                            dbAvailable = false;
                            
                            // Warn user once
                            if (!userWarnedAboutStorage) {
                                userWarnedAboutStorage = true;
                                alert("Warnung: Der Browser-Speicher ist voll. Ihre Bilder bleiben nur für diese Sitzung erhalten und gehen beim Neuladen verloren.\n\nTipp: Verarbeiten Sie die aktuellen Bilder und laden Sie dann neue hoch.");
                            }
                        }
                    };
                };
                
                transaction.onerror = () => {
                    console.error("Transaction error:", transaction.error);
                    resolve();
                };
                
                transaction.oncomplete = () => {
                    console.log(`Images saved to IndexedDB (${uploadedFiles.length} files)`);
                    resolve();
                };
            } catch (e) {
                console.error("Error saving to IndexedDB:", e);
                dbAvailable = false;
                resolve();
            }
        });
    }

    function loadImagesFromIndexedDB() {
        return new Promise((resolve) => {
            if (!dbAvailable || !db) {
                resolve();
                return;
            }

            try {
                const transaction = db.transaction(["uploadedImages"], "readonly");
                const store = transaction.objectStore("uploadedImages");
                const request = store.get("images");
                
                request.onsuccess = () => {
                    const data = request.result;
                    if (data && Array.isArray(data) && data.length > 0) {
                        uploadedFiles = data;
                        refreshImagePreviews(); // Display loaded images and update visibility
                        console.log(`Loaded ${uploadedFiles.length} images from IndexedDB`);
                    }
                    resolve();
                };
                
                request.onerror = () => {
                    console.error("Error loading from IndexedDB:", request.error);
                    resolve();
                };
            } catch (e) {
                console.error("Error loading from IndexedDB:", e);
                resolve();
            }
        });
    }

    // Initialize IndexedDB and load images
    initIndexedDB()
        .then(() => loadImagesFromIndexedDB())
        .catch((err) => {
            console.error("Failed to initialize IndexedDB, using session-only mode:", err);
            dbAvailable = false;
        })
        .then(() => {
            // Set dark mode as default (after DB initialized)
            document.body.classList.add("dark-mode");
            themeSwitch.checked = true;
            console.log("App initialized successfully");
        });

    // For compatibility, use IndexedDB save instead of localStorage
    const saveImagesToLocalStorage = saveImagesToIndexedDB;

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
        
        // Hide overlay on drop
        dragCounter = 0;
        dragDropOverlay.classList.remove("active");
        
        handleFiles(e.dataTransfer.files);
    });

    // Drag and drop overlay visual feedback
    document.body.addEventListener("dragenter", (e) => {
        e.preventDefault();
        dragCounter++;
        if (dragCounter === 1) {
            dragDropOverlay.classList.add("active");
        }
    });

    document.body.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dragCounter--;
        if (dragCounter === 0) {
            dragDropOverlay.classList.remove("active");
        }
    });

    // Global drag and drop for the entire website (except drop-zone, handled above)
    document.body.addEventListener("dragover", (e) => {
        e.preventDefault(); // Prevent default to allow drop
    });

    document.body.addEventListener("drop", (e) => {
        e.preventDefault();
        // Hide overlay on drop
        dragCounter = 0;
        dragDropOverlay.classList.remove("active");
        
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
                    updatePreviewButtonState();
                    saveImagesToLocalStorage().catch(err => console.error("Error saving image:", err)); // Save after each new file is read
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
        img.style.cursor = "pointer";
        img.title = "Klicken für große Ansicht";
        
        // Click handler for lightbox
        img.addEventListener("click", () => {
            openLightbox(index);
        });

        const deleteButton = document.createElement("span");
        deleteButton.classList.add("delete-image-button");
        deleteButton.innerHTML = "&times;"; // \"x\" icon
        deleteButton.title = "Bild entfernen";
        deleteButton.addEventListener("click", () => {
            removeImagePreview(index);
        });

        // Add loading bar container
        const loadingBarContainer = document.createElement("div");
        loadingBarContainer.classList.add("loading-bar-container");
        loadingBarContainer.style.display = "none";
        
        const loadingBar = document.createElement("div");
        loadingBar.classList.add("loading-bar-fill");
        loadingBarContainer.appendChild(loadingBar);
        
        // Add checkmark overlay
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

    function removeImagePreview(index) {
        uploadedFiles.splice(index, 1); // Remove file from array
        saveImagesToLocalStorage().catch(err => console.error("Error saving after removal:", err)); // Save after removal
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
        
        // Update delete-all button visibility
        updateDeleteAllButtonVisibility();

        // Update preview button state
        updatePreviewButtonState();
    }

    // Easing function for smooth non-linear animation
    function easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    // Start loading bar animation (fills to 75% in 2-3 seconds)
    function startLoadingAnimation(previewElement) {
        const loadingBarContainer = previewElement.querySelector(".loading-bar-container");
        const loadingBar = previewElement.querySelector(".loading-bar-fill");
        
        loadingBarContainer.style.display = "block";
        loadingBar.style.width = "0%";
        
        const targetProgress = 0.75; // 75%
        const animationDuration = Math.random() * 1000 + 2000; // 2-3 seconds in ms
        const startTime = performance.now();
        let animationId = null;

        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / animationDuration, 1);
            
            // Apply easing function
            const easedProgress = easeInOutCubic(progress);
            const currentWidth = easedProgress * targetProgress * 100;
            
            loadingBar.style.width = currentWidth + "%";
            
            if (progress < 1) {
                animationId = requestAnimationFrame(animate);
            } else {
                // Store animation state for later completion
                previewElement._loadingAnimationId = null;
                previewElement._loadingProgress = targetProgress;
            }
        }
        
        animationId = requestAnimationFrame(animate);
        previewElement._loadingAnimationId = animationId;
        previewElement._loadingStartTime = startTime;
        previewElement._loadingDuration = animationDuration;
        previewElement._targetProgress = targetProgress;
        
        return animationId;
    }

    // Complete loading bar animation (fill to 100% and show checkmark)
    function completeLoadingAnimation(previewElement) {
        const loadingBar = previewElement.querySelector(".loading-bar-fill");
        const checkmarkOverlay = previewElement.querySelector(".checkmark-overlay");
        
        // Cancel any ongoing animation
        if (previewElement._loadingAnimationId) {
            cancelAnimationFrame(previewElement._loadingAnimationId);
        }
        
        // Ensure transition is set BEFORE changing width
        loadingBar.style.transition = "width 0.4s ease-out";
        
        // Force reflow to ensure transition is applied
        void loadingBar.offsetHeight;
        
        // Fill to 100% quickly
        loadingBar.style.width = "100%";
        
        // Show checkmark after bar animation completes
        setTimeout(() => {
            checkmarkOverlay.style.display = "flex";
            
            // Hide bar and checkmark after 1.5 seconds
            setTimeout(() => {
                const loadingBarContainer = previewElement.querySelector(".loading-bar-container");
                loadingBarContainer.style.opacity = "0";
                checkmarkOverlay.style.opacity = "0";
                
                setTimeout(() => {
                    loadingBarContainer.style.display = "none";
                    checkmarkOverlay.style.display = "none";
                    loadingBarContainer.style.opacity = "1";
                    checkmarkOverlay.style.opacity = "1";
                    loadingBar.style.transition = "none";
                    loadingBar.style.width = "0%";
                }, 300);
            }, 1500);
        }, 400);
    }

    // Draw detection boxes on canvas and return new image DataURL
    function drawDetectionsOnImage(imageDataURL, detections) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                // Create canvas with same dimensions as image
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                
                const ctx = canvas.getContext('2d');
                
                // Draw original image on canvas
                ctx.drawImage(img, 0, 0);
                
                // Draw detection boxes
                ctx.strokeStyle = '#00ff00'; // Bright green
                ctx.lineWidth = 3;
                ctx.font = 'bold 16px Arial';
                ctx.fillStyle = '#00ff00';
                
                if (detections && detections.length > 0) {
                    detections.forEach((detection) => {
                        // x, y sind der Mittelpunkt, w, h sind Breite/Höhe
                        const x = detection.x;
                        const y = detection.y;
                        const w = detection.w;
                        const h = detection.h;
                        
                        // Berechne linke obere Ecke
                        const rectX = x - w / 2;
                        const rectY = y - h / 2;
                        
                        // Zeichne Rechteck
                        ctx.strokeRect(rectX, rectY, w, h);
                        
                        // Zeichne Type-Label oben auf der Box
                        if (detection.type) {
                            const labelText = detection.type;
                            const textMetrics = ctx.measureText(labelText);
                            const textWidth = textMetrics.width;
                            
                            // Background für Text
                            ctx.fillStyle = '#00ff00';
                            ctx.fillRect(
                                rectX, 
                                rectY - 25, 
                                textWidth + 8, 
                                20
                            );
                            
                            // Text selbst
                            ctx.fillStyle = '#000000';
                            ctx.fillText(labelText, rectX + 4, rectY - 8);
                        }
                    });
                }
                
                // Convert canvas to DataURL
                const newImageDataURL = canvas.toDataURL();
                resolve(newImageDataURL);
            };
            img.src = imageDataURL;
        });
    }

    function updateDeleteAllButtonVisibility() {
        if (uploadedFiles.length > 0) {
            deleteAllButton.classList.add("visible");
        } else {
            deleteAllButton.classList.remove("visible");
        }
    }

    function updatePreviewButtonState() {
        if (!previewButton) {
            return;
        }
        previewButton.disabled = uploadedFiles.length === 0;
    }

    // Preview processing handler (send images to backend)
    previewButton.addEventListener("click", async () => {
        if (uploadedFiles.length === 0) {
            return;
        }

        previewButton.disabled = true;
        const originalText = previewButton.textContent;
        previewButton.textContent = "⏳ Verarbeitung läuft...";
        const subject = censorshipSubjectSelect.value; // e.g., faces | eyes | body

        for (const [index, imageObj] of uploadedFiles.entries()) {
            try {
                // Get the preview element for this image
                const previewElement = imagePreviewGrid.querySelector(`[data-file-index="${index}"]`);
                if (previewElement) {
                    // Start loading animation
                    startLoadingAnimation(previewElement);
                }

                const payload = {
                    subject,
                    image: imageObj.dataURL,
                    filename: imageObj.name,
                    type: imageObj.type
                };

                const response = await fetch(detectApiUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    console.error(`Preview request failed for image ${index + 1}:`, response.status);
                    continue;
                }

                const data = await response.json();
                console.log(`Preview response for image ${index + 1}:`, data);

                // Draw detections on image and update preview
                if (data.objects && data.objects.length > 0) {
                    const imageWithDetections = await drawDetectionsOnImage(
                        imageObj.dataURL,
                        data.objects
                    );
                    
                    // Update the preview image with detections
                    if (previewElement) {
                        const imgElement = previewElement.querySelector('img');
                        if (imgElement) {
                            imgElement.src = imageWithDetections;
                        }
                    }
                    
                    // Store the detection image in memory for later use
                    imageObj.previewImage = imageWithDetections;
                    imageObj.detections = data.objects;
                }

                // Complete loading animation
                if (previewElement) {
                    completeLoadingAnimation(previewElement);
                }
            } catch (error) {
                console.error(`Preview request error for image ${index + 1}:`, error);
            }
        }

        // Restore button text and state
        previewButton.textContent = originalText;
        updatePreviewButtonState();
    });

    // Delete all images handler
    deleteAllButton.addEventListener("click", () => {
        if (uploadedFiles.length === 0) {
            return;
        }

        const confirmDelete = confirm(`Möchten Sie wirklich alle ${uploadedFiles.length} Bild${uploadedFiles.length > 1 ? 'er' : ''} löschen?`);
        
        if (confirmDelete) {
            uploadedFiles = [];
            saveImagesToLocalStorage().catch(err => console.error("Error clearing images:", err));
            refreshImagePreviews();
            
            // Clear output preview
            Array.from(outputPreviewGrid.children).forEach(child => {
                if (child.classList.contains("image-preview-item")) {
                    outputPreviewGrid.removeChild(child);
                }
            });
            downloadButton.disabled = true;
        }
    });

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

    // ============================================
    // LIGHTBOX FUNCTIONALITY
    // ============================================
    
    const lightboxModal = document.getElementById("lightbox-modal");
    const lightboxImage = document.getElementById("lightbox-image");
    const lightboxClose = document.getElementById("lightbox-close");
    const lightboxPrev = document.getElementById("lightbox-prev");
    const lightboxNext = document.getElementById("lightbox-next");
    const lightboxCounter = document.getElementById("lightbox-counter");
    
    let currentLightboxIndex = 0;
    
    function openLightbox(index) {
        if (uploadedFiles.length === 0) return;
        
        currentLightboxIndex = index;
        updateLightboxImage();
        lightboxModal.classList.add("active");
        document.body.style.overflow = "hidden"; // Prevent scrolling
    }
    
    function closeLightbox() {
        lightboxModal.classList.remove("active");
        document.body.style.overflow = ""; // Re-enable scrolling
    }
    
    function updateLightboxImage() {
        const imageObj = uploadedFiles[currentLightboxIndex];
        if (!imageObj) return;
        
        // Use preview image if available (with detections), otherwise use original
        const imageToShow = imageObj.previewImage || imageObj.dataURL;
        lightboxImage.src = imageToShow;
        
        // Update counter
        lightboxCounter.textContent = `${currentLightboxIndex + 1} / ${uploadedFiles.length}`;
        
        // Show/hide navigation buttons
        lightboxPrev.style.display = uploadedFiles.length > 1 ? "flex" : "none";
        lightboxNext.style.display = uploadedFiles.length > 1 ? "flex" : "none";
    }
    
    function showPreviousImage() {
        currentLightboxIndex = (currentLightboxIndex - 1 + uploadedFiles.length) % uploadedFiles.length;
        updateLightboxImage();
    }
    
    function showNextImage() {
        currentLightboxIndex = (currentLightboxIndex + 1) % uploadedFiles.length;
        updateLightboxImage();
    }
    
    // Event listeners
    lightboxClose.addEventListener("click", closeLightbox);
    lightboxPrev.addEventListener("click", showPreviousImage);
    lightboxNext.addEventListener("click", showNextImage);
    
    // Close on background click
    lightboxModal.addEventListener("click", (e) => {
        if (e.target === lightboxModal) {
            closeLightbox();
        }
    });
    
    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
        if (!lightboxModal.classList.contains("active")) return;
        
        if (e.key === "Escape") {
            closeLightbox();
        } else if (e.key === "ArrowLeft") {
            showPreviousImage();
        } else if (e.key === "ArrowRight") {
            showNextImage();
        }
    });
});
