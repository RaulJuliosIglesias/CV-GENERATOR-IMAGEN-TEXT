import React from 'react';
import { X, ExternalLink, Download, FileText } from 'lucide-react';
import { Button } from './ui/Button';
import { getHtmlUrl, getPdfUrl } from '../lib/api';
import { motion } from 'framer-motion';

export function PreviewModal({ filename, onClose }) {
    if (!filename) return null;

    const htmlUrl = getHtmlUrl(filename);
    const pdfUrl = getPdfUrl(filename);

    const handleDownloadPdf = () => {
        window.open(pdfUrl, '_blank');
    };

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

                {/* Content - Iframe */}
                <div className="flex-1 bg-white/5 relative">
                    <iframe
                        src={htmlUrl}
                        className="w-full h-full border-0"
                        title="CV Preview"
                    />
                </div>
            </motion.div>
        </div>
    );
}
