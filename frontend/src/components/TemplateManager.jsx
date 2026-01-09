import { useState, useEffect } from 'react';
import { Save, FolderOpen, Trash2, Download, Upload, X, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Label } from './ui/Label';
import useGenerationStore from '../stores/useGenerationStore';
import { saveTemplate, loadTemplates, deleteTemplate, exportConfig, importConfig } from '../lib/storage';
import { toast } from 'sonner';

/**
 * TemplateManager - Componente para gestionar templates guardados
 */
export default function TemplateManager() {
    const config = useGenerationStore(s => s.config);
    const loadTemplates = useGenerationStore(s => s.loadTemplates);
    const loadTemplate = useGenerationStore(s => s.loadTemplate);
    const deleteTemplateAction = useGenerationStore(s => s.deleteTemplate);
    const templates = useGenerationStore(s => s.templates);
    
    // Load collapsed state from localStorage
    const [isCollapsed, setIsCollapsed] = useState(() => {
        const saved = localStorage.getItem('template-manager-collapsed');
        return saved ? JSON.parse(saved) : true; // Collapsed by default
    });
    
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [templateName, setTemplateName] = useState('');
    const [templateDescription, setTemplateDescription] = useState('');
    const [showImportModal, setShowImportModal] = useState(false);
    
    // Save collapsed state to localStorage
    useEffect(() => {
        localStorage.setItem('template-manager-collapsed', JSON.stringify(isCollapsed));
    }, [isCollapsed]);

    useEffect(() => {
        // Load templates on mount
        loadTemplates();
    }, [loadTemplates]);

    const handleSaveTemplate = () => {
        if (!templateName.trim()) {
            toast.error('Template name is required');
            return;
        }

        try {
            const template = saveTemplate(templateName.trim(), templateDescription.trim());
            loadTemplates();
            setShowSaveModal(false);
            setTemplateName('');
            setTemplateDescription('');
            toast.success(`Template "${template.name}" saved successfully`);
        } catch (error) {
            toast.error(`Failed to save template: ${error.message}`);
        }
    };

    const handleLoadTemplate = (templateId) => {
        try {
            const template = loadTemplate(templateId);
            if (template) {
                toast.success(`Template "${template.name}" loaded`);
            } else {
                toast.error('Template not found');
            }
        } catch (error) {
            toast.error(`Failed to load template: ${error.message}`);
        }
    };

    const handleDeleteTemplate = (templateId, templateName) => {
        if (confirm(`Delete template "${templateName}"?`)) {
            try {
                deleteTemplateAction(templateId);
                loadTemplates();
                toast.success('Template deleted');
            } catch (error) {
                toast.error(`Failed to delete template: ${error.message}`);
            }
        }
    };

    const handleExportConfig = () => {
        try {
            exportConfig(config);
            toast.success('Configuration exported');
        } catch (error) {
            toast.error(`Failed to export: ${error.message}`);
        }
    };

    const handleImportConfig = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedConfig = importConfig(e.target.result);
                // Apply imported config
                Object.entries(importedConfig).forEach(([key, value]) => {
                    useGenerationStore.getState().setConfig(key, value);
                });
                setShowImportModal(false);
                toast.success('Configuration imported successfully');
            } catch (error) {
                toast.error(`Failed to import: ${error.message}`);
            }
        };
        reader.readAsText(file);
    };

    return (
        <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
            {/* Header - Always visible, clickable to collapse */}
            <div
                className="flex items-center justify-between p-3 cursor-pointer hover:bg-card/70 transition-colors"
                onClick={() => setIsCollapsed(!isCollapsed)}
            >
                <div className="flex items-center gap-2">
                    <FolderOpen className="w-4 h-4 text-primary" />
                    <h3 className="text-sm font-semibold text-foreground">Templates</h3>
                    <span className="text-xs text-muted-foreground">
                        ({templates.length})
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    {!isCollapsed && (
                        <>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowSaveModal(true);
                                }}
                                className="h-7 px-2 text-xs"
                            >
                                <Save className="w-3 h-3 mr-1" />
                                Save
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleExportConfig();
                                }}
                                className="h-7 px-2 text-xs"
                                title="Export configuration"
                            >
                                <Download className="w-3 h-3" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowImportModal(true);
                                }}
                                className="h-7 px-2 text-xs"
                                title="Import configuration"
                            >
                                <Upload className="w-3 h-3" />
                            </Button>
                        </>
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
                    {/* Templates List */}
                    {templates.length === 0 ? (
                <div className="text-center py-8 text-sm text-muted-foreground">
                    <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No templates saved yet</p>
                    <p className="text-xs mt-1">Save your current configuration as a template</p>
                </div>
            ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {templates.map((template) => (
                        <div
                            key={template.id}
                            className="flex items-center justify-between p-2 rounded border border-border/50 hover:bg-accent/20 transition-colors group"
                        >
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <FolderOpen className="w-4 h-4 text-muted-foreground shrink-0" />
                                    <div className="min-w-0 flex-1">
                                        <p className="text-sm font-medium text-foreground truncate">
                                            {template.name}
                                        </p>
                                        {template.description && (
                                            <p className="text-xs text-muted-foreground truncate">
                                                {template.description}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleLoadTemplate(template.id)}
                                    className="h-7 px-2 text-xs"
                                    title="Load template"
                                >
                                    Load
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleDeleteTemplate(template.id, template.name)}
                                    className="h-7 px-2 text-xs text-red-400 hover:text-red-500"
                                    title="Delete template"
                                >
                                    <Trash2 className="w-3 h-3" />
                                </Button>
                            </div>
                        </div>
                    ))}
                    </div>
                )}
                </div>
            )}

            {/* Save Template Modal */}
            {showSaveModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold">Save Template</h3>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setShowSaveModal(false)}
                                className="h-6 w-6"
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <Label htmlFor="template-name">Template Name</Label>
                                <Input
                                    id="template-name"
                                    value={templateName}
                                    onChange={(e) => setTemplateName(e.target.value)}
                                    placeholder="e.g., Junior Developer Template"
                                    className="mt-1"
                                    autoFocus
                                />
                            </div>
                            <div>
                                <Label htmlFor="template-desc">Description (optional)</Label>
                                <Input
                                    id="template-desc"
                                    value={templateDescription}
                                    onChange={(e) => setTemplateDescription(e.target.value)}
                                    placeholder="Brief description..."
                                    className="mt-1"
                                />
                            </div>
                            <div className="flex items-center gap-2 justify-end">
                                <Button
                                    variant="outline"
                                    onClick={() => setShowSaveModal(false)}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSaveTemplate}
                                    disabled={!templateName.trim()}
                                >
                                    Save Template
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Import Modal */}
            {showImportModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold">Import Configuration</h3>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setShowImportModal(false)}
                                className="h-6 w-6"
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-4">
                            <p className="text-sm text-muted-foreground">
                                Select a JSON configuration file to import
                            </p>
                            <div>
                                <Label htmlFor="import-file">Configuration File</Label>
                                <Input
                                    id="import-file"
                                    type="file"
                                    accept=".json"
                                    onChange={handleImportConfig}
                                    className="mt-1"
                                />
                            </div>
                            <div className="flex items-center gap-2 justify-end">
                                <Button
                                    variant="outline"
                                    onClick={() => setShowImportModal(false)}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
