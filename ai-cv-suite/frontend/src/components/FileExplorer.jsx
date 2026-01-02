import { useEffect } from 'react';
import { FileText, Trash2, FolderOpen, ExternalLink, RefreshCw, HardDrive } from 'lucide-react';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { deleteFile, openFolder, getPdfUrl } from '../lib/api';

export default function FileExplorer() {
    const { files, loadFiles, isLoadingFiles } = useGenerationStore();

    useEffect(() => {
        loadFiles();
    }, []);

    const handleOpenFile = (filename) => {
        window.open(getPdfUrl(filename), '_blank');
    };

    const handleDeleteFile = async (filename) => {
        if (confirm(`Are you sure you want to delete ${filename}?`)) {
            try {
                await deleteFile(filename);
                loadFiles();
            } catch (error) {
                console.error('Failed to delete file:', error);
            }
        }
    };

    const handleOpenFolder = async () => {
        try {
            await openFolder();
        } catch (error) {
            console.error('Failed to open folder:', error);
        }
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div className="border-t border-border/50 bg-card/30">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border/50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
                        <HardDrive className="w-4 h-4 text-green-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-foreground">Generated Files</h3>
                        <p className="text-xs text-muted-foreground">{files.length} PDFs in output folder</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button onClick={loadFiles} variant="ghost" size="icon" disabled={isLoadingFiles}>
                        <RefreshCw className={`w-4 h-4 ${isLoadingFiles ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button onClick={handleOpenFolder} variant="outline" size="sm">
                        <FolderOpen className="w-4 h-4 mr-2" />
                        Open Folder
                    </Button>
                </div>
            </div>

            {/* Files Table */}
            {files.length === 0 ? (
                <div className="p-8 text-center">
                    <FileText className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">No files generated yet</p>
                </div>
            ) : (
                <div className="max-h-64 overflow-y-auto">
                    <table className="w-full">
                        <thead className="bg-secondary/30 sticky top-0">
                            <tr>
                                <th className="text-left text-xs font-medium text-muted-foreground px-4 py-2">Filename</th>
                                <th className="text-left text-xs font-medium text-muted-foreground px-4 py-2">Created</th>
                                <th className="text-right text-xs font-medium text-muted-foreground px-4 py-2">Size</th>
                                <th className="text-right text-xs font-medium text-muted-foreground px-4 py-2">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map((file) => (
                                <tr
                                    key={file.filename}
                                    className="border-b border-border/30 hover:bg-secondary/20 transition-colors"
                                >
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-red-400" />
                                            <span className="text-sm font-medium text-foreground truncate max-w-[200px]">
                                                {file.filename}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-xs text-muted-foreground">{formatDate(file.created_at)}</span>
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <span className="text-xs text-muted-foreground">{file.size_kb} KB</span>
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <div className="flex items-center justify-end gap-1">
                                            <Button
                                                onClick={() => handleOpenFile(file.filename)}
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                onClick={() => handleDeleteFile(file.filename)}
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
