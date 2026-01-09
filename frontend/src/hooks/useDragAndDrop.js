import { useState, useCallback, useEffect } from 'react';

/**
 * useDragAndDrop - Hook para manejar drag and drop de archivos
 */
export function useDragAndDrop(onDrop, accept = ['.json']) {
    const [isDragging, setIsDragging] = useState(false);
    const [dragCounter, setDragCounter] = useState(0);

    const handleDragEnter = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragCounter(prev => prev + 1);
        
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            setIsDragging(true);
        }
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragCounter(prev => {
            const newCounter = prev - 1;
            if (newCounter === 0) {
                setIsDragging(false);
            }
            return newCounter;
        });
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        setDragCounter(0);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const files = Array.from(e.dataTransfer.files);
            const validFiles = files.filter(file => {
                const ext = '.' + file.name.split('.').pop().toLowerCase();
                return accept.includes(ext) || accept.includes('*');
            });

            if (validFiles.length > 0) {
                onDrop(validFiles);
            }
        }
    }, [onDrop, accept]);

    return {
        isDragging,
        dragHandlers: {
            onDragEnter: handleDragEnter,
            onDragLeave: handleDragLeave,
            onDragOver: handleDragOver,
            onDrop: handleDrop
        }
    };
}

/**
 * useFileDrop - Hook específico para arrastrar archivos de configuración
 */
export function useFileDrop(onFileLoad) {
    const handleDrop = useCallback((files) => {
        if (files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    onFileLoad(e.target.result, file.name);
                } catch (error) {
                    console.error('Error reading file:', error);
                }
            };
            reader.readAsText(file);
        }
    }, [onFileLoad]);

    return useDragAndDrop(handleDrop, ['.json']);
}
