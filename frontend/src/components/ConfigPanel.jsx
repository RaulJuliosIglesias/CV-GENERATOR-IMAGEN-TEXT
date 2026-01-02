import { useEffect, useState, useMemo } from 'react';
import { Sparkles, Users, Globe, Briefcase, Zap, Cpu, Image, Clock, Coins, Calendar, Award, MapPin, Search, Filter, DollarSign } from 'lucide-react';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { RangeSlider } from './ui/RangeSlider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { Label } from './ui/Label';
import { MultiSelect } from './ui/MultiSelect';
import { TagInput } from './ui/TagInput';
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

// Hierarchical location options
const LOCATION_OPTIONS = [
    { value: 'any', label: '🌍 Any Location' },
    { value: '---continent', label: '--- Continents ---', disabled: true },
    { value: 'Europe', label: '🇪🇺 Europe' },
    { value: 'Asia', label: '🌏 Asia' },
    { value: 'North America', label: '🌎 North America' },
    { value: 'South America', label: '🌎 South America' },
    { value: 'Africa', label: '🌍 Africa' },
    { value: 'Oceania', label: '🌏 Oceania' },
    { value: '---countries', label: '--- Countries ---', disabled: true },
    { value: 'United States', label: '🇺🇸 United States' },
    { value: 'United Kingdom', label: '🇬🇧 United Kingdom' },
    { value: 'Germany', label: '🇩🇪 Germany' },
    { value: 'France', label: '🇫🇷 France' },
    { value: 'Spain', label: '🇪🇸 Spain' },
    { value: 'Italy', label: '🇮🇹 Italy' },
    { value: 'Netherlands', label: '🇳🇱 Netherlands' },
    { value: 'Canada', label: '🇨🇦 Canada' },
    { value: 'Australia', label: '🇦🇺 Australia' },
    { value: 'China', label: '🇨🇳 China' },
    { value: 'Japan', label: '🇯🇵 Japan' },
    { value: 'India', label: '🇮🇳 India' },
    { value: 'Brazil', label: '🇧🇷 Brazil' },
    { value: 'Mexico', label: '🇲🇽 Mexico' },
    { value: 'Singapore', label: '🇸🇬 Singapore' },
].filter(opt => !opt.disabled);

