import { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from './Badge';
import { Input } from './Input';

// Common role suggestions
const ROLE_SUGGESTIONS = [
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

export function TagInput({ value = [], onChange, placeholder = "Add roles..." }) {
    const [inputValue, setInputValue] = useState('');
    const [showSuggestions, setShowSuggestions] = useState(false);

    const filteredSuggestions = ROLE_SUGGESTIONS.filter(role =>
        role.toLowerCase().includes(inputValue.toLowerCase()) &&
        !value.includes(role)
    ).slice(0, 8);

    const addRole = (role) => {
        if (role.trim() && !value.includes(role.trim())) {
            onChange([...value, role.trim()]);
            setInputValue('');
            setShowSuggestions(false);
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

    return (
        <div className="relative w-full">
            {/* Tags Display */}
            <div className="flex flex-wrap gap-2 mb-2">
                {value.map((role, index) => (
                    <Badge
                        key={index}
                        variant="secondary"
                        className="gap-1 pl-3 pr-1 py-1"
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

            {/* Input */}
            <div className="relative">
                <Input
                    value={inputValue}
                    onChange={(e) => {
                        setInputValue(e.target.value);
                        setShowSuggestions(true);
                    }}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder={placeholder}
                    className="pr-10"
                />
                <button
                    type="button"
                    onClick={() => addRole(inputValue)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-accent rounded-md transition-colors"
                >
                    <Plus className="h-4 w-4" />
                </button>
            </div>

            {/* Suggestions Dropdown */}
            {showSuggestions && inputValue && filteredSuggestions.length > 0 && (
                <div className="absolute z-50 mt-1 w-full rounded-lg border bg-card shadow-xl max-h-60 overflow-auto">
                    <div className="p-1">
                        {filteredSuggestions.map((role, index) => (
                            <div
                                key={index}
                                onClick={() => addRole(role)}
                                className="px-3 py-2 text-sm rounded-md cursor-pointer hover:bg-accent transition-colors"
                            >
                                {role}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Add custom hint */}
            {inputValue && !filteredSuggestions.some(s => s.toLowerCase() === inputValue.toLowerCase()) && (
                <p className="text-xs text-muted-foreground mt-1">
                    Press Enter to add "{inputValue}" as custom role
                </p>
            )}
        </div>
    );
}
