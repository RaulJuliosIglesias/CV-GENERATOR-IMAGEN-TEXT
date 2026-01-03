import { useState, useMemo, useEffect } from 'react';
import { FileText, Trash2, FolderOpen, ExternalLink, RefreshCw, HardDrive, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { deleteFile, openFolder, getPdfUrl, getHtmlUrl } from '../lib/api';

export default function FileExplorer({ height }) {
    const { files, loadFiles, isLoadingFiles } = useGenerationStore();
    const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });

    useEffect(() => {
        loadFiles();
    }, []);

    const handleOpenPdf = (filename) => {
        window.open(getPdfUrl(filename), '_blank');
    };

    const handleOpenHtml = (filename) => {
        window.open(getHtmlUrl(filename), '_blank');
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
        try {
            const date = new Date(isoString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        } catch (e) { return isoString; }
    };

    // Parse filename to extract metadata (ID, Name, Role)
    const parseFilename = (filename) => {
        try {
            const cleanName = filename.replace(/\.(html|pdf)$/, '');

            // Try new format first (Double Underscore separator)
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

            // Fallback for legacy files (Simple underscore split)
            const parts = cleanName.split('_');
            if (parts.length >= 2) {
                const id = parts[0];
                const rest = cleanName.substring(id.length + 1).replace(/_/g, ' ');
                return { id, name: rest, role: '-' };
            }
        } catch (e) { console.error(e); }

        return { id: '', name: filename, role: '' };
    };

    const sortedFiles = useMemo(() => {
        let sortableFiles = [...files];
        sortableFiles.sort((a, b) => {
            const metaA = parseFilename(a.filename);
            const metaB = parseFilename(b.filename);

            let aValue, bValue;

            switch (sortConfig.key) {
                case 'id':
                    aValue = metaA.id;
                    bValue = metaB.id;
                    break;
                case 'name':
                    aValue = metaA.name; // Use parsed name
                    bValue = metaB.name;
                    break;
                case 'role':
                    aValue = metaA.role; // Use parsed role
                    bValue = metaB.role;
                    break;
                case 'size_kb':
                    aValue = a.size_kb;
                    bValue = b.size_kb;
                    break;
                default:
                    aValue = a[sortConfig.key];
                    bValue = b[sortConfig.key];
            }

            if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
        return sortableFiles;
    }, [files, sortConfig]);

    const requestSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const SortIcon = ({ columnKey }) => {
        if (sortConfig.key !== columnKey) return <ArrowUpDown className="w-3 h-3 ml-1 text-muted-foreground/30" />;
        return sortConfig.direction === 'asc'
            ? <ArrowUp className="w-3 h-3 ml-1 text-primary" />
            : <ArrowDown className="w-3 h-3 ml-1 text-primary" />;
    };

    return (
        <div className="border-t border-border/50 bg-card/30 flex flex-col" style={{ height: height ? `${height}px` : 'auto' }}>
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

            {/* Files Table - Sticky Header */}
            {files.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-card/10">
                    <FileText className="w-12 h-12 text-muted-foreground/30 mb-3" />
                    <p className="text-sm text-muted-foreground">No files generated yet</p>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-secondary/50 backdrop-blur-md sticky top-0 z-10 shadow-sm">
                            <tr>
                                <th
                                    className="text-xs font-semibold text-muted-foreground px-4 py-3 cursor-pointer hover:bg-secondary/80 hover:text-foreground transition-colors select-none"
                                    onClick={() => requestSort('id')}
                                >
                                    <div className="flex items-center">ID <SortIcon columnKey="id" /></div>
                                </th>
                                <th
                                    className="text-xs font-semibold text-muted-foreground px-4 py-3 cursor-pointer hover:bg-secondary/80 hover:text-foreground transition-colors select-none"
                                    onClick={() => requestSort('name')}
                                >
                                    <div className="flex items-center">Candidate Name <SortIcon columnKey="name" /></div>
                                </th>
                                <th
                                    className="text-xs font-semibold text-muted-foreground px-4 py-3 cursor-pointer hover:bg-secondary/80 hover:text-foreground transition-colors select-none"
                                    onClick={() => requestSort('role')}
                                >
                                    <div className="flex items-center">Role <SortIcon columnKey="role" /></div>
                                </th>
                                <th
                                    className="text-xs font-semibold text-muted-foreground px-4 py-3 cursor-pointer hover:bg-secondary/80 hover:text-foreground transition-colors select-none"
                                    onClick={() => requestSort('created_at')}
                                >
                                    <div className="flex items-center">Created <SortIcon columnKey="created_at" /></div>
                                </th>
                                <th
                                    className="text-right text-xs font-semibold text-muted-foreground px-4 py-3 cursor-pointer hover:bg-secondary/80 hover:text-foreground transition-colors select-none"
                                    onClick={() => requestSort('size_kb')}
                                >
                                    <div className="flex items-center justify-end">Size <SortIcon columnKey="size_kb" /></div>
                                </th>
                                <th className="text-right text-xs font-semibold text-muted-foreground px-4 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border/30">
                            {sortedFiles.map((file) => {
                                const meta = parseFilename(file.filename);
                                return (
                                    <tr
                                        key={file.filename}
                                        className="hover:bg-accent/20 transition-colors group"
                                    >
                                        <td className="px-4 py-3">
                                            <span className="font-mono text-xs text-muted-foreground bg-primary/5 px-1.5 py-0.5 rounded border border-primary/10">
                                                {meta.id}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                {file.filename.endsWith('.pdf') ? (
                                                    <FileText className="w-4 h-4 text-red-400 shrink-0" />
                                                ) : (
                                                    <ExternalLink className="w-4 h-4 text-blue-400 shrink-0" />
                                                )}
                                                <a
                                                    href={getPdfUrl(file.filename)}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-sm font-medium text-foreground truncate max-w-[200px] hover:underline"
                                                    title={meta.name}
                                                >
                                                    {meta.name}
                                                </a>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-sm text-foreground/80 truncate max-w-[200px]" title={meta.role}>
                                                {meta.role}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs text-muted-foreground whitespace-nowrap">{formatDate(file.created_at)}</span>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className="text-xs text-muted-foreground font-mono">{file.size_kb} KB</span>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <div className="flex items-center justify-end gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                                                <Button
                                                    onClick={() => handleOpenPdf(file.filename)}
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7 hover:bg-red-500/10 hover:text-red-400"
                                                    title="View PDF"
                                                >
                                                    <FileText className="w-3.5 h-3.5" />
                                                </Button>
                                                <Button
                                                    onClick={() => handleOpenHtml(file.filename)}
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7 hover:bg-blue-500/10 hover:text-blue-400"
                                                    title="View HTML"
                                                >
                                                    <ExternalLink className="w-3.5 h-3.5" />
                                                </Button>
                                                <Button
                                                    onClick={() => handleDeleteFile(file.filename)}
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7 text-muted-foreground hover:text-red-400 hover:bg-red-500/10"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                </Button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
