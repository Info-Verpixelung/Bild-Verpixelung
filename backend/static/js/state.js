// Shared application state
// This module exports shared state and configuration used across the app

export const state = {
    uploadedFiles: [],
    dbAvailable: true,
    userWarnedAboutStorage: false,
    dragCounter: 0,
    db: null,
    currentLightboxIndex: 0
};

export const config = {
    detectApiUrl: "http://localhost:5001/api/v1/detect",
    maxFiles: 10
};

export function updateState(newState) {
    Object.assign(state, newState);
}
