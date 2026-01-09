import { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { FileText, Trash2, FolderOpen, ExternalLink, RefreshCw, HardDrive, ArrowUpDown, ArrowUp, ArrowDown, Download, ChevronLeft, ChevronRight, Search, Filter, X } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import useGenerationStore from '../stores/useGenerationStore';
import { deleteFile, openFolder, getPdfUrl, getHtmlUrl } from '../lib/api';
import { AnimatePresence } from 'framer-motion';
import { PreviewModal } from './PreviewModal';

// Items per page for pagination
const PAGE_SIZE = 50;

export default function FileExplorer({ height }) {
    // Atomic Selectors - CRITICAL for performance
    const files = useGenerationStore(s => s.files);
    const loadFiles = useGenerationStore(s => s.loadFiles);
    const isLoadingFiles = useGenerationStore(s => s.isLoadingFiles);

    // Selecting ONLY the count of completed tasks prevents re-renders on every poll update
    const completedCount = useGenerationStore(s =>
        s.allTasks.filter(t => t.status === 'complete').length
    );

    const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
    const [previewFile, setPreviewFile] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    
    // Search and filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [filterRole, setFilterRole] = useState('');
    const [showFilters, setShowFilters] = useState(false);

    // Track previous count to trigger reload only on INCREASE
    const prevCompletedCountRef = useRef(0);

    // Initial load - always try to load files on mount
    useEffect(() => {
        loadFiles();
    }, [loadFiles]);

    // Optimize Auto-refresh: Only runs when COUNT changes (not every poll tick)
    useEffect(() => {
        if (completedCount > prevCompletedCountRef.current && prevCompletedCountRef.current > 0) {
            console.log(`📁 Task completed! Refreshing files... (${prevCompletedCountRef.current} → ${completedCount})`);
            loadFiles();
        }
        prevCompletedCountRef.current = completedCount;
    }, [completedCount, loadFiles]);

    // Parse filename to extract metadata (ID, Name, Role)
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

    // Pre-calculate metadata once when files change
    const filesWithMeta = useMemo(() => {
        return files.map(file => ({
            ...file,
            meta: parseFilename(file.filename)
        }));
    }, [files, parseFilename]);

    // Extract unique roles for filter dropdown
    const uniqueRoles = useMemo(() => {
        const roles = new Set();
        filesWithMeta.forEach(file => {
            if (file.meta.role && file.meta.role !== '-') {
                roles.add(file.meta.role);
            }
        });
        return Array.from(roles).sort();
    }, [filesWithMeta]);

    // Filter and search files
    const filteredFiles = useMemo(() => {
        let filtered = [...filesWithMeta];

        // Apply search query
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(file => {
                const meta = file.meta;
                return (
                    meta.name.toLowerCase().includes(query) ||
                    meta.role.toLowerCase().includes(query) ||
                    meta.id.toLowerCase().includes(query) ||
                    file.filename.toLowerCase().includes(query)
                );
            });
        }

        // Apply role filter
        if (filterRole) {
            filtered = filtered.filter(file => file.meta.role === filterRole);
        }

        return filtered;
    }, [filesWithMeta, searchQuery, filterRole]);

    const sortedFiles = useMemo(() => {
        let sortableFiles = [...filteredFiles];
        sortableFiles.sort((a, b) => {
            const metaA = a.meta;
            const metaB = b.meta;

            let aValue, bValue;

            switch (sortConfig.key) {
                case 'id':
                    aValue = metaA.id;
                    bValue = metaB.id;
                    break;
                case 'name':
                    aValue = metaA.name;
                    bValue = metaB.name;
                    break;
                case 'role':
                    aValue = metaA.role;
                    bValue = metaB.role;
                    break;
                case 'created_at':
                default:
                    aValue = new Date(a.created_at || 0).getTime();
                    bValue = new Date(b.created_at || 0).getTime();
                    break;
            }

            if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
        return sortableFiles;
    }, [filteredFiles, sortConfig]);

    // Pagination
    const totalPages = Math.ceil(sortedFiles.length / PAGE_SIZE);
    const paginatedFiles = useMemo(() => {
        const start = (currentPage - 1) * PAGE_SIZE;
        return sortedFiles.slice(start, start + PAGE_SIZE);
    }, [sortedFiles, currentPage]);

    // Reset to page 1 when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery, filterRole, sortConfig]);

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    const handleDelete = async (filename) => {
        if (!confirm(`Delete ${filename}?`)) return;
        try {
            await deleteFile(filename);
            loadFiles();
        } catch (error) {
            console.error('Delete failed:', error);
        }
    };

    const SortButton = ({ sortKey, label }) => (
        <Button
            variant="ghost"
            size="sm"
            onClick={() => handleSort(sortKey)}
            className="h-7 px-2 text-xs flex items-center gap-1"
        >
            {label}
            {sortConfig.key === sortKey && (
                sortConfig.direction === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
            )}
        </Button>
    );

    return (
        <div className="flex flex-col h-full bg-background border-t border-border/50 overflow-hidden">
            {/* Header with Search and Filters */}
            <div className="p-4 border-b border-border/50 space-y-3 flex-shrink-0">
                {/* Search Bar */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        type="text"
                        placeholder="Search by name, role, or ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 pr-9 h-9"
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

                {/* Filter Toggle and Active Filters */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowFilters(!showFilters)}
                            className="h-7 px-2 text-xs"
                        >
                            <Filter className="w-3 h-3 mr-1" />
                            Filters
                            {(filterRole) && (
                                <span className="ml-1 px-1.5 py-0.5 bg-primary/20 text-primary rounded text-[10px]">
                                    {filterRole ? 1 : 0}
                                </span>
                            )}
                        </Button>
                        {(filterRole) && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                    setFilterRole('');
                                }}
                                className="h-7 px-2 text-xs"
                            >
                                Clear
                            </Button>
                        )}
                    </div>
                    <div className="text-xs text-muted-foreground">
                        {filteredFiles.length} of {files.length} files
                    </div>
                </div>

                {/* Filter Panel */}
                {showFilters && (
                    <div className="p-3 bg-card/50 rounded-lg border border-border/50 space-y-2">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-muted-foreground">Role</label>
                            <select
                                value={filterRole}
                                onChange={(e) => setFilterRole(e.target.value)}
                                className="w-full h-8 px-2 text-xs bg-background border border-border rounded"
                            >
                                <option value="">All Roles</option>
                                {uniqueRoles.map(role => (
                                    <option key={role} value={role}>{role}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                )}

                {/* Sort Controls */}
                <div className="flex items-center gap-1 flex-wrap">
                    <span className="text-xs text-muted-foreground mr-1">Sort:</span>
                    <SortButton sortKey="created_at" label="Date" />
                    <SortButton sortKey="name" label="Name" />
                    <SortButton sortKey="role" label="Role" />
                    <SortButton sortKey="id" label="ID" />
                </div>
            </div>

            {/* File List */}
            <div className="flex-1 overflow-y-auto p-4">
                {isLoadingFiles ? (
                    <div className="flex items-center justify-center h-full">
                        <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
                    </div>
                ) : paginatedFiles.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <FileText className="w-12 h-12 text-muted-foreground/50 mb-4" />
                        <p className="text-sm text-muted-foreground">
                            {searchQuery || filterRole ? 'No files match your filters' : 'No files generated yet'}
                        </p>
                        {(searchQuery || filterRole) && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                    setSearchQuery('');
                                    setFilterRole('');
                                }}
                                className="mt-2"
                            >
                                Clear filters
                            </Button>
                        )}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-2">
                        <AnimatePresence mode="popLayout">
                            {paginatedFiles.map((file) => {
                                const meta = file.meta;
                                return (
                                    <div
                                        key={file.filename}
                                        className="group flex items-center justify-between p-3 rounded-lg border border-border/50 hover:bg-accent/20 transition-all cursor-pointer"
                                        onClick={() => setPreviewFile(file)}
                                    >
                                        <div className="flex items-center gap-3 flex-1 min-w-0">
                                            <FileText 
                                                className="w-5 h-5 text-blue-400 shrink-0 cursor-pointer" 
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setPreviewFile(file);
                                                }}
                                            />
                                            <div className="flex-1 min-w-0">
                                                <p 
                                                    className="text-sm font-medium truncate cursor-pointer"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setPreviewFile(file);
                                                    }}
                                                >
                                                    {meta.name || file.filename}
                                                </p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    {meta.role && meta.role !== '-' && (
                                                        <span className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                                                            {meta.role}
                                                        </span>
                                                    )}
                                                    <span className="text-xs text-muted-foreground truncate">
                                                        {meta.id || 'No ID'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => setPreviewFile(file)}
                                                className="h-8 w-8"
                                                title="Preview"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => window.open(getPdfUrl(file.filename), '_blank')}
                                                className="h-8 w-8"
                                                title="Download PDF"
                                            >
                                                <Download className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => handleDelete(file.filename)}
                                                className="h-8 w-8 text-red-400 hover:text-red-500"
                                                title="Delete"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                );
                            })}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="p-4 border-t border-border/50 flex items-center justify-between flex-shrink-0">
                    <div className="text-xs text-muted-foreground">
                        Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                            disabled={currentPage === 1}
                            className="h-7 px-2"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                            disabled={currentPage === totalPages}
                            className="h-7 px-2"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </Button>
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
        </div>
    );
}
