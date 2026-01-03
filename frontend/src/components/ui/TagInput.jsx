import { useState } from 'react';
import { X, Plus, Check } from 'lucide-react';
import * as PopoverPrimitive from "@radix-ui/react-popover"
import { cn } from '../../lib/utils';
import { Badge } from './Badge';
import { Input } from './Input';

// Default role suggestions (fallback if not provided from API)
const DEFAULT_ROLE_SUGGESTIONS = [
    'Software Developer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
    'DevOps Engineer', 'Data Scientist', 'Machine Learning Engineer', 'Data Engineer',
    'Product Manager', 'Project Manager', 'Scrum Master', 'Agile Coach',
    'UI/UX Designer', 'Graphic Designer', 'Product Designer', 'UX Researcher',
    'QA Engineer', 'Test Engineer', 'QA Automation Engineer',
    'Security Engineer', 'Cybersecurity Analyst', 'Penetration Tester',
    'Cloud Architect', 'Solutions Architect', 'Enterprise Architect',
    'Mobile Developer', 'iOS Developer', 'Android Developer', 'React Native Developer',
    'Database Administrator', 'DBA', 'Data Analyst', 'Business Analyst',
    'Marketing Manager', 'Digital Marketing Specialist', 'SEO Specialist',
    'Sales Engineer', 'Account Manager', 'Customer Success Manager',
    'HR Manager', 'Recruiter', 'Talent Acquisition Specialist',
    'Financial Analyst', 'Accountant', 'Controller', 'CFO',
];

export function TagInput({ value = [], onChange, placeholder = "Add roles...", suggestions }) {
    const [inputValue, setInputValue] = useState('');
    const [open, setOpen] = useState(false);

    // Use provided suggestions or fallback to defaults
    const roleSuggestions = suggestions || DEFAULT_ROLE_SUGGESTIONS;

    const filteredSuggestions = roleSuggestions.filter(role =>
        role.toLowerCase().includes(inputValue.toLowerCase()) &&
        !value.includes(role)
    ).slice(0, 8);

    const addRole = (role) => {
        if (role.trim() && !value.includes(role.trim())) {
            onChange([...value, role.trim()]);
            setInputValue('');
            setOpen(false);
        }
    };

    const removeRole = (index) => {
        onChange(value.filter((_, i) => i !== index));
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addRole(inputValue);
        }
    };

    const handleInputChange = (e) => {
        const val = e.target.value;
        setInputValue(val);
        if (val.length > 0) {
            setOpen(true);
        } else {
            setOpen(false); // Can keep open if you want default suggestions
        }
    };

    return (
        <div className="relative w-full space-y-2">
            {/* Tags Display */}
            <div className="flex flex-wrap gap-2">
                {value.map((role, index) => (
                    <Badge
                        key={index}
                        variant="secondary"
                        className="gap-1 pl-3 pr-1 py-1 bg-secondary/80 backdrop-blur-md"
                    >
                        <span className="text-xs">{role}</span>
                        <button
                            type="button"
                            onClick={() => removeRole(index)}
                            className="ml-1 rounded-full hover:bg-destructive/20 p-0.5 transition-colors"
                        >
                            <X className="h-3 w-3" />
                        </button>
                    </Badge>
                ))}
            </div>

            {/* Input with Popover Suggestions */}
            <PopoverPrimitive.Root open={open && filteredSuggestions.length > 0} onOpenChange={setOpen}>
                <PopoverPrimitive.Anchor asChild>
                    <div className="relative">
                        <Input
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            onFocus={() => inputValue && setOpen(true)}
                            onBlur={() => {
                                // Delay closing to allow clicking suggestions
                                setTimeout(() => setOpen(false), 200)
                            }}
                            placeholder={placeholder}
                            className="pr-10 bg-background/50 backdrop-blur-sm border-input/50 focus:ring-primary/50"
                        />
                        <button
                            type="button"
                            onClick={() => addRole(inputValue)}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-accent rounded-md transition-colors text-muted-foreground hover:text-foreground"
                        >
                            <Plus className="h-4 w-4" />
                        </button>
                    </div>
                </PopoverPrimitive.Anchor>

                <PopoverPrimitive.Portal>
                    <PopoverPrimitive.Content
                        className="z-50 w-[var(--radix-popover-anchor-width)] rounded-xl border border-white/10 bg-card/95 p-1 text-card-foreground shadow-2xl backdrop-blur-xl outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
                        align="start"
                        sideOffset={5}
                        onOpenAutoFocus={(e) => e.preventDefault()}
                    >
                        <div className="max-h-60 overflow-y-auto p-1 custom-scrollbar">
                            {filteredSuggestions.map((role, index) => (
                                <div
                                    key={index}
                                    onMouseDown={(e) => {
                                        // Use onMouseDown instead of onClick to fire before blur
                                        e.preventDefault();
                                        addRole(role);
                                    }}
                                    className="px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors flex items-center justify-between group"
                                >
                                    <span>{role}</span>
                                    <Plus className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground" />
                                </div>
                            ))}
                        </div>
                    </PopoverPrimitive.Content>
                </PopoverPrimitive.Portal>
            </PopoverPrimitive.Root>

            {/* Custom hint */}
            {inputValue && !filteredSuggestions.some(s => s.toLowerCase() === inputValue.toLowerCase()) && !open && (
                <p className="text-[10px] text-muted-foreground pl-1 animate-pulse">
                    Press Enter to add "{inputValue}"
                </p>
            )}
        </div>
    );
}
