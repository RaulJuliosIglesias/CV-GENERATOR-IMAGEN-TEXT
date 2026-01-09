import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, BarChart3, GitCompare, Download, FolderOpen } from 'lucide-react';
import { Button } from './ui/Button';
import StatsPanel from './StatsPanel';
import CVComparison from './CVComparison';
import BatchOperations from './BatchOperations';
import DownloadZipPanel from './DownloadZipPanel';

/**
 * ToolsPanel - Panel único colapsable que contiene todas las herramientas
 * (Estadísticas, Comparar CVs, Operaciones en lote, Descargar ZIP)
 */
export default function ToolsPanel() {
    // Load collapsed state from localStorage
    const [isCollapsed, setIsCollapsed] = useState(() => {
        const saved = localStorage.getItem('tools-panel-collapsed');
        return saved ? JSON.parse(saved) : true; // Collapsed by default
    });
    
    // Save collapsed state to localStorage
    useEffect(() => {
        localStorage.setItem('tools-panel-collapsed', JSON.stringify(isCollapsed));
    }, [isCollapsed]);

    return (
        <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
            {/* Header - Always visible, clickable to collapse */}
            <div
                className="flex items-center justify-between p-3 cursor-pointer hover:bg-card/70 transition-colors"
                onClick={() => setIsCollapsed(!isCollapsed)}
            >
                <div className="flex items-center gap-2">
                    <FolderOpen className="w-4 h-4 text-primary" />
                    <span className="text-sm font-semibold">Tools & Utilities</span>
                </div>
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

            {/* Collapsible Content */}
            {!isCollapsed && (
                <div className="px-3 pb-3 space-y-2 border-t border-border/50 pt-3">
                    {/* Statistics */}
                    <div className="border-b border-border/30 pb-2 last:border-b-0">
                        <StatsPanel />
                    </div>

                    {/* CV Comparison */}
                    <div className="border-b border-border/30 pb-2 last:border-b-0">
                        <CVComparison />
                    </div>

                    {/* Batch Operations */}
                    <div className="border-b border-border/30 pb-2 last:border-b-0">
                        <BatchOperations />
                    </div>

                    {/* Download ZIP */}
                    <div>
                        <DownloadZipPanel />
                    </div>
                </div>
            )}
        </div>
    );
}
