/**
 * Storage Service - Persistencia de configuración y templates
 * Maneja localStorage con validación, migración y manejo de errores
 */

const STORAGE_KEYS = {
    CONFIG: 'cv-generator-config',
    TEMPLATES: 'cv-generator-templates',
    STATS: 'cv-generator-stats',
    THEME: 'cv-generator-theme'
};

const CONFIG_VERSION = 1;

/**
 * Obtiene un valor del localStorage de forma segura
 */
function getStorageItem(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        if (item === null) return defaultValue;
        return JSON.parse(item);
    } catch (error) {
        console.error(`Error reading from localStorage (${key}):`, error);
        return defaultValue;
    }
}

/**
 * Guarda un valor en localStorage de forma segura
 */
function setStorageItem(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        if (error.name === 'QuotaExceededError') {
            console.error('localStorage quota exceeded. Clearing old data...');
            // Intentar limpiar datos antiguos
            clearOldData();
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (retryError) {
                console.error('Failed to save after cleanup:', retryError);
                return false;
            }
        }
        console.error(`Error writing to localStorage (${key}):`, error);
        return false;
    }
}

/**
 * Limpia datos antiguos cuando el storage está lleno
 */
function clearOldData() {
    // Limpiar stats antiguos (mantener solo últimos 30 días)
    const stats = getStorageItem(STORAGE_KEYS.STATS, {});
    if (stats.history) {
        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
        stats.history = stats.history.filter(entry => entry.timestamp > thirtyDaysAgo);
        setStorageItem(STORAGE_KEYS.STATS, stats);
    }
}

/**
 * Guarda la configuración actual
 */
export function saveConfig(config) {
    const configData = {
        version: CONFIG_VERSION,
        config: config,
        savedAt: Date.now()
    };
    return setStorageItem(STORAGE_KEYS.CONFIG, configData);
}

/**
 * Carga la configuración guardada
 */
export function loadConfig() {
    const data = getStorageItem(STORAGE_KEYS.CONFIG, null);
    if (!data) return null;
    
    // Migración de versiones (si es necesario en el futuro)
    if (data.version !== CONFIG_VERSION) {
        console.warn(`Config version mismatch. Current: ${CONFIG_VERSION}, Found: ${data.version}`);
        // Aquí se puede añadir lógica de migración
    }
    
    return data.config || null;
}

/**
 * Guarda un template
 */
export function saveTemplate(name, config, description = '') {
    const templates = loadTemplates();
    const template = {
        id: `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name,
        description,
        config,
        createdAt: Date.now(),
        updatedAt: Date.now()
    };
    
    templates.push(template);
    setStorageItem(STORAGE_KEYS.TEMPLATES, templates);
    return template;
}

/**
 * Carga todos los templates
 */
export function loadTemplates() {
    return getStorageItem(STORAGE_KEYS.TEMPLATES, []);
}

/**
 * Obtiene un template por ID
 */
export function getTemplate(id) {
    const templates = loadTemplates();
    return templates.find(t => t.id === id) || null;
}

/**
 * Actualiza un template existente
 */
export function updateTemplate(id, updates) {
    const templates = loadTemplates();
    const index = templates.findIndex(t => t.id === id);
    
    if (index === -1) {
        throw new Error(`Template with id ${id} not found`);
    }
    
    templates[index] = {
        ...templates[index],
        ...updates,
        updatedAt: Date.now()
    };
    
    setStorageItem(STORAGE_KEYS.TEMPLATES, templates);
    return templates[index];
}

/**
 * Elimina un template
 */
export function deleteTemplate(id) {
    const templates = loadTemplates();
    const filtered = templates.filter(t => t.id !== id);
    setStorageItem(STORAGE_KEYS.TEMPLATES, filtered);
    return filtered.length < templates.length;
}

/**
 * Exporta la configuración como JSON
 */
export function exportConfig(config) {
    const exportData = {
        version: CONFIG_VERSION,
        exportedAt: new Date().toISOString(),
        config: config
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cv-generator-config-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Importa configuración desde JSON
 */
export function importConfig(jsonString) {
    try {
        const data = JSON.parse(jsonString);
        
        // Validar estructura
        if (!data.config || typeof data.config !== 'object') {
            throw new Error('Invalid config structure');
        }
        
        // Validar campos requeridos
        const requiredFields = ['qty', 'genders', 'ethnicities', 'origins', 'roles'];
        const missingFields = requiredFields.filter(field => !(field in data.config));
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }
        
        return data.config;
    } catch (error) {
        if (error instanceof SyntaxError) {
            throw new Error('Invalid JSON format');
        }
        throw error;
    }
}

/**
 * Guarda estadísticas
 */
export function saveStats(stats) {
    return setStorageItem(STORAGE_KEYS.STATS, stats);
}

/**
 * Carga estadísticas
 */
export function loadStats() {
    return getStorageItem(STORAGE_KEYS.STATS, {
        totalGenerations: 0,
        successful: 0,
        failed: 0,
        totalTime: 0,
        history: [],
        byRole: {},
        byDate: []
    });
}

/**
 * Añade una entrada de generación a las estadísticas
 */
export function trackGeneration(generationData) {
    const stats = loadStats();
    
    stats.totalGenerations += 1;
    if (generationData.status === 'success') {
        stats.successful += 1;
    } else {
        stats.failed += 1;
    }
    
    if (generationData.duration) {
        stats.totalTime += generationData.duration;
    }
    
    // Track por rol
    if (generationData.role) {
        stats.byRole[generationData.role] = (stats.byRole[generationData.role] || 0) + 1;
    }
    
    // Añadir a historial
    stats.history.push({
        ...generationData,
        timestamp: Date.now()
    });
    
    // Mantener solo últimos 1000 registros
    if (stats.history.length > 1000) {
        stats.history = stats.history.slice(-1000);
    }
    
    saveStats(stats);
    return stats;
}

/**
 * Calcula estadísticas agregadas
 */
export function getStatsSummary() {
    const stats = loadStats();
    const avgTime = stats.totalGenerations > 0 
        ? stats.totalTime / stats.totalGenerations 
        : 0;
    const successRate = stats.totalGenerations > 0
        ? (stats.successful / stats.totalGenerations) * 100
        : 0;
    
    return {
        ...stats,
        averageTime: Math.round(avgTime * 10) / 10,
        successRate: Math.round(successRate * 10) / 10
    };
}

/**
 * Limpia todos los datos guardados (útil para testing o reset)
 */
export function clearAllStorage() {
    Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
    });
}

/**
 * Obtiene el tamaño aproximado del storage usado
 */
export function getStorageSize() {
    let total = 0;
    for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
            total += localStorage[key].length + key.length;
        }
    }
    return total;
}
