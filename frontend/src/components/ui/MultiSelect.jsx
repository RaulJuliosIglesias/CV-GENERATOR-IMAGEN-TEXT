import * as React from "react"
import { Check, X } from "lucide-react"
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
        <div className="relative" ref={ref}>
            <div
                onClick={() => setOpen(!open)}
                className={cn(
                    "flex min-h-10 w-full items-center justify-between rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background cursor-pointer hover:bg-accent/50 transition-colors",
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
                                className="gap-1"
                            >
                                {label}
                                <X
                                    className="h-3 w-3 cursor-pointer hover:text-destructive"
                                    onClick={(e) => handleRemove(value[index], e)}
                                />
                            </Badge>
                        ))
                    )}
                </div>
                <svg
                    className={cn(
                        "h-4 w-4 opacity-50 transition-transform",
                        open && "transform rotate-180"
                    )}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            {open && (
                <div className="absolute z-50 mt-2 w-full rounded-lg border bg-card shadow-xl max-h-60 overflow-auto">
                    <div className="p-1">
                        {options.map((option) => {
                            const isSelected = value.includes(option.value)
                            return (
                                <div
                                    key={option.value}
                                    onClick={() => handleToggle(option.value)}
                                    className={cn(
                                        "relative flex cursor-pointer select-none items-center rounded-md px-2 py-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground transition-colors",
                                        isSelected && "bg-accent"
                                    )}
                                >
                                    <div className={cn(
                                        "flex h-4 w-4 items-center justify-center rounded border mr-2",
                                        isSelected && "bg-primary border-primary"
                                    )}>
                                        {isSelected && <Check className="h-3 w-3 text-primary-foreground" />}
                                    </div>
                                    <span>{option.label}</span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
})
MultiSelect.displayName = "MultiSelect"

export { MultiSelect }
