/**
 * Theme Service - Gestión persistente de tema oscuro/claro
 */

const THEME_KEY = 'cv-generator-theme';
const THEMES = {
    DARK: 'dark',
    LIGHT: 'light',
    SYSTEM: 'system'
};

/**
 * Obtiene el tema guardado o el preferido del sistema
 */
export function getStoredTheme() {
    try {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored && Object.values(THEMES).includes(stored)) {
            return stored;
        }
    } catch (error) {
        console.error('Error reading theme from localStorage:', error);
    }
    return THEMES.SYSTEM;
}

/**
 * Guarda el tema seleccionado
 */
export function saveTheme(theme) {
    try {
        localStorage.setItem(THEME_KEY, theme);
        return true;
    } catch (error) {
        console.error('Error saving theme to localStorage:', error);
        return false;
    }
}

/**
 * Aplica el tema al documento
 */
export function applyTheme(theme) {
    const root = document.documentElement;
    const actualTheme = theme === THEMES.SYSTEM 
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? THEMES.DARK : THEMES.LIGHT)
        : theme;
    
    root.setAttribute('data-theme', actualTheme);
    root.classList.remove('dark', 'light');
    root.classList.add(actualTheme);
    
    return actualTheme;
}

/**
 * Inicializa el tema al cargar la página
 */
export function initTheme() {
    const theme = getStoredTheme();
    applyTheme(theme);
    
    // Listen for system theme changes if using system theme
    if (theme === THEMES.SYSTEM) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = () => applyTheme(THEMES.SYSTEM);
        mediaQuery.addEventListener('change', handleChange);
        
        // Return cleanup function
        return () => mediaQuery.removeEventListener('change', handleChange);
    }
    
    return () => {};
}

/**
 * Obtiene el tema actual aplicado
 */
export function getCurrentTheme() {
    const root = document.documentElement;
    return root.getAttribute('data-theme') || THEMES.DARK;
}

export { THEMES };
