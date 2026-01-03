import React from 'react';
import { Check, Image as ImageIcon, Zap, DollarSign, Clock, Coins } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from './Badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './Select';

export function ModelSelector({
    models = [],
    selectedId,
    onSelect,
    type = 'llm', // 'llm' or 'image'
    placeholder = "Select model..."
}) {

    const selectedModel = models.find(m => m.id === selectedId);

    return (
        <Select
            value={selectedId || ''}
            onValueChange={onSelect}
        >
            <SelectTrigger className="w-full h-auto py-2">
                <SelectValue placeholder={placeholder}>
                    {selectedModel ? (
                        <div className="flex items-center justify-between w-full gap-2 pr-4">
                            <span className="font-medium truncate">{selectedModel.name}</span>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground shrink-0 opacity-70">
                                {type === 'image' ? (
                                    <>
                                        <Clock className="w-3 h-3" />
                                        <span>{selectedModel.time}</span>
                                    </>
                                ) : (
                                    <>
                                        <span className="uppercase text-[10px] bg-primary/10 px-1 rounded">{selectedModel.provider}</span>
                                    </>
                                )}
                            </div>
                        </div>
                    ) : (
                        <span className="text-muted-foreground">{placeholder}</span>
                    )}
                </SelectValue>
            </SelectTrigger>
            <SelectContent className="max-h-80">
                {models.map((model) => {
                    const isFree = model.cost?.toLowerCase().includes('free') || model.cost === '$0.00/1M';

                    return (
                        <SelectItem key={model.id} value={model.id} className="py-2">
                            <div className="flex flex-col w-full gap-1">
                                <div className="flex items-center justify-between">
                                    <span className="font-medium text-sm">{model.name}</span>
                                    {type === 'image' && (
                                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                            <Zap className="w-3 h-3 text-yellow-500/70" />
                                            <span>{model.time}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                    <div className="flex items-center gap-2">
                                        <Badge variant="secondary" className="h-4 px-1 text-[10px] font-normal">
                                            {model.provider || (type === 'image' ? 'KREA' : 'LLM')}
                                        </Badge>
                                        {/* Show simple description snippet if needed, or omit for cleaner look */}
                                    </div>
                                    <span className={cn(
                                        "flex items-center gap-0.5",
                                        isFree ? "text-green-400" : "text-muted-foreground"
                                    )}>
                                        <DollarSign className="w-2.5 h-2.5" />
                                        {model.cost || model.compute_units || "Free"}
                                    </span>
                                </div>
                            </div>
                        </SelectItem>
                    );
                })}
            </SelectContent>
        </Select>
    );
}
