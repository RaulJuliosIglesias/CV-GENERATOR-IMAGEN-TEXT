import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
    // baseURL intentionally left empty to use relative paths (proxied by Vite)
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getModels = async () => {
    const response = await api.get('/api/models');
    return response.data;
};

export const getConfig = async () => {
    const response = await api.get('/api/config');
    return response.data;
};

export const generateBatch = async (params) => {
    // Extract keys to prevent sending them in body (optional, but cleaner)
    const { apiKeys, ...body } = params;

    const headers = {};
    if (apiKeys?.openRouter) headers['X-OpenRouter-Key'] = apiKeys.openRouter;
    if (apiKeys?.krea) headers['X-Krea-Key'] = apiKeys.krea;

    const response = await api.post('/api/generate', body, { headers });
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

export const deleteTask = async (taskId) => {
    const response = await api.delete(`/api/task/${taskId}`);
    return response.data;
};

export const healthCheck = async () => {
    const response = await api.get('/api/health');
    return response.data;
};

/**
 * Download multiple CVs as a ZIP file
 * @param {Object} options - Download options
 * @param {string[]} options.filenames - Optional list of specific HTML filenames to download (takes precedence)
 * @param {string[]} options.batchIds - Optional list of batch IDs to download (null = all files)
 * @param {boolean} options.includeHtml - Include HTML files in ZIP
 * @param {boolean} options.includeAvatars - Include avatar images in ZIP
 * @returns {Promise<Blob>} ZIP file as Blob
 */
export const downloadZip = async (options = {}) => {
    const { 
        filenames = null, 
        batchIds = null, 
        includeHtml = false, 
        includeAvatars = false 
    } = options;
    
    const response = await api.post(
        '/api/download-zip',
        {
            filenames: filenames,
            batch_ids: batchIds,
            include_html: includeHtml,
            include_avatars: includeAvatars
        },
        {
            responseType: 'blob', // Important: receive as blob for file download
        }
    );
    
    return response.data;
};

// Get PDF/HTML URL for viewing - files are now in /html/ subdirectory
// Get PDF/HTML URL for viewing
// Get PDF/HTML URL for viewing
export const getPdfUrl = (filename) => {
    // The filename from the API is likely the HTML filename (e.g. ID__Name__Role.html)
    // We need to serve the PDF version from /api/files/pdf/ID__Name__Role.pdf
    const base = filename.replace(/\.(html|pdf)$/, '');
    return `/api/files/pdf/${base}.pdf`;
};

export const getHtmlUrl = (filename) => {
    const base = filename.replace(/\.(html|pdf)$/, '');
    // Serve HTML from /api/files/html/ID__Name__Role.html
    return `/api/files/html/${base}.html`;
};

export default api;
