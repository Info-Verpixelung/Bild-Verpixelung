// Loading animations

function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export function startLoadingAnimation(previewElement) {
    const loadingBarContainer = previewElement.querySelector(".loading-bar-container");
    const loadingBar = previewElement.querySelector(".loading-bar-fill");
    
    loadingBarContainer.style.display = "block";
    loadingBar.style.width = "0%";
    
    const targetProgress = 0.75;
    const animationDuration = Math.random() * 1000 + 2000;
    const startTime = performance.now();
    let animationId = null;

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / animationDuration, 1);
        
        const easedProgress = easeInOutCubic(progress);
        const currentWidth = easedProgress * targetProgress * 100;
        
        loadingBar.style.width = currentWidth + "%";
        
        if (progress < 1) {
            animationId = requestAnimationFrame(animate);
        } else {
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

export function completeLoadingAnimation(previewElement) {
    const loadingBar = previewElement.querySelector(".loading-bar-fill");
    const checkmarkOverlay = previewElement.querySelector(".checkmark-overlay");
    
    if (previewElement._loadingAnimationId) {
        cancelAnimationFrame(previewElement._loadingAnimationId);
    }
    
    loadingBar.style.transition = "width 0.4s ease-out";
    void loadingBar.offsetHeight;
    
    loadingBar.style.width = "100%";
    
    setTimeout(() => {
        checkmarkOverlay.style.display = "flex";
        
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
