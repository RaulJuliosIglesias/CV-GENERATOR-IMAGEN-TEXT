import { useState, useMemo, useEffect, useCallback } from 'react';
import { GitCompare, X, FileText, Download, ExternalLink, ChevronDown, ChevronUp, Search, CheckSquare, Square } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { PreviewModal } from './PreviewModal';
import useGenerationStore from '../stores/useGenerationStore';
import { getPdfUrl } from '../lib/api';

/**
 * CVComparison - Componente para comparar múltiples CVs lado a lado
 */
export default function CVComparison() {
    const files = useGenerationStore(s => s.files);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [previewFile, setPreviewFile] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    
    // Load collapsed state from localStorage
    const [isCollapsed, setIsCollapsed] = useState(() => {
        const saved = localStorage.getItem('cv-comparison-collapsed');
        return saved ? JSON.parse(saved) : true; // Collapsed by default
    });
    
    // Save collapsed state to localStorage
    useEffect(() => {
        localStorage.setItem('cv-comparison-collapsed', JSON.stringify(isCollapsed));
    }, [isCollapsed]);

    // Parse filename to extract metadata (same as FileExplorer)
    const parseFilename = useCallback((filename) => {
        try {
            const cleanName = filename.replace(/\.(html|pdf)$/, '');

            if (cleanName.includes('__')) {
                const parts = cleanName.split('__');
                if (parts.length >= 3) {
                    return {
                        id: parts[0],
                        name: parts[1].replace(/_/g, ' '),
                        role: parts[2].replace(/_/g, ' ')
                    };
                }
            }

            const parts = cleanName.split('_');
            if (parts.length >= 2) {
                const potentialId = parts[0];
                const isHashLike = /^[a-z0-9]+$/i.test(potentialId) && /\d/.test(potentialId);

                if (isHashLike || potentialId.length >= 8) {
                    const id = parts[0];
                    const rest = cleanName.substring(id.length + 1).replace(/_/g, ' ');
                    return { id, name: rest, role: '-' };
                }
                return { id: '', name: cleanName.replace(/_/g, ' '), role: '-' };
            }
        } catch (e) { console.error(e); }
        return { id: '', name: filename, role: '' };
    }, []);

    // Pre-calculate metadata for all files
    const filesWithMeta = useMemo(() => {
        return files.map(file => ({
            ...file,
            meta: parseFilename(file.filename)
        }));
    }, [files, parseFilename]);

    // Filter files based on search query
    const filteredFiles = useMemo(() => {
        if (!searchQuery.trim()) {
            return filesWithMeta;
        }
        
        const query = searchQuery.toLowerCase();
        return filesWithMeta.filter(file => {
            const meta = file.meta;
            return (
                meta.name.toLowerCase().includes(query) ||
                meta.role.toLowerCase().includes(query) ||
                meta.id.toLowerCase().includes(query) ||
                file.filename.toLowerCase().includes(query)
            );
        });
    }, [filesWithMeta, searchQuery]);

    const toggleFile = (file) => {
        setSelectedFiles(prev => {
            const index = prev.findIndex(f => f.filename === file.filename);
            if (index >= 0) {
                return prev.filter((_, i) => i !== index);
            } else if (prev.length < 4) { // Max 4 files for comparison
                return [...prev, file];
            }
            return prev;
        });
    };

    const clearSelection = () => {
        setSelectedFiles([]);
    };

    const selectAll = () => {
        const maxFiles = Math.min(4, filteredFiles.length);
        setSelectedFiles(filteredFiles.slice(0, maxFiles));
    };

    const deselectAll = () => {
        setSelectedFiles([]);
    };

    const allSelected = filteredFiles.length > 0 && filteredFiles.every(file => 
        selectedFiles.some(f => f.filename === file.filename)
    );
    const someSelected = filteredFiles.some(file => 
        selectedFiles.some(f => f.filename === file.filename)
    );

    if (files.length < 2) {
        return null;
    }

    return (
        <>
            <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
                {/* Header - Always visible, clickable to collapse */}
                <div
                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-card/70 transition-colors"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                >
                    <div className="flex items-center gap-2">
                        <GitCompare className="w-4 h-4 text-primary" />
                        <span className="text-sm font-semibold">Compare CVs</span>
                        {selectedFiles.length > 0 && (
                            <span className="text-xs text-muted-foreground">
                                ({selectedFiles.length} selected)
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        {!isCollapsed && selectedFiles.length > 0 && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    clearSelection();
                                }}
                                className="h-6 px-2 text-xs"
                            >
                                Clear
                            </Button>
                        )}
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                                e.stopPropagation();
                                setIsCollapsed(!isCollapsed);
                            }}
                            className="h-6 w-6 p-0"
                        >
                            {isCollapsed ? (
                                <ChevronDown className="w-4 h-4 text-muted-foreground" />
                            ) : (
                                <ChevronUp className="w-4 h-4 text-muted-foreground" />
                            )}
                        </Button>
                    </div>
                </div>

                {/* Collapsible Content */}
                {!isCollapsed && (
                    <div className="px-3 pb-3 space-y-3 border-t border-border/50 pt-3">
                        {/* Search Bar */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <Input
                                type="text"
                                placeholder="Search CVs by name, role, or ID..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9 pr-9 h-8 text-xs"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setSearchQuery('')}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>

                        {/* Selection Actions */}
                        {filteredFiles.length > 0 && (
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={allSelected ? deselectAll : selectAll}
                                        className="h-7 px-2 text-xs"
                                    >
                                        {allSelected ? (
                                            <>
                                                <CheckSquare className="w-3 h-3 mr-1" />
                                                Deselect All
                                            </>
                                        ) : (
                                            <>
                                                <Square className="w-3 h-3 mr-1" />
                                                Select All ({Math.min(4, filteredFiles.length)} max)
                                            </>
                                        )}
                                    </Button>
                                    {selectedFiles.length > 0 && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={clearSelection}
                                            className="h-7 px-2 text-xs"
                                        >
                                            Clear ({selectedFiles.length})
                                        </Button>
                                    )}
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    {filteredFiles.length} {filteredFiles.length === 1 ? 'CV' : 'CVs'}
                                    {searchQuery && ` found`}
                                </span>
                            </div>
                        )}

                        {/* Selected Files Display */}
                        {selectedFiles.length > 0 && (
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 flex-wrap">
                                    {selectedFiles.map((file) => {
                                        const meta = parseFilename(file.filename);
                                        return (
                                            <div
                                                key={file.filename}
                                                className="flex items-center gap-2 px-2 py-1 bg-primary/20 rounded border border-primary/50 text-xs"
                                            >
                                                <FileText className="w-3 h-3 text-primary" />
                                                <span className="truncate max-w-[150px] font-medium">
                                                    {meta.name || file.filename}
                                                </span>
                                                {meta.role && meta.role !== '-' && (
                                                    <span className="text-[10px] px-1.5 py-0.5 bg-primary/30 rounded">
                                                        {meta.role}
                                                    </span>
                                                )}
                                                <button
                                                    onClick={() => toggleFile(file)}
                                                    className="text-primary hover:text-destructive transition-colors"
                                                >
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                                {selectedFiles.length >= 2 && (
                                    <Button
                                        variant="default"
                                        size="sm"
                                        onClick={() => setIsOpen(true)}
                                        className="w-full h-7 text-xs"
                                    >
                                        <GitCompare className="w-3 h-3 mr-1" />
                                        Open Comparison View ({selectedFiles.length} CVs)
                                    </Button>
                                )}
                            </div>
                        )}

                        {/* File List - All files with search */}
                        <div className="border-t border-border/30 pt-3">
                            <p className="text-xs text-muted-foreground mb-2">
                                {searchQuery ? 'Search Results' : 'All CVs'} ({filteredFiles.length}):
                            </p>
                            <div className="max-h-64 overflow-y-auto space-y-1 custom-scrollbar">
                                {filteredFiles.length === 0 ? (
                                    <p className="text-xs text-muted-foreground text-center py-4">
                                        No CVs found matching "{searchQuery}"
                                    </p>
                                ) : (
                                    filteredFiles.map((file) => {
                                        const isSelected = selectedFiles.some(f => f.filename === file.filename);
                                        const meta = file.meta;
                                        const isDisabled = !isSelected && selectedFiles.length >= 4;
                                        
                                        return (
                                            <button
                                                key={file.filename}
                                                onClick={() => !isDisabled && toggleFile(file)}
                                                disabled={isDisabled}
                                                className={`w-full flex items-center gap-2 px-2 py-2 rounded border transition-colors text-left ${
                                                    isSelected
                                                        ? 'bg-primary text-primary-foreground border-primary'
                                                        : isDisabled
                                                        ? 'bg-background/50 border-border/30 opacity-50 cursor-not-allowed'
                                                        : 'bg-background border-border/50 hover:bg-accent/50 hover:border-accent'
                                                }`}
                                            >
                                                {isSelected ? (
                                                    <CheckSquare className="w-4 h-4 shrink-0" />
                                                ) : (
                                                    <Square className="w-4 h-4 shrink-0 text-muted-foreground" />
                                                )}
                                                <FileText className="w-4 h-4 shrink-0" />
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-xs font-medium truncate">
                                                        {meta.name || file.filename}
                                                    </p>
                                                    <div className="flex items-center gap-2 mt-0.5">
                                                        {meta.role && meta.role !== '-' && (
                                                            <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                                                                {meta.role}
                                                            </span>
                                                        )}
                                                        <span className="text-[10px] text-muted-foreground truncate">
                                                            {meta.id || 'No ID'}
                                                        </span>
                                                    </div>
                                                </div>
                                                {isDisabled && (
                                                    <span className="text-[10px] text-muted-foreground shrink-0">
                                                        (Max 4)
                                                    </span>
                                                )}
                                            </button>
                                        );
                                    })
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Comparison Modal */}
            {isOpen && selectedFiles.length >= 2 && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md p-4">
                    <div className="h-full flex flex-col bg-background border border-border rounded-xl overflow-hidden">
                        {/* Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
                            <div className="flex items-center gap-3">
                                <GitCompare className="w-5 h-5 text-primary" />
                                <h2 className="text-lg font-bold">CV Comparison</h2>
                                <span className="text-sm text-muted-foreground">
                                    {selectedFiles.length} files
                                </span>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setIsOpen(false)}
                            >
                                <X className="w-5 h-5" />
                            </Button>
                        </div>

                        {/* Comparison Grid */}
                        <div className="flex-1 overflow-auto p-4">
                            <div
                                className={`grid gap-4 h-full ${
                                    selectedFiles.length === 2
                                        ? 'grid-cols-2'
                                        : selectedFiles.length === 3
                                        ? 'grid-cols-3'
                                        : 'grid-cols-2'
                                }`}
                            >
                                {selectedFiles.map((file) => (
                                    <div
                                        key={file.filename}
                                        className="border border-border rounded-lg overflow-hidden bg-card flex flex-col"
                                    >
                                        <div className="p-2 border-b border-border bg-card/50 flex items-center justify-between">
                                            <span className="text-xs font-medium truncate flex-1">
                                                {file.filename}
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    onClick={() => setPreviewFile(file)}
                                                    className="h-6 w-6"
                                                    title="Preview"
                                                >
                                                    <ExternalLink className="w-3 h-3" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    onClick={() => window.open(getPdfUrl(file.filename), '_blank')}
                                                    className="h-6 w-6"
                                                    title="Download"
                                                >
                                                    <Download className="w-3 h-3" />
                                                </Button>
                                            </div>
                                        </div>
                                        <div className="flex-1 overflow-auto">
                                            <iframe
                                                src={`/api/files/html/${file.filename.replace('.pdf', '.html')}`}
                                                className="w-full h-full border-0"
                                                title={file.filename}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Preview Modal */}
            {previewFile && (
                <PreviewModal
                    file={previewFile}
                    onClose={() => setPreviewFile(null)}
                />
            )}
        </>
    );
}
