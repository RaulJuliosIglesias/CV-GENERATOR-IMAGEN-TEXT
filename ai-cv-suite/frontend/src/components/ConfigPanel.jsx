import { useEffect } from 'react';
import { Sparkles, Users, Globe, Briefcase, Zap, Cpu, Image, Clock, Coins } from 'lucide-react';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { Input } from './ui/Input';
import { Label } from './ui/Label';
import useGenerationStore from '../stores/useGenerationStore';

const GENDER_OPTIONS = [
    { value: 'any', label: 'Any Gender' },
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
];

const ETHNICITY_OPTIONS = [
    { value: 'any', label: 'Any Ethnicity' },
    { value: 'asian', label: 'Asian' },
    { value: 'caucasian', label: 'Caucasian' },
    { value: 'african', label: 'African' },
    { value: 'hispanic', label: 'Hispanic' },
    { value: 'middle-eastern', label: 'Middle Eastern' },
    { value: 'mixed', label: 'Mixed' },
];

export default function ConfigPanel() {
    const {
        config,
        setConfig,
        startGeneration,
        isGenerating,
        llmModels,
        imageModels,
        modelsLoaded,
        loadModels
    } = useGenerationStore();

    // Load models on mount
    useEffect(() => {
        if (!modelsLoaded) {
            loadModels();
        }
    }, [modelsLoaded, loadModels]);

    const handleGenerate = () => {
        startGeneration();
    };

    // Get selected model info for display
    const selectedLlmModel = llmModels.find(m => m.id === config.llm_model);
    const selectedImageModel = imageModels.find(m => m.id === config.image_model);

    return (
        <aside className="w-96 h-screen bg-card/50 backdrop-blur-xl border-r border-border/50 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-border/50">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold gradient-text">AI CV Suite</h1>
                        <p className="text-xs text-muted-foreground">Resume Generator</p>
                    </div>
                </div>
            </div>

            {/* Configuration Form */}
            <div className="flex-1 overflow-y-auto p-6 space-y-5">
                {/* Quantity Slider */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            Quantity
                        </Label>
                        <span className="text-2xl font-bold gradient-text">{config.qty}</span>
                    </div>
                    <Slider
                        value={[config.qty]}
                        onValueChange={([value]) => setConfig('qty', value)}
                        min={1}
                        max={20}
                        step={1}
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>1</span>
                        <span>20</span>
                    </div>
                </div>

                {/* Divider */}
                <div className="border-t border-border/50 pt-4">
                    <p className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wider">CV Configuration</p>
                </div>

                {/* Gender Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-pink-400" />
                        Gender
                    </Label>
                    <Select value={config.gender} onValueChange={(value) => setConfig('gender', value)}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                            {GENDER_OPTIONS.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Ethnicity Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-blue-400" />
                        Ethnicity
                    </Label>
                    <Select value={config.ethnicity} onValueChange={(value) => setConfig('ethnicity', value)}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select ethnicity" />
                        </SelectTrigger>
                        <SelectContent>
                            {ETHNICITY_OPTIONS.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Origin Input */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-green-400" />
                        Region / Origin
                    </Label>
                    <Input
                        value={config.origin}
                        onChange={(e) => setConfig('origin', e.target.value)}
                        placeholder="e.g., Europe, United States, Asia"
                    />
                </div>

                {/* Role Input */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-orange-400" />
                        Target Role
                    </Label>
                    <Input
                        value={config.role}
                        onChange={(e) => setConfig('role', e.target.value)}
                        placeholder="e.g., Software Developer, DevOps Engineer"
                    />
                </div>

                {/* Divider */}
                <div className="border-t border-border/50 pt-4">
                    <p className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wider">AI Models</p>
                </div>

                {/* LLM Model Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-purple-400" />
                        Text Model (LLM)
                    </Label>
                    <Select
                        value={config.llm_model || ''}
                        onValueChange={(value) => setConfig('llm_model', value)}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select LLM model" />
                        </SelectTrigger>
                        <SelectContent>
                            {llmModels.map((model) => (
                                <SelectItem key={model.id} value={model.id}>
                                    <div className="flex flex-col">
                                        <span>{model.name}</span>
                                        <span className="text-xs text-muted-foreground">{model.cost}</span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    {selectedLlmModel && (
                        <p className="text-xs text-muted-foreground">{selectedLlmModel.description}</p>
                    )}
                </div>

                {/* Image Model Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Image className="w-4 h-4 text-cyan-400" />
                        Image Model (Krea)
                    </Label>
                    <Select
                        value={config.image_model || ''}
                        onValueChange={(value) => setConfig('image_model', value)}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select image model" />
                        </SelectTrigger>
                        <SelectContent>
                            {imageModels.map((model) => (
                                <SelectItem key={model.id} value={model.id}>
                                    <div className="flex items-center justify-between w-full gap-4">
                                        <span>{model.name}</span>
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                            <Clock className="w-3 h-3" />
                                            <span>{model.time}</span>
                                            <Coins className="w-3 h-3 ml-1" />
                                            <span>{model.compute_units}</span>
                                        </div>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    {selectedImageModel && (
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <span>{selectedImageModel.description}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Generate Button */}
            <div className="p-6 border-t border-border/50">
                <Button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    variant="gradient"
                    size="lg"
                    className="w-full"
                >
                    {isGenerating ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generating...
                        </>
                    ) : (
                        <>
                            <Sparkles className="w-5 h-5 mr-2" />
                            Generate Batch
                        </>
                    )}
                </Button>
            </div>
        </aside>
    );
}
