import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API functions
export const getModels = async () => {
    const response = await api.get('/api/models');
    return response.data;
};

export const generateBatch = async (params) => {
    const response = await api.post('/api/generate', params);
    return response.data;
};

export const getStatus = async () => {
    const response = await api.get('/api/status');
    return response.data;
};

export const getBatchStatus = async (batchId) => {
    const response = await api.get(`/api/status/${batchId}`);
    return response.data;
};

export const getFiles = async () => {
    const response = await api.get('/api/files');
    return response.data;
};

export const deleteFile = async (filename) => {
    const response = await api.delete(`/api/files/${filename}`);
    return response.data;
};

export const openFolder = async () => {
    const response = await api.post('/api/open-folder');
    return response.data;
};

export const clearAll = async () => {
    const response = await api.delete('/api/clear');
    return response.data;
};

export const healthCheck = async () => {
    const response = await api.get('/api/health');
    return response.data;
};

// Get PDF/HTML URL for viewing - files are now in /html/ subdirectory
export const getPdfUrl = (filename) => {
    return `http://localhost:8000/html/${filename}`;
};

export default api;
