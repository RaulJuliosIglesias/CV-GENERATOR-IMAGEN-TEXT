import { useState, useEffect, useCallback } from 'react';
import { Archive, Download, FileText, Image, Loader2, ChevronDown, ChevronUp, CheckSquare, Square } from 'lucide-react';
import { Button } from './ui/Button';
import { useDownloadZip } from '../hooks/useDownloadZip';
import useGenerationStore from '../stores/useGenerationStore';

/**
 * DownloadZipPanel - Dedicated component for ZIP download functionality
 * Provides options to download CVs with customizable file types and file selection
 */
export default function DownloadZipPanel() {
    const { downloadSelected, isDownloading } = useDownloadZip();
    const files = useGenerationStore(s => s.files);
    const completedTasks = useGenerationStore(s => 
        s.allTasks.filter(t => t.status === 'complete')
    );

    const [isCollapsed, setIsCollapsed] = useState(true);
    const [options, setOptions] = useState({
        includeHtml: false,
        includeAvatars: false
    });
    const [selectedFiles, setSelectedFiles] = useState(new Set());

    const hasFiles = files.length > 0 || completedTasks.length > 0;

    // Initialize selection: all files selected by default when files change
    useEffect(() => {
        if (files.length > 0) {
            const fileFilenames = files.map(f => f.filename);
            setSelectedFiles(prev => {
                // Only update if the files list has changed
                const currentFilenames = Array.from(prev);
                const filesChanged = 
                    fileFilenames.length !== currentFilenames.length ||
                    !fileFilenames.every(f => currentFilenames.includes(f));
                
                if (filesChanged || prev.size === 0) {
                    return new Set(fileFilenames);
                }
                return prev;
            });
        }
    }, [files]);

    const toggleFileSelection = useCallback((filename) => {
        setSelectedFiles(prev => {
            const newSet = new Set(prev);
            if (newSet.has(filename)) {
                newSet.delete(filename);
            } else {
                newSet.add(filename);
            }
            return newSet;
        });
    }, []);

    const selectAll = useCallback(() => {
        if (files.length > 0) {
            setSelectedFiles(new Set(files.map(f => f.filename)));
        }
    }, [files]);

    const deselectAll = useCallback(() => {
        setSelectedFiles(new Set());
    }, []);

    const handleDownload = () => {
        if (selectedFiles.size === 0) {
            return;
        }

        downloadSelected({
            filenames: Array.from(selectedFiles),
            includeHtml: options.includeHtml,
            includeAvatars: options.includeAvatars
        });
    };

    if (!hasFiles) {
        return null; // Don't show panel if no files
    }

    const selectedCount = selectedFiles.size;
    const totalCount = files.length;
    const allSelected = selectedCount === totalCount && totalCount > 0;

    return (
        <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
            {/* Header - Always visible, clickable to collapse */}
            <div 
                className="flex items-center gap-3 p-4 cursor-pointer hover:bg-card/70 transition-colors"
                onClick={() => setIsCollapsed(!isCollapsed)}
            >
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center shrink-0">
                    <Archive className="w-5 h-5 text-purple-400" />
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-foreground">Download CVs as ZIP</h3>
                    <p className="text-xs text-muted-foreground truncate">
                        {selectedCount > 0 
                            ? `${selectedCount} of ${totalCount} PDF${totalCount !== 1 ? 's' : ''} selected`
                            : `${totalCount} PDF${totalCount !== 1 ? 's' : ''} ready to download`
                        }
                    </p>
                </div>
                <button
                    type="button"
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsCollapsed(!isCollapsed);
                    }}
                    className="p-2 hover:bg-accent/20 rounded transition-colors shrink-0"
                    aria-label={isCollapsed ? 'Expand' : 'Collapse'}
                >
                    {isCollapsed ? (
                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                    ) : (
                        <ChevronUp className="w-5 h-5 text-muted-foreground" />
                    )}
                </button>
            </div>

            {/* Collapsible Content */}
            {!isCollapsed && (
                <div className="px-4 pb-4 space-y-4 border-t border-border/50 pt-4">
                    {/* Selection Controls - Top of content */}
                    <div className="flex items-center justify-between pb-2 border-b border-border/30">
                        <span className="text-xs font-medium text-foreground">
                            Select files to download
                        </span>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                                e.stopPropagation();
                                if (allSelected) {
                                    deselectAll();
                                } else {
                                    selectAll();
                                }
                            }}
                            className="h-7 px-3 text-xs"
                            type="button"
                        >
                            {allSelected ? 'Deselect All' : 'Select All'}
                        </Button>
                    </div>

                    {/* File Selection List */}
                    <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                        {files.length === 0 ? (
                            <p className="text-xs text-muted-foreground text-center py-4">
                                No files available
                            </p>
                        ) : (
                            files.map((file) => {
                                const isSelected = selectedFiles.has(file.filename);
                                const meta = file.filename.replace(/\.(html|pdf)$/, '').split('__');
                                const displayName = meta.length >= 2 ? meta[1].replace(/_/g, ' ') : file.filename;

                                return (
                                    <label
                                        key={file.filename}
                                        className="flex items-center gap-2 p-2 rounded hover:bg-accent/20 cursor-pointer group"
                                    >
                                        <div className="shrink-0">
                                            {isSelected ? (
                                                <CheckSquare className="w-4 h-4 text-primary" />
                                            ) : (
                                                <Square className="w-4 h-4 text-muted-foreground group-hover:text-foreground" />
                                            )}
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={isSelected}
                                            onChange={() => toggleFileSelection(file.filename)}
                                            className="sr-only"
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                        <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                                        <span className="text-sm text-foreground truncate flex-1" title={displayName}>
                                            {displayName}
                                        </span>
                                        <span className="text-xs text-muted-foreground shrink-0">
                                            {file.size_kb} KB
                                        </span>
                                    </label>
                                );
                            })
                        )}
                    </div>

                    {/* Options */}
                    <div className="space-y-2 pt-2 border-t border-border/30">
                        <label className="flex items-center gap-2 cursor-pointer group">
                            <input
                                type="checkbox"
                                checked={options.includeHtml}
                                onChange={(e) => setOptions(prev => ({ ...prev, includeHtml: e.target.checked }))}
                                className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                                disabled={isDownloading}
                            />
                            <FileText className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                                Include HTML files
                            </span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer group">
                            <input
                                type="checkbox"
                                checked={options.includeAvatars}
                                onChange={(e) => setOptions(prev => ({ ...prev, includeAvatars: e.target.checked }))}
                                className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                                disabled={isDownloading}
                            />
                            <Image className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                                Include avatar images
                            </span>
                        </label>
                    </div>

                    {/* Download Button */}
                    <Button
                        onClick={handleDownload}
                        disabled={isDownloading || selectedCount === 0}
                        className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        size="sm"
                    >
                        {isDownloading ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Compressing...
                            </>
                        ) : (
                            <>
                                <Download className="w-4 h-4 mr-2" />
                                Download {selectedCount > 0 ? `${selectedCount} ` : ''}as ZIP
                            </>
                        )}
                    </Button>
                </div>
            )}
        </div>
    );
}
