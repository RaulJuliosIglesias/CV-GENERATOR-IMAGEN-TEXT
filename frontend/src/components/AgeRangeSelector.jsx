import { useState, useEffect } from 'react';
import { Calendar } from 'lucide-react';
import { Label } from './ui/Label';
import { RangeSlider } from './ui/RangeSlider';
import useGenerationStore from '../stores/useGenerationStore';

export function AgeRangeSelector() {
    const config = useGenerationStore(state => state.config);
    const setConfig = useGenerationStore(state => state.setConfig);

    // Default range if not set
    const initialRange = [config.age_min || 25, config.age_max || 45];
    const [localRange, setLocalRange] = useState(initialRange);

    // Sync from global if it changes externally
    useEffect(() => {
        setLocalRange([config.age_min || 25, config.age_max || 45]);
    }, [config.age_min, config.age_max]);

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <Label className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-cyan-400" />
                    Age Range
                </Label>
                <span className="text-sm font-semibold text-primary">
                    {localRange[0]} - {localRange[1]} years
                </span>
            </div>
            <RangeSlider
                value={localRange}
                onValueChange={(val) => setLocalRange(val)}
                onValueCommit={([min, max]) => {
                    setLocalRange([min, max]);
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
    );
}