const EXPERTISE_OPTIONS = [
    { value: 'any', label: 'Any Level' },
    { value: 'junior', label: 'Junior (0-2 years)' },
    { value: 'mid', label: 'Mid-Level (2-5 years)' },
    { value: 'senior', label: 'Senior (5-10 years)' },
    { value: 'expert', label: 'Expert (10+ years)' },
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
        <aside className="w-96 h-screen bg-card/50 backdrop-blur-xl border-r border-border/50 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-border/50 flex-shrink-0">
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

            {/* Configuration Form - Scrollable */}
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
                        max={50}
                        step={1}
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>1</span>
                        <span>50</span>
                    </div>
                </div>

                {/* Divider */}
                <div className="border-t border-border/50 pt-4">
                    <p className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wider">Profile Configuration</p>
                </div>

                {/* Gender Multi-Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-pink-400" />
                        Gender
                    </Label>
                    <MultiSelect
                        options={GENDER_OPTIONS}
                        value={config.genders}
                        onChange={(value) => setConfig('genders', value)}
                        placeholder="Select genders..."
                    />
                </div>

                {/* Ethnicity Multi-Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-blue-400" />
                        Ethnicity
                    </Label>
                    <MultiSelect
                        options={ETHNICITY_OPTIONS}
                        value={config.ethnicities}
                        onChange={(value) => setConfig('ethnicities', value)}
                        placeholder="Select ethnicities..."
                    />
                </div>

                {/* Location Multi-Select with Hierarchy */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-green-400" />
                        Location / Origin
                    </Label>
                    <MultiSelect
                        options={LOCATION_OPTIONS}
                        value={config.origins}
                        onChange={(value) => setConfig('origins', value)}
                        placeholder="Select locations..."
                    />
                    <p className="text-xs text-muted-foreground">Continents or specific countries</p>
                </div>

                {/* Age Range Slider */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-cyan-400" />
                            Age Range
                        </Label>
                        <span className="text-sm font-semibold text-primary">
                            {config.age_min} - {config.age_max} years
                        </span>
                    </div>
                    <RangeSlider
                        value={[config.age_min, config.age_max]}
                        onValueChange={([min, max]) => {
                            setConfig('age_min', min);
                            setConfig('age_max', max);
                        }}
                        min={18}
                        max={70}
                        step={1}
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>18</span>
                        <span>70</span>
                    </div>
                </div>

                {/* Expertise Multi-Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Award className="w-4 h-4 text-purple-400" />
                        Expertise Level
                    </Label>
                    <MultiSelect
                        options={EXPERTISE_OPTIONS}
                        value={config.expertise_levels}
                        onChange={(value) => setConfig('expertise_levels', value)}
                        placeholder="Select expertise levels..."
                    />
                </div>

                {/* Target Roles - Custom Tags */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-orange-400" />
                        Target Roles
                    </Label>
                    <TagInput
                        value={config.roles}
                        onChange={(value) => setConfig('roles', value)}
                        placeholder="Type to search or add custom roles..."
                    />
                    <p className="text-xs text-muted-foreground">
                        Search suggestions or add any custom role
                    </p>
                </div>

                {/* Remote Work */}
                <div className="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        id="remote"
                        checked={config.remote}
                        onChange={(e) => setConfig('remote', e.target.checked)}
                        className="w-4 h-4 rounded border-input bg-background"
                    />
                    <Label htmlFor="remote" className="text-sm cursor-pointer">
                        Include remote work preference
                    </Label>
                </div>

                {/* Divider */}
                <div className="border-t border-border/50 pt-4">
                    <p className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wider">AI Models</p>
                </div>

                {/* LLM Model Select - Enhanced with Search, Filter, Sort */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-purple-400" />
                        Text Model (LLM)
                    </Label>

                    {/* Search and Filters */}
                    <div className="space-y-2">
                        {/* Search Input */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <input
                                type="text"
                                placeholder="Search models..."
                                value={config.llmSearch || ''}
                                onChange={(e) => setConfig('llmSearch', e.target.value)}
                                className="w-full pl-9 pr-3 py-2 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>

                        {/* Filter Row */}
                        <div className="flex gap-2">
                            {/* Provider Filter */}
                            <Select
                                value={config.llmProvider || 'all'}
                                onValueChange={(value) => setConfig('llmProvider', value)}
                            >
                                <SelectTrigger className="flex-1 h-8 text-xs">
                                    <Filter className="w-3 h-3 mr-1" />
                                    <SelectValue placeholder="Provider" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Providers</SelectItem>
                                    {[...new Set(llmModels.map(m => m.provider))].sort().map(provider => (
                                        <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>

                            {/* Free Only Toggle */}
                            <button
                                onClick={() => setConfig('llmFreeOnly', !config.llmFreeOnly)}
                                className={`px-3 h-8 text-xs rounded-md border transition-colors flex items-center gap-1 ${config.llmFreeOnly
                                        ? 'bg-green-500/20 border-green-500 text-green-400'
                                        : 'border-input text-muted-foreground hover:bg-accent'
                                    }`}
                            >
                                <DollarSign className="w-3 h-3" />
                                Free
                            </button>
                        </div>
                    </div>

                    {/* Model List */}
                    <Select
                        value={config.llm_model || ''}
                        onValueChange={(value) => setConfig('llm_model', value)}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select LLM model" />
                        </SelectTrigger>
                        <SelectContent className="max-h-80">
                            {llmModels
                                .filter(model => {
                                    const search = (config.llmSearch || '').toLowerCase();
                                    const matchesSearch = !search ||
                                        model.name.toLowerCase().includes(search) ||
                                        model.id.toLowerCase().includes(search) ||
                                        model.provider?.toLowerCase().includes(search);
                                    const matchesProvider = !config.llmProvider || config.llmProvider === 'all' ||
                                        model.provider === config.llmProvider;
                                    const matchesFree = !config.llmFreeOnly ||
                                        model.cost?.toLowerCase().includes('free') ||
                                        model.cost === '$0.00/1M';
                                    return matchesSearch && matchesProvider && matchesFree;
                                })
                                .sort((a, b) => {
                                    // Sort by cost (free first, then by price)
                                    const aFree = a.cost?.toLowerCase().includes('free') || a.cost === '$0.00/1M';
                                    const bFree = b.cost?.toLowerCase().includes('free') || b.cost === '$0.00/1M';
                                    if (aFree && !bFree) return -1;
                                    if (!aFree && bFree) return 1;
                                    // Then alphabetically
                                    return a.name.localeCompare(b.name);
                                })
                                .map((model) => (
                                    <SelectItem key={model.id} value={model.id}>
                                        <div className="flex flex-col py-1">
                                            <span className="font-medium">{model.name}</span>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <span className="text-blue-400">{model.provider}</span>
                                                <span>•</span>
                                                <span className={model.cost?.toLowerCase().includes('free') ? 'text-green-400' : ''}>{model.cost}</span>
                                            </div>
                                        </div>
                                    </SelectItem>
                                ))}
                        </SelectContent>
                    </Select>
                    {selectedLlmModel && (
                        <p className="text-xs text-muted-foreground">{selectedLlmModel.description}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                        {llmModels.filter(m => {
                            const search = (config.llmSearch || '').toLowerCase();
                            const matchesSearch = !search || m.name.toLowerCase().includes(search) || m.id.toLowerCase().includes(search);
                            const matchesProvider = !config.llmProvider || config.llmProvider === 'all' || m.provider === config.llmProvider;
                            const matchesFree = !config.llmFreeOnly || m.cost?.toLowerCase().includes('free') || m.cost === '$0.00/1M';
                            return matchesSearch && matchesProvider && matchesFree;
                        }).length} models available
                    </p>
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
                        <SelectContent className="max-h-80">
                            {imageModels.map((model) => (
                                <SelectItem key={model.id} value={model.id}>
                                    <div className="flex items-center justify-between w-full gap-4 py-1">
                                        <span className="font-medium">{model.name}</span>
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground shrink-0">
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

            {/* Generate Button - Fixed at bottom */}
            <div className="p-6 border-t border-border/50 flex-shrink-0">
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
