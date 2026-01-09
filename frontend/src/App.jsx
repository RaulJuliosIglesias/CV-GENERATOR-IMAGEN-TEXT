import { useState, useRef, useEffect } from 'react';
import ConfigPanel from './components/ConfigPanel';
import ProgressTracker from './components/ProgressTracker';
import FileExplorer from './components/FileExplorer';
import ToolsPanel from './components/ToolsPanel';
import DragDropZone from './components/DragDropZone';
import { useKeyboardShortcuts, COMMON_SHORTCUTS } from './hooks/useKeyboardShortcuts';
import useGenerationStore from './stores/useGenerationStore';
import { Toaster } from 'sonner';

function App() {
    const [fileExplorerHeight, setFileExplorerHeight] = useState(300); // Initial height in pixels
    const [isResizing, setIsResizing] = useState(false);
    const resizeRef = useRef(null);
    const mainRef = useRef(null);
    const startYRef = useRef(0);
    const startHeightRef = useRef(0);
    
    const startGeneration = useGenerationStore(s => s.startGeneration);
    const stopGeneration = useGenerationStore(s => s.stopGeneration);
    const clearQueue = useGenerationStore(s => s.clearQueue);
    const loadFiles = useGenerationStore(s => s.loadFiles);
    const isGenerating = useGenerationStore(s => s.isGenerating);

    // Keyboard shortcuts
    useKeyboardShortcuts([
        {
            key: COMMON_SHORTCUTS.GENERATE.key,
            handler: () => {
                if (!isGenerating) {
                    startGeneration();
                }
            }
        },
        {
            key: COMMON_SHORTCUTS.STOP.key,
            handler: () => {
                if (isGenerating) {
                    stopGeneration();
                }
            }
        },
        {
            key: COMMON_SHORTCUTS.CLEAR.key,
            handler: () => {
                clearQueue();
            }
        },
        {
            key: COMMON_SHORTCUTS.REFRESH.key,
            handler: (e) => {
                e.preventDefault();
                loadFiles();
            }
        }
    ]);

    // Limits
    const MIN_HEIGHT = 150;
    const MAX_HEIGHT = 800;

    const startResizing = (e) => {
        setIsResizing(true);
        e.preventDefault(); // Prevent text selection
        
        // Store initial mouse Y position and current height
        startYRef.current = e.clientY;
        startHeightRef.current = fileExplorerHeight;
    };

    const stopResizing = () => {
        setIsResizing(false);
    };

    const resize = (e) => {
        if (isResizing) {
            e.preventDefault();
            e.stopPropagation();
            
            // Calculate the difference in mouse Y position
            // When dragging down (mouseY increases), we want to decrease height
            // When dragging up (mouseY decreases), we want to increase height
            const deltaY = startYRef.current - e.clientY;
            
            // New height = start height + delta
            // delta is positive when dragging up (mouseY decreases) -> height increases ✓
            // delta is negative when dragging down (mouseY increases) -> height decreases ✓
            const newHeight = startHeightRef.current + deltaY;

            if (newHeight >= MIN_HEIGHT && newHeight <= MAX_HEIGHT) {
                setFileExplorerHeight(newHeight);
                // Save to localStorage
                localStorage.setItem('file-explorer-height', newHeight.toString());
            }
        }
    };
    
    // Load saved height from localStorage
    useEffect(() => {
        const savedHeight = localStorage.getItem('file-explorer-height');
        if (savedHeight) {
            const height = parseInt(savedHeight, 10);
            if (height >= MIN_HEIGHT && height <= MAX_HEIGHT) {
                setFileExplorerHeight(height);
            }
        }
    }, []);

    useEffect(() => {
        if (isResizing) {
            window.addEventListener('mousemove', resize);
            window.addEventListener('mouseup', stopResizing);
        }
        return () => {
            window.removeEventListener('mousemove', resize);
            window.removeEventListener('mouseup', stopResizing);
        };
    }, [isResizing]);

    return (
        <DragDropZone>
            <div className="flex h-screen overflow-hidden bg-background">
                {/* Sidebar - Config Panel */}
                <ConfigPanel />

            {/* Main Content */}
            <main ref={mainRef} className="flex-1 flex flex-col overflow-hidden">
                {/* Progress Tracker */}
                <ProgressTracker />

                {/* Tools Panel - All utilities in one collapsible panel */}
                <div className="border-t border-border/50 bg-card/30 p-4 flex-shrink-0">
                    <ToolsPanel />
                </div>

                {/* Resize Handle - Between Tools Panel and File Explorer */}
                <div
                    ref={resizeRef}
                    className="h-3 bg-border/50 hover:bg-primary/40 cursor-row-resize transition-colors w-full flex items-center justify-center group relative flex-shrink-0"
                    onMouseDown={startResizing}
                    style={{ userSelect: 'none', cursor: 'row-resize' }}
                >
                    <div className="w-32 h-1.5 rounded-full bg-border group-hover:bg-primary transition-colors" />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                            ═ Drag to resize ═
                        </span>
                    </div>
                </div>

                {/* File Explorer - Fixed height container */}
                <div 
                    className="overflow-hidden flex-shrink-0" 
                    style={{ 
                        height: `${fileExplorerHeight}px`,
                        minHeight: `${fileExplorerHeight}px`,
                        maxHeight: `${fileExplorerHeight}px`
                    }}
                >
                    <FileExplorer height={fileExplorerHeight} />
                </div>
            </main>
            <Toaster position="bottom-right" theme="dark" richColors />
            </div>
        </DragDropZone>
    );
}

export default App;
