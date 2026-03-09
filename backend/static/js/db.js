// IndexedDB functions for persistent storage
import { state } from './state.js';

export function initIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("ImageAnonymizer", 1);
        
        request.onerror = () => {
            console.error("IndexedDB initialization failed:", request.error);
            state.dbAvailable = false;
            reject(request.error);
        };
        
        request.onsuccess = () => {
            state.db = request.result;
            console.log("IndexedDB initialized successfully");
            resolve(state.db);
        };
        
        request.onupgradeneeded = (event) => {
            const database = event.target.result;
            if (!database.objectStoreNames.contains("uploadedImages")) {
                database.createObjectStore("uploadedImages");
                console.log("Object store created");
            }
        };
    });
}

export function saveImagesToIndexedDB() {
    if (!state.dbAvailable || !state.db) {
        return Promise.resolve();
    }

    return new Promise((resolve) => {
        try {
            const transaction = state.db.transaction(["uploadedImages"], "readwrite");
            const store = transaction.objectStore("uploadedImages");
            
            const clearRequest = store.clear();
            
            clearRequest.onsuccess = () => {
                const appState = {
                    uploadedFiles: state.uploadedFiles,
                    outputFiles: state.outputFiles
                };

                const putRequest = store.put(appState, "images");
                
                putRequest.onerror = () => {
                    console.error("Put error:", putRequest.error);
                    
                    if (putRequest.error && putRequest.error.name === 'QuotaExceededError') {
                        state.dbAvailable = false;
                        
                        if (!state.userWarnedAboutStorage) {
                            state.userWarnedAboutStorage = true;
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
                console.log(`Images saved to IndexedDB (${state.uploadedFiles.length} preview, ${state.outputFiles.length} output)`);
                resolve();
            };
        } catch (e) {
            console.error("Error saving to IndexedDB:", e);
            state.dbAvailable = false;
            resolve();
        }
    });
}

export function loadImagesFromIndexedDB() {
    return new Promise((resolve) => {
        if (!state.dbAvailable || !state.db) {
            resolve();
            return;
        }

        try {
            const transaction = state.db.transaction(["uploadedImages"], "readonly");
            const store = transaction.objectStore("uploadedImages");
            const request = store.get("images");
            
            request.onsuccess = () => {
                const data = request.result;
                if (Array.isArray(data)) {
                    state.uploadedFiles = data;
                    state.outputFiles = [];
                    console.log(`Loaded ${state.uploadedFiles.length} images from IndexedDB (legacy format)`);
                } else if (data && typeof data === "object") {
                    state.uploadedFiles = Array.isArray(data.uploadedFiles) ? data.uploadedFiles : [];
                    state.outputFiles = Array.isArray(data.outputFiles) ? data.outputFiles : [];
                    console.log(`Loaded ${state.uploadedFiles.length} preview and ${state.outputFiles.length} output images from IndexedDB`);
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
