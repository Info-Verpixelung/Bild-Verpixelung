// Canvas and detection box rendering
export function drawDetectionsOnImage(imageDataURL, detections) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            
            const ctx = canvas.getContext('2d');
            
            ctx.drawImage(img, 0, 0);
            
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 3;
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = '#00ff00';
            
            if (detections && detections.length > 0) {
                detections.forEach((detection) => {
                    const x = detection.x;
                    const y = detection.y;
                    const w = detection.w;
                    const h = detection.h;
                    
                    const rectX = x - w / 2;
                    const rectY = y - h / 2;
                    
                    ctx.strokeRect(rectX, rectY, w, h);
                    
                    if (detection.type) {
                        const labelText = detection.type;
                        const textMetrics = ctx.measureText(labelText);
                        const textWidth = textMetrics.width;
                        
                        ctx.fillStyle = '#00ff00';
                        ctx.fillRect(
                            rectX, 
                            rectY - 25, 
                            textWidth + 8, 
                            20
                        );
                        
                        ctx.fillStyle = '#000000';
                        ctx.fillText(labelText, rectX + 4, rectY - 8);
                    }
                });
            }
            
            const newImageDataURL = canvas.toDataURL();
            resolve(newImageDataURL);
        };
        img.src = imageDataURL;
    });
}
