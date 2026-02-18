// Lightbox modal functionality
import { state } from './state.js';

export function setupLightbox() {
    const lightboxModal = document.getElementById("lightbox-modal");
    const lightboxImage = document.getElementById("lightbox-image");
    const lightboxClose = document.getElementById("lightbox-close");
    const lightboxPrev = document.getElementById("lightbox-prev");
    const lightboxNext = document.getElementById("lightbox-next");
    const lightboxCounter = document.getElementById("lightbox-counter");
    
    function openLightbox(index) {
        if (state.uploadedFiles.length === 0) return;
        
        state.currentLightboxIndex = index;
        updateLightboxImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext);
        lightboxModal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
    
    function closeLightbox() {
        lightboxModal.classList.remove("active");
        document.body.style.overflow = "";
    }
    
    function updateLightboxImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext) {
        const imageObj = state.uploadedFiles[state.currentLightboxIndex];
        if (!imageObj) return;
        
        const imageToShow = imageObj.previewImage || imageObj.dataURL;
        lightboxImage.src = imageToShow;
        
        lightboxCounter.textContent = `${state.currentLightboxIndex + 1} / ${state.uploadedFiles.length}`;
        
        lightboxPrev.style.display = state.uploadedFiles.length > 1 ? "flex" : "none";
        lightboxNext.style.display = state.uploadedFiles.length > 1 ? "flex" : "none";
    }
    
    function showPreviousImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext) {
        state.currentLightboxIndex = (state.currentLightboxIndex - 1 + state.uploadedFiles.length) % state.uploadedFiles.length;
        updateLightboxImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext);
    }
    
    function showNextImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext) {
        state.currentLightboxIndex = (state.currentLightboxIndex + 1) % state.uploadedFiles.length;
        updateLightboxImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext);
    }
    
    // Event listeners
    lightboxClose.addEventListener("click", closeLightbox);
    lightboxPrev.addEventListener("click", () => showPreviousImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext));
    lightboxNext.addEventListener("click", () => showNextImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext));
    
    lightboxModal.addEventListener("click", (e) => {
        if (e.target === lightboxModal) {
            closeLightbox();
        }
    });
    
    document.addEventListener("keydown", (e) => {
        if (!lightboxModal.classList.contains("active")) return;
        
        if (e.key === "Escape") {
            closeLightbox();
        } else if (e.key === "ArrowLeft") {
            showPreviousImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext);
        } else if (e.key === "ArrowRight") {
            showNextImage(lightboxImage, lightboxCounter, lightboxPrev, lightboxNext);
        }
    });
    
    return { openLightbox };
}
