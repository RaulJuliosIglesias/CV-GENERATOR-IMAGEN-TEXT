import { useState, useCallback } from 'react';
import { downloadZip } from '../lib/api';
import { toast } from 'sonner';
import useGenerationStore from '../stores/useGenerationStore';

/**
 * Custom hook for downloading CVs as ZIP
 * Handles ZIP generation, download, and error management
 */
export function useDownloadZip() {
    const [isDownloading, setIsDownloading] = useState(false);
    const allTasks = useGenerationStore(s => s.allTasks);

    const downloadSelected = useCallback(async (options = {}) => {
        const {
            filenames = null,
            batchIds = null,
            includeHtml = false,
            includeAvatars = false
        } = options;

        setIsDownloading(true);
        const toastId = toast.loading('Preparing ZIP file...', { id: 'download-zip' });

        try {
            // Download ZIP
            const blob = await downloadZip({
                filenames,
                batchIds,
                includeHtml,
                includeAvatars
            });

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            // Generate filename with timestamp
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const fileCount = filenames ? filenames.length : 'all';
            link.download = `CVs_${fileCount}_${timestamp}.zip`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            toast.success(`Downloaded ${fileCount} CV${fileCount !== 1 ? 's' : ''} as ZIP`, { id: toastId });
        } catch (error) {
            console.error('Failed to download ZIP:', error);
            toast.error(
                error.response?.data?.detail || 'Failed to download ZIP file',
                { id: toastId }
            );
        } finally {
            setIsDownloading(false);
        }
    }, []);

    // Legacy function for backward compatibility
    const downloadAll = useCallback(async (options = {}) => {
        const {
            batchIds = null,
            includeHtml = false,
            includeAvatars = false
        } = options;

        // If no batchIds provided, get all from completed tasks
        let finalBatchIds = batchIds;
        if (!finalBatchIds) {
            const completedTasks = allTasks.filter(t => t.status === 'complete');
            finalBatchIds = [...new Set(completedTasks.map(t => t.batch_id).filter(Boolean))];
            // If still empty, use null to download ALL files
            if (finalBatchIds.length === 0) {
                finalBatchIds = null;
            }
        }

        return downloadSelected({
            filenames: null,
            batchIds: finalBatchIds,
            includeHtml,
            includeAvatars
        });
    }, [allTasks, downloadSelected]);

    return {
        downloadSelected,
        downloadAll, // Legacy support
        isDownloading
    };
}

