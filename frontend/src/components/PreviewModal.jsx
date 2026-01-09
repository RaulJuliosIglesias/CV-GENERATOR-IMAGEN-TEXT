import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Download, FileText, ZoomIn, ZoomOut, RotateCw, ChevronLeft, ChevronRight, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from './ui/Button';
import { getHtmlUrl, getPdfUrl } from '../lib/api';
import { motion } from 'framer-motion';
import useGenerationStore from '../stores/useGenerationStore';

export function PreviewModal({ file, onClose }) {
    const files = useGenerationStore(s => s.files);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [zoom, setZoom] = useState(100);
    const [viewMode, setViewMode] = useState('html'); // 'html' or 'pdf'
    const [isFullscreen, setIsFullscreen] = useState(false);

    // Find current file index
    useEffect(() => {
        if (file && files.length > 0) {
            const index = files.findIndex(f => f.filename === file.filename || f.filename === file);
            if (index !== -1) {
                setCurrentIndex(index);
            }
        }
    }, [file, files]);

    const currentFile = files[currentIndex];
    if (!currentFile) return null;

    const filename = typeof currentFile === 'string' ? currentFile : currentFile.filename;
    const htmlUrl = getHtmlUrl(filename);
    const pdfUrl = getPdfUrl(filename);

    const handleDownloadPdf = () => {
        window.open(pdfUrl, '_blank');
    };

    const handlePrevious = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
        }
    };

    const handleNext = () => {
        if (currentIndex < files.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    const handleZoomIn = () => {
        setZoom(prev => Math.min(prev + 25, 200));
    };

    const handleZoomOut = () => {
        setZoom(prev => Math.max(prev - 25, 50));
    };

    const handleResetZoom = () => {
        setZoom(100);
    };

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                onClose();
            } else if (e.key === 'ArrowLeft' && !e.target.tagName.match(/INPUT|TEXTAREA/)) {
                handlePrevious();
            } else if (e.key === 'ArrowRight' && !e.target.tagName.match(/INPUT|TEXTAREA/)) {
                handleNext();
            } else if (e.key === '+' || e.key === '=') {
                handleZoomIn();
            } else if (e.key === '-') {
                handleZoomOut();
            } else if (e.key === '0') {
                handleResetZoom();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentIndex, files.length]);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 md:p-8">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-background border border-border rounded-xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col overflow-hidden relative"
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/50 backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <FileText className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-foreground truncate max-w-sm" title={filename}>
                                {filename.replace(/_/g, ' ').replace('.html', '')}
                            </h2>
                            <p className="text-xs text-muted-foreground">Preview Mode</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => window.open(htmlUrl, '_blank')}
                            className="hidden sm:flex"
                        >
                            <ExternalLink className="w-4 h-4 mr-2" />
                            Open New Tab
                        </Button>
                        <Button
                            variant="default"
                            size="sm"
                            onClick={handleDownloadPdf}
                            className="bg-green-600 hover:bg-green-700 text-white"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Download PDF
                        </Button>
                        <div className="w-px h-6 bg-border mx-2"></div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onClose}
                            className="hover:bg-destructive/10 hover:text-destructive scroll-m-2"
                        >
                            <X className="w-5 h-5" />
                        </Button>
                    </div>
                </div>

                {/* Controls Bar */}
                <div className="px-4 py-2 border-b border-border bg-card/30 flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handlePrevious}
                            disabled={currentIndex === 0}
                            className="h-7 px-2 text-xs"
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </Button>
                        <span className="text-xs text-muted-foreground">
                            {currentIndex + 1} / {files.length}
                        </span>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleNext}
                            disabled={currentIndex === files.length - 1}
                            className="h-7 px-2 text-xs"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </Button>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button
                            variant={viewMode === 'html' ? 'default' : 'ghost'}
                            size="sm"
                            onClick={() => setViewMode('html')}
                            className="h-7 px-2 text-xs"
                        >
                            HTML
                        </Button>
                        <Button
                            variant={viewMode === 'pdf' ? 'default' : 'ghost'}
                            size="sm"
                            onClick={() => setViewMode('pdf')}
                            className="h-7 px-2 text-xs"
                        >
                            PDF
                        </Button>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleZoomOut}
                            className="h-7 px-2 text-xs"
                        >
                            <ZoomOut className="w-4 h-4" />
                        </Button>
                        <span className="text-xs text-muted-foreground min-w-[3rem] text-center">
                            {zoom}%
                        </span>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleZoomIn}
                            className="h-7 px-2 text-xs"
                        >
                            <ZoomIn className="w-4 h-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleResetZoom}
                            className="h-7 px-2 text-xs"
                        >
                            <RotateCw className="w-4 h-4" />
                        </Button>
                    </div>
                </div>

                {/* Content - Iframe or PDF */}
                <div className="flex-1 bg-white/5 relative overflow-auto">
                    {viewMode === 'html' ? (
                        <div
                            style={{
                                transform: `scale(${zoom / 100})`,
                                transformOrigin: 'top left',
                                width: `${100 / (zoom / 100)}%`,
                                height: `${100 / (zoom / 100)}%`
                            }}
                        >
                            <iframe
                                src={htmlUrl}
                                className="w-full h-full border-0"
                                title="CV Preview"
                            />
                        </div>
                    ) : (
                        <div className="w-full h-full flex items-center justify-center">
                            <iframe
                                src={`${pdfUrl}#zoom=${zoom}`}
                                className="w-full h-full border-0"
                                title="PDF Preview"
                            />
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
}
