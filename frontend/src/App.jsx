import { useState, useRef, useEffect } from 'react';
import ConfigPanel from './components/ConfigPanel';
import ProgressTracker from './components/ProgressTracker';
import FileExplorer from './components/FileExplorer';
import DownloadZipPanel from './components/DownloadZipPanel';
import { Toaster } from 'sonner';

function App() {
    const [fileExplorerHeight, setFileExplorerHeight] = useState(300); // Initial height in pixels
    const [isResizing, setIsResizing] = useState(false);

    // Limits
    const MIN_HEIGHT = 150;
    const MAX_HEIGHT = 800;

    const startResizing = (e) => {
        setIsResizing(true);
        e.preventDefault(); // Prevent text selection
    };

    const stopResizing = () => {
        setIsResizing(false);
    };

    const resize = (e) => {
        if (isResizing) {
            const containerHeight = window.innerHeight;
            // The mouse Y position relative to bottom determines height
            // But since we are dragging a "top" border of a bottom component:
            // newHeight = totalHeight - mouseY
            const newHeight = containerHeight - e.clientY;

            if (newHeight >= MIN_HEIGHT && newHeight <= MAX_HEIGHT) {
                setFileExplorerHeight(newHeight);
            }
        }
    };

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
        <div className="flex h-screen overflow-hidden bg-background">
            {/* Sidebar - Config Panel */}
            <ConfigPanel />

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Progress Tracker */}
                <ProgressTracker />

                {/* Download ZIP Panel - Separate dedicated component */}
                <div className="border-t border-border/50 bg-card/30 p-4">
                    <DownloadZipPanel />
                </div>

                {/* File Explorer */}
                {/* File Explorer with Resize Handle */}

                {/* Drag Handle */}
                <div
                    className="h-1 bg-border hover:bg-primary/50 cursor-row-resize transition-colors w-full flex items-center justify-center group"
                    onMouseDown={startResizing}
                >
                    <div className="w-16 h-1 rounded-full bg-border group-hover:bg-primary transition-colors" />
                </div>

                <FileExplorer height={fileExplorerHeight} />
            </main>
            <Toaster position="bottom-right" theme="dark" richColors />
        </div>
    );
}

export default App;
