import { useEffect } from 'react';

/**
 * useKeyboardShortcuts - Hook para manejar atajos de teclado globales
 */
export function useKeyboardShortcuts(shortcuts) {
    useEffect(() => {
        const handleKeyDown = (event) => {
            // Ignore if typing in input/textarea
            if (
                event.target.tagName === 'INPUT' ||
                event.target.tagName === 'TEXTAREA' ||
                event.target.isContentEditable
            ) {
                return;
            }

            const key = event.key.toLowerCase();
            const ctrl = event.ctrlKey || event.metaKey;
            const shift = event.shiftKey;
            const alt = event.altKey;

            // Build key string
            let keyString = '';
            if (ctrl) keyString += 'ctrl+';
            if (shift) keyString += 'shift+';
            if (alt) keyString += 'alt+';
            keyString += key;

            // Find matching shortcut
            const shortcut = shortcuts.find(s => s.key === keyString);
            if (shortcut) {
                event.preventDefault();
                shortcut.handler(event);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts]);
}

/**
 * Predefined shortcuts for common actions
 */
export const COMMON_SHORTCUTS = {
    GENERATE: { key: 'ctrl+enter', description: 'Start generation' },
    STOP: { key: 'ctrl+shift+s', description: 'Stop generation' },
    SEARCH: { key: 'ctrl+k', description: 'Focus search' },
    CLEAR: { key: 'ctrl+shift+c', description: 'Clear queue' },
    REFRESH: { key: 'ctrl+r', description: 'Refresh files' },
    THEME: { key: 'ctrl+shift+t', description: 'Toggle theme' },
    SETTINGS: { key: 'ctrl+,', description: 'Open settings' },
};
