import { useEffect, useState, useMemo } from 'react';
import { Sparkles, Users, Globe, Briefcase, Zap, Cpu, Image, Clock, Coins, Calendar, Award, MapPin, Search, Filter, DollarSign, ArrowUpDown, PlusCircle, Play, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { RangeSlider } from './ui/RangeSlider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { ModelSelector } from './ui/ModelSelector';
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
        loadModels,
        configOptions,
        loadConfig,
        error
    } = useGenerationStore();

    // Load models and config on mount
    useEffect(() => {
        if (!modelsLoaded) {
            loadModels();
        }
        if (!configOptions.configLoaded) {
            loadConfig();
        }
    }, [modelsLoaded, loadModels, configOptions.configLoaded, loadConfig]);

    // Local state for performant sliders
    const [localQty, setLocalQty] = useState(config.qty);
    const [localAgeRange, setLocalAgeRange] = useState([config.age_min, config.age_max]);
    const [isAdded, setIsAdded] = useState(false);

    // Sync local state when config changes externally (e.g. loaded from DB or reset)
    useEffect(() => {
        setLocalQty(config.qty);
    }, [config.qty]);

    useEffect(() => {
        setLocalAgeRange([config.age_min, config.age_max]);
    }, [config.age_min, config.age_max]);

    // Error handling
    useEffect(() => {
        if (error) {
            toast.error('Generation Failed', {
                description: error
            });
        }
    }, [error]);

    // Use database options if available, fallback to hardcoded
    const ETHNICITY_OPTIONS_FINAL = configOptions.ethnicities.length > 0
        ? configOptions.ethnicities
        : ETHNICITY_OPTIONS;

    const LOCATION_OPTIONS_FINAL = configOptions.origins.length > 0
        ? configOptions.origins
        : LOCATION_OPTIONS;

    const EXPERTISE_OPTIONS_FINAL = configOptions.expertise_levels.length > 0
        ? configOptions.expertise_levels
        : EXPERTISE_OPTIONS;

    const GENDER_OPTIONS_FINAL = configOptions.genders.length > 0
        ? configOptions.genders
        : GENDER_OPTIONS;

    const handleGenerate = () => {
        startGeneration();
        if (isGenerating) {
            setIsAdded(true);
            setTimeout(() => setIsAdded(false), 2000);
            toast.info('Added to queue', {
                description: `${config.qty} more profiles will be generated.`
            });
        } else {
            toast.success('Generation started', {
                description: `Creating ${config.qty} unique profiles...`
            });
        }
    };

    // Get selected model info for display
    const selectedProfileModel = llmModels.find(m => m.id === config.profile_model);
    const selectedCvModel = llmModels.find(m => m.id === config.cv_model);
    const selectedImageModel = imageModels.find(m => m.id === config.image_model);

    // Prepare filtered models once to use in both dropdowns
    const filteredLlmModels = useMemo(() => {
        return llmModels
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
                // Sorting logic
                const sort = config.llmSort || 'default';

                // Helper to parse cost
                const getCostVal = (costStr) => {
                    if (!costStr) return 0;
                    if (costStr.toLowerCase().includes('free')) return 0;
                    const match = costStr.match(/\$(\d+\.?\d*)/);
                    return match ? parseFloat(match[1]) : 0;
                };

                const costA = getCostVal(a.cost);
                const costB = getCostVal(b.cost);

                if (sort === 'price_asc') {
                    if (costA !== costB) return costA - costB;
                } else if (sort === 'price_desc') {
                    if (costA !== costB) return costB - costA;
                } else {
                    // Default: Free first
                    const aFree = a.cost?.toLowerCase().includes('free') || a.cost === '$0.00/1M';
                    const bFree = b.cost?.toLowerCase().includes('free') || b.cost === '$0.00/1M';
                    if (aFree && !bFree) return -1;
                    if (!aFree && bFree) return 1;
                }

                // Tie-break alphabetically
                return a.name.localeCompare(b.name);
            });
    }, [llmModels, config.llmSearch, config.llmProvider, config.llmFreeOnly, config.llmSort]);


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
                        <span className="text-2xl font-bold gradient-text">{localQty}</span>
                    </div>
                    <Slider
                        value={[localQty]}
                        onValueChange={([value]) => setLocalQty(value)}
                        onValueCommit={([value]) => setConfig('qty', value)}
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
                        options={GENDER_OPTIONS_FINAL}
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
                        options={ETHNICITY_OPTIONS_FINAL}
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
                        options={LOCATION_OPTIONS_FINAL}
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
                            {localAgeRange[0]} - {localAgeRange[1]} years
                        </span>
                    </div>
                    <RangeSlider
                        value={localAgeRange}
                        onValueChange={(value) => setLocalAgeRange(value)}
                        onValueCommit={([min, max]) => {
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
                        options={EXPERTISE_OPTIONS_FINAL}
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
                        suggestions={configOptions.roles.length > 0 ? configOptions.roles : undefined}
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

                {/* LLM Model Selection Section */}
                <div className="space-y-4">

                    {/* Common Search and Filter Controls */}
                    <div className="space-y-2">
                        <Label className="flex items-center gap-2 mb-2">
                            <Cpu className="w-4 h-4 text-purple-400" />
                            Text Models (LLM)
                        </Label>

                        {/* Search Input */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <input
                                type="text"
                                placeholder="Search models (e.g. gpt, claude)..."
                                value={config.llmSearch || ''}
                                onChange={(e) => setConfig('llmSearch', e.target.value)}
                                className="w-full pl-9 pr-3 py-2 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>

                        {/* Filter Row: Provider | Sort | Free */}
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

                            {/* Sort Filter */}
                            <Select
                                value={config.llmSort || 'default'}
                                onValueChange={(value) => setConfig('llmSort', value)}
                            >
                                <SelectTrigger className="flex-1 h-8 text-xs">
                                    <ArrowUpDown className="w-3 h-3 mr-1" />
                                    <SelectValue placeholder="Sort" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="default">Default</SelectItem>
                                    <SelectItem value="price_asc">Price: Low to High</SelectItem>
                                    <SelectItem value="price_desc">Price: High to Low</SelectItem>
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

                    {/* Profile Model Selector */}
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">1. Profile Generator (Phase 1)</Label>
                        <ModelSelector
                            models={filteredLlmModels}
                            selectedId={config.profile_model}
                            onSelect={(id) => setConfig('profile_model', id)}
                            type="llm"
                        />
                        {selectedProfileModel && (
                            <p className="text-[10px] text-muted-foreground truncate px-1">{selectedProfileModel.description}</p>
                        )}
                    </div>

                    {/* CV Content Model Selector */}
                    <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">2. CV Content Writer (Phase 2)</Label>
                        <ModelSelector
                            models={filteredLlmModels}
                            selectedId={config.cv_model}
                            onSelect={(id) => setConfig('cv_model', id)}
                            type="llm"
                        />
                        {selectedCvModel && (
                            <p className="text-[10px] text-muted-foreground truncate px-1">{selectedCvModel.description}</p>
                        )}
                    </div>

                    <p className="text-xs text-muted-foreground text-center pt-2">
                        {filteredLlmModels.length} models available
                    </p>
                </div>

                {/* Image Model Select */}
                <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                        <Image className="w-4 h-4 text-cyan-400" />
                        Image Model (Krea)
                    </Label>
                    <ModelSelector
                        models={imageModels}
                        selectedId={config.image_model}
                        onSelect={(id) => setConfig('image_model', id)}
                        type="image"
                    />
                    {selectedImageModel && (
                        <div className="flex items-center gap-3 text-xs text-muted-foreground px-1">
                            <span>{selectedImageModel.description}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Generate Button - Fixed at bottom */}
            <div className="p-6 border-t border-border/50 flex-shrink-0">
                <Button
                    onClick={handleGenerate}
                    disabled={false}
                    variant={isGenerating ? "outline" : "gradient"}
                    size="lg"
                    className="w-full relative overflow-hidden transition-all duration-300"
                >
                    {isGenerating ? (
                        <div className="flex items-center justify-center gap-2">
                            {isAdded ? (
                                <>
                                    <div className="bg-white/20 text-white rounded-full p-0.5">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                                    </div>
                                    <span className="font-bold">Added to Queue!</span>
                                </>
                            ) : (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                                    <span>Add to Queue</span>
                                </>
                            )}
                            {/* Subtle progress indicator background */}
                            <div className="absolute bottom-0 left-0 h-1 bg-primary/20 w-full">
                                <div className="h-full bg-primary/50 animate-pulse w-full"></div>
                            </div>
                        </div>
                    ) : (
                        <>
                            <Sparkles className="w-5 h-5 mr-2" />
                            Generate Batch
                        </>
                    )}
                </Button>
                {isGenerating && (
                    <p className="text-[10px] text-center text-muted-foreground mt-2">
                        Generation in progress. Adding more will queue them.
                    </p>
                )}
            </div>
        </aside>
    );
}
