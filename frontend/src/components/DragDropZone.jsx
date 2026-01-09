import { useFileDrop } from '../hooks/useDragAndDrop';
import { Upload, FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { importConfig } from '../lib/storage';
import useGenerationStore from '../stores/useGenerationStore';
import { toast } from 'sonner';

/**
 * DragDropZone - Zona para arrastrar y soltar archivos de configuración
 */
export default function DragDropZone({ children, onImport }) {
    const setConfig = useGenerationStore(s => s.setConfig);

    const handleFileLoad = (content, filename) => {
        try {
            const importedConfig = importConfig(content);
            
            // Apply imported config
            Object.entries(importedConfig).forEach(([key, value]) => {
                setConfig(key, value);
            });

            toast.success(`Configuration imported from ${filename}`);
            
            if (onImport) {
                onImport(importedConfig);
            }
        } catch (error) {
            toast.error(`Failed to import: ${error.message}`);
        }
    };

    const { isDragging, dragHandlers } = useFileDrop(handleFileLoad);

    return (
        <div
            {...dragHandlers}
            className="relative"
        >
            {children}
            <AnimatePresence>
                {isDragging && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 bg-primary/20 backdrop-blur-sm flex items-center justify-center pointer-events-none"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-card border-2 border-dashed border-primary rounded-xl p-12 flex flex-col items-center gap-4 pointer-events-auto"
                        >
                            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                                <Upload className="w-8 h-8 text-primary" />
                            </div>
                            <div className="text-center">
                                <p className="text-lg font-semibold text-foreground">
                                    Drop configuration file here
                                </p>
                                <p className="text-sm text-muted-foreground mt-1">
                                    JSON configuration files only
                                </p>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
