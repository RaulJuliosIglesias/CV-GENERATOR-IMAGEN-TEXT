import { useState } from 'react';
import { Code, Save, RotateCcw, CheckCircle2, XCircle } from 'lucide-react';
import { Button } from './ui/Button';
import { Label } from './ui/Label';
import useGenerationStore from '../stores/useGenerationStore';
import { saveConfig } from '../lib/storage';
import { toast } from 'sonner';

/**
 * ConfigEditor - Editor JSON para configuración avanzada
 */
export default function ConfigEditor() {
    const config = useGenerationStore(s => s.config);
    const setConfig = useGenerationStore(s => s.setConfig);
    const [isOpen, setIsOpen] = useState(false);
    const [jsonText, setJsonText] = useState('');
    const [isValid, setIsValid] = useState(true);
    const [error, setError] = useState('');

    const openEditor = () => {
        setJsonText(JSON.stringify(config, null, 2));
        setIsValid(true);
        setError('');
        setIsOpen(true);
    };

    const validateJSON = (text) => {
        try {
            const parsed = JSON.parse(text);
            setIsValid(true);
            setError('');
            return parsed;
        } catch (e) {
            setIsValid(false);
            setError(e.message);
            return null;
        }
    };

    const handleTextChange = (text) => {
        setJsonText(text);
        validateJSON(text);
    };

    const handleSave = () => {
        const parsed = validateJSON(jsonText);
        if (parsed) {
            // Validate required fields
            const requiredFields = ['qty', 'genders', 'ethnicities', 'origins', 'roles'];
            const missingFields = requiredFields.filter(field => !(field in parsed));
            
            if (missingFields.length > 0) {
                setError(`Missing required fields: ${missingFields.join(', ')}`);
                setIsValid(false);
                return;
            }

            // Apply config
            Object.entries(parsed).forEach(([key, value]) => {
                setConfig(key, value);
            });

            saveConfig(parsed);
            toast.success('Configuration saved');
            setIsOpen(false);
        }
    };

    const handleReset = () => {
        setJsonText(JSON.stringify(config, null, 2));
        setIsValid(true);
        setError('');
    };

    return (
        <>
            <Button
                variant="outline"
                size="sm"
                onClick={openEditor}
                className="h-7 px-2 text-xs"
            >
                <Code className="w-3 h-3 mr-1" />
                JSON Editor
            </Button>

            {isOpen && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
                    <div className="bg-card border border-border rounded-xl w-full max-w-4xl h-[80vh] flex flex-col overflow-hidden">
                        {/* Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
                            <div className="flex items-center gap-3">
                                <Code className="w-5 h-5 text-primary" />
                                <h2 className="text-lg font-bold">JSON Configuration Editor</h2>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setIsOpen(false)}
                            >
                                <XCircle className="w-5 h-5" />
                            </Button>
                        </div>

                        {/* Editor */}
                        <div className="flex-1 flex flex-col overflow-hidden">
                            <div className="px-6 py-2 border-b border-border flex items-center justify-between">
                                <Label className="text-sm">Configuration JSON</Label>
                                <div className="flex items-center gap-2">
                                    {isValid ? (
                                        <div className="flex items-center gap-1 text-xs text-success">
                                            <CheckCircle2 className="w-4 h-4" />
                                            Valid JSON
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-1 text-xs text-destructive">
                                            <XCircle className="w-4 h-4" />
                                            Invalid JSON
                                        </div>
                                    )}
                                </div>
                            </div>
                            <textarea
                                value={jsonText}
                                onChange={(e) => handleTextChange(e.target.value)}
                                className="flex-1 font-mono text-sm p-4 bg-background border-0 resize-none focus:outline-none"
                                spellCheck={false}
                            />
                            {error && (
                                <div className="px-6 py-2 bg-destructive/10 border-t border-destructive/20">
                                    <p className="text-xs text-destructive">{error}</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between px-6 py-4 border-t border-border">
                            <Button
                                variant="outline"
                                onClick={handleReset}
                                className="flex items-center gap-2"
                            >
                                <RotateCcw className="w-4 h-4" />
                                Reset
                            </Button>
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    onClick={() => setIsOpen(false)}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSave}
                                    disabled={!isValid}
                                    className="flex items-center gap-2"
                                >
                                    <Save className="w-4 h-4" />
                                    Save Configuration
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
