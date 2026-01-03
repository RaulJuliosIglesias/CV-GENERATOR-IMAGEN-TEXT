import * as React from "react"
import { Check, X, ChevronDown } from "lucide-react"
import * as PopoverPrimitive from "@radix-ui/react-popover"
import { cn } from "../../lib/utils"
import { Badge } from "./Badge"

const MultiSelect = React.forwardRef(({
    options = [],
    value = [],
    onChange,
    placeholder = "Select items...",
    className
}, ref) => {
    const [open, setOpen] = React.useState(false)

    const handleToggle = (optionValue) => {
        const newValue = value.includes(optionValue)
            ? value.filter(v => v !== optionValue)
            : [...value, optionValue]
        onChange(newValue)
    }

    const handleRemove = (optionValue, e) => {
        e.stopPropagation()
        onChange(value.filter(v => v !== optionValue))
    }

    const selectedLabels = options
        .filter(opt => value.includes(opt.value))
        .map(opt => opt.label)

    return (
        <PopoverPrimitive.Root open={open} onOpenChange={setOpen}>
            <PopoverPrimitive.Trigger asChild>
                <div
                    ref={ref}
                    className={cn(
                        "flex min-h-10 w-full items-center justify-between rounded-xl border border-input/50 bg-background/50 px-3 py-2 text-sm ring-offset-background cursor-pointer hover:bg-accent/50 transition-all duration-200 backdrop-blur-sm shadow-sm",
                        className
                    )}
                >
                    <div className="flex flex-wrap gap-1 flex-1">
                        {value.length === 0 ? (
                            <span className="text-muted-foreground">{placeholder}</span>
                        ) : (
                            selectedLabels.map((label, index) => (
                                <Badge
                                    key={index}
                                    variant="secondary"
                                    className="gap-1 bg-secondary/80 backdrop-blur-md"
                                >
                                    {label}
                                    <X
                                        className="h-3 w-3 cursor-pointer hover:text-destructive transition-colors"
                                        onClick={(e) => handleRemove(value[index], e)}
                                    />
                                </Badge>
                            ))
                        )}
                    </div>
                    <ChevronDown
                        className={cn(
                            "h-4 w-4 opacity-50 transition-transform duration-200",
                            open && "transform rotate-180"
                        )}
                    />
                </div>
            </PopoverPrimitive.Trigger>
            <PopoverPrimitive.Portal>
                <PopoverPrimitive.Content
                    className="z-50 w-[var(--radix-popover-trigger-width)] rounded-xl border border-white/10 bg-card/95 p-1 text-card-foreground shadow-2xl backdrop-blur-xl outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2"
                    align="start"
                    sideOffset={5}
                >
                    <div className="max-h-60 overflow-y-auto p-1 custom-scrollbar">
                        {options.map((option) => {
                            const isSelected = value.includes(option.value)
                            return (
                                <div
                                    key={option.value}
                                    onClick={() => handleToggle(option.value)}
                                    className={cn(
                                        "relative flex cursor-pointer select-none items-center rounded-lg px-2 py-2 text-sm outline-none transition-colors duration-150",
                                        isSelected
                                            ? "bg-primary/20 text-primary"
                                            : "hover:bg-accent hover:text-accent-foreground"
                                    )}
                                >
                                    <div className={cn(
                                        "flex h-4 w-4 items-center justify-center rounded border mr-2 transition-colors",
                                        isSelected
                                            ? "bg-primary border-primary"
                                            : "border-muted-foreground/30"
                                    )}>
                                        {isSelected && <Check className="h-3 w-3 text-primary-foreground" />}
                                    </div>
                                    <span>{option.label}</span>
                                </div>
                            )
                        })}
                    </div>
                </PopoverPrimitive.Content>
            </PopoverPrimitive.Portal>
        </PopoverPrimitive.Root>
    )
})
MultiSelect.displayName = "MultiSelect"

export { MultiSelect }
