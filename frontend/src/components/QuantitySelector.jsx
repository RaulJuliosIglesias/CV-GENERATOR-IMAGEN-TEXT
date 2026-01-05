import { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';
import { Label } from './ui/Label';
import { Slider } from './ui/Slider';
import useGenerationStore from '../stores/useGenerationStore';

export function QuantitySelector() {
    const configQty = useGenerationStore(state => state.config.qty);
    const setConfig = useGenerationStore(state => state.setConfig);

    // Local state for smooth sliding without global updates
    const [localValue, setLocalValue] = useState(configQty || 1);

    // Sync from global if it changes externally
    useEffect(() => {
        setLocalValue(configQty || 1);
    }, [configQty]);

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <Label className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    Quantity
                </Label>
                <span className="text-2xl font-bold gradient-text">{localValue}</span>
            </div>
            <Slider
                value={[localValue]}
                onValueChange={([val]) => setLocalValue(val)}
                onValueCommit={([val]) => {
                    setLocalValue(val);
                    setConfig('qty', val);
                }}
                min={1}
                max={50}
                step={1}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
                <span>1</span>
                <span>50</span>
            </div>
        </div>
    );
}
