// Shared application state
// This module exports shared state and configuration used across the app

// Get current host dynamically (works on both localhost and mobile devices in same network)
const getApiBaseUrl = () => {
    const protocol = window.location.protocol;
    const host = window.location.host;
    return `${protocol}//${host}`;
};

export const state = {
    uploadedFiles: [],
    dbAvailable: true,
    userWarnedAboutStorage: false,
    dragCounter: 0,
    db: null,
    currentLightboxIndex: 0
};

export const config = {
    detectApiUrl: `${getApiBaseUrl()}/api/v1/detect`,
    maxFiles: 10
};

export function updateState(newState) {
    Object.assign(state, newState);
}
