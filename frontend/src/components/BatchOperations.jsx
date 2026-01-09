import { useState } from 'react';
import { Trash2, Download, Archive, CheckSquare, Square } from 'lucide-react';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { deleteFile, getPdfUrl } from '../lib/api';
import { downloadZip } from '../lib/api';
import { toast } from 'sonner';

/**
 * BatchOperations - Componente para operaciones en lote sobre archivos
 */
export default function BatchOperations() {
    const files = useGenerationStore(s => s.files);
    const loadFiles = useGenerationStore(s => s.loadFiles);
    const allTasks = useGenerationStore(s => s.allTasks);
    const stopGeneration = useGenerationStore(s => s.stopGeneration);
    const clearQueue = useGenerationStore(s => s.clearQueue);

    const [selectedFiles, setSelectedFiles] = useState(new Set());
    const [isProcessing, setIsProcessing] = useState(false);

    const allSelected = selectedFiles.size === files.length && files.length > 0;
    const someSelected = selectedFiles.size > 0 && selectedFiles.size < files.length;

    const toggleSelectAll = () => {
        if (allSelected) {
            setSelectedFiles(new Set());
        } else {
            setSelectedFiles(new Set(files.map(f => f.filename)));
        }
    };

    const toggleSelectFile = (filename) => {
        setSelectedFiles(prev => {
            const next = new Set(prev);
            if (next.has(filename)) {
                next.delete(filename);
            } else {
                next.add(filename);
            }
            return next;
        });
    };

    const handleBatchDelete = async () => {
        if (selectedFiles.size === 0) return;
        
        if (!confirm(`Delete ${selectedFiles.size} file(s)?`)) return;

        setIsProcessing(true);
        const toastId = toast.loading(`Deleting ${selectedFiles.size} files...`);

        try {
            const deletePromises = Array.from(selectedFiles).map(filename =>
                deleteFile(filename).catch(err => {
                    console.error(`Failed to delete ${filename}:`, err);
                    return { filename, error: err };
                })
            );

            const results = await Promise.all(deletePromises);
            const failed = results.filter(r => r && r.error);
            
            if (failed.length > 0) {
                toast.error(`Failed to delete ${failed.length} file(s)`, { id: toastId });
            } else {
                toast.success(`Deleted ${selectedFiles.size} file(s)`, { id: toastId });
            }

            setSelectedFiles(new Set());
            loadFiles();
        } catch (error) {
            toast.error('Batch delete failed', { id: toastId });
        } finally {
            setIsProcessing(false);
        }
    };

    const handleBatchDownload = async () => {
        if (selectedFiles.size === 0) return;

        setIsProcessing(true);
        const toastId = toast.loading(`Preparing ${selectedFiles.size} files for download...`);

        try {
            const filenames = Array.from(selectedFiles);
            const blob = await downloadZip({ filenames });
            
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `CVs_Batch_${Date.now()}.zip`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            toast.success(`Downloaded ${filenames.length} files`, { id: toastId });
        } catch (error) {
            toast.error('Batch download failed', { id: toastId });
        } finally {
            setIsProcessing(false);
        }
    };

    const handleStopGeneration = () => {
        if (confirm('Stop current generation?')) {
            stopGeneration();
            toast.info('Generation stopped');
        }
    };

    const handleClearQueue = () => {
        if (confirm('Clear all queued tasks?')) {
            clearQueue();
            toast.info('Queue cleared');
        }
    };

    const activeTasks = allTasks.filter(t => t.status === 'pending' || t.status === 'in_progress');

    return (
        <div className="border border-border/50 rounded-lg bg-card/50 p-3 space-y-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleSelectAll}
                        className="h-7 px-2 text-xs"
                    >
                        {allSelected ? (
                            <CheckSquare className="w-3 h-3 mr-1" />
                        ) : (
                            <Square className="w-3 h-3 mr-1" />
                        )}
                        {allSelected ? 'Deselect All' : 'Select All'}
                    </Button>
                    {selectedFiles.size > 0 && (
                        <span className="text-xs text-muted-foreground">
                            {selectedFiles.size} selected
                        </span>
                    )}
                </div>
            </div>

            {selectedFiles.size > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleBatchDownload}
                        disabled={isProcessing}
                        className="h-7 px-2 text-xs"
                    >
                        <Download className="w-3 h-3 mr-1" />
                        Download ({selectedFiles.size})
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleBatchDelete}
                        disabled={isProcessing}
                        className="h-7 px-2 text-xs text-red-400 hover:text-red-500"
                    >
                        <Trash2 className="w-3 h-3 mr-1" />
                        Delete ({selectedFiles.size})
                    </Button>
                </div>
            )}

            {activeTasks.length > 0 && (
                <div className="flex items-center gap-2 pt-2 border-t border-border/30">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleStopGeneration}
                        className="h-7 px-2 text-xs"
                    >
                        Stop Generation
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleClearQueue}
                        className="h-7 px-2 text-xs"
                    >
                        Clear Queue ({activeTasks.length})
                    </Button>
                </div>
            )}

            {/* File selection checkboxes - can be integrated into FileExplorer */}
            <div className="text-xs text-muted-foreground">
                Tip: Select files in the file list to perform batch operations
            </div>
        </div>
    );
}
