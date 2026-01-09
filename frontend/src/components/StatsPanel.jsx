import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Clock, CheckCircle2, XCircle, Award, Calendar } from 'lucide-react';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { getStatsSummary } from '../lib/storage';

/**
 * StatsPanel - Panel de estadísticas de generación
 */
export default function StatsPanel() {
    const [stats, setStats] = useState(null);
    // Load collapsed state from localStorage
    const [isExpanded, setIsExpanded] = useState(() => {
        const saved = localStorage.getItem('stats-panel-expanded');
        return saved ? JSON.parse(saved) : false; // Collapsed by default
    });
    const loadStatsAction = useGenerationStore(s => s.loadStats);
    
    // Save expanded state to localStorage
    useEffect(() => {
        localStorage.setItem('stats-panel-expanded', JSON.stringify(isExpanded));
    }, [isExpanded]);

    useEffect(() => {
        // Load stats on mount using getStatsSummary to ensure calculated fields exist
        const loadedStats = getStatsSummary();
        setStats(loadedStats);
        
        // Also update store
        if (loadStatsAction) {
            loadStatsAction();
        }
    }, [loadStatsAction]);

    // Refresh stats periodically
    useEffect(() => {
        const interval = setInterval(() => {
            const updatedStats = getStatsSummary();
            setStats(updatedStats);
        }, 5000); // Every 5 seconds

        return () => clearInterval(interval);
    }, []);

    if (!stats) {
        return null;
    }

    const {
        totalGenerations = 0,
        successful = 0,
        failed = 0,
        averageTime = 0,
        successRate = 0,
        byRole = {}
    } = stats || {};
    
    // Ensure numeric values for display
    const safeAverageTime = typeof averageTime === 'number' ? averageTime : 0;
    const safeSuccessRate = typeof successRate === 'number' ? successRate : 0;

    const topRoles = Object.entries(byRole)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5);

    return (
        <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
            {/* Header */}
            <div
                className="flex items-center justify-between p-3 cursor-pointer hover:bg-card/70 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    <span className="text-sm font-semibold">Statistics</span>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-xs text-muted-foreground">
                        {totalGenerations} total
                    </div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            setIsExpanded(!isExpanded);
                        }}
                        className="h-6 w-6 p-0"
                    >
                        {isExpanded ? '−' : '+'}
                    </Button>
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="px-3 pb-3 space-y-3 border-t border-border/50 pt-3">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-2 gap-2">
                        <div className="p-2 bg-success/10 rounded border border-success/20">
                            <div className="flex items-center gap-1 mb-1">
                                <CheckCircle2 className="w-3 h-3 text-success" />
                                <span className="text-xs text-muted-foreground">Success</span>
                            </div>
                            <p className="text-lg font-bold text-success">{successful}</p>
                            <p className="text-[10px] text-muted-foreground">
                                {safeSuccessRate.toFixed(1)}% rate
                            </p>
                        </div>
                        <div className="p-2 bg-destructive/10 rounded border border-destructive/20">
                            <div className="flex items-center gap-1 mb-1">
                                <XCircle className="w-3 h-3 text-destructive" />
                                <span className="text-xs text-muted-foreground">Failed</span>
                            </div>
                            <p className="text-lg font-bold text-destructive">{failed}</p>
                            <p className="text-[10px] text-muted-foreground">
                                {(100 - safeSuccessRate).toFixed(1)}% rate
                            </p>
                        </div>
                        <div className="p-2 bg-primary/10 rounded border border-primary/20">
                            <div className="flex items-center gap-1 mb-1">
                                <Clock className="w-3 h-3 text-primary" />
                                <span className="text-xs text-muted-foreground">Avg Time</span>
                            </div>
                            <p className="text-lg font-bold text-primary">
                                {safeAverageTime.toFixed(1)}s
                            </p>
                        </div>
                        <div className="p-2 bg-purple-500/10 rounded border border-purple-500/20">
                            <div className="flex items-center gap-1 mb-1">
                                <TrendingUp className="w-3 h-3 text-purple-400" />
                                <span className="text-xs text-muted-foreground">Total</span>
                            </div>
                            <p className="text-lg font-bold text-purple-400">{totalGenerations}</p>
                        </div>
                    </div>

                    {/* Top Roles */}
                    {topRoles.length > 0 && (
                        <div>
                            <div className="flex items-center gap-1 mb-2">
                                <Award className="w-3 h-3 text-muted-foreground" />
                                <span className="text-xs font-semibold text-muted-foreground">
                                    Top Roles
                                </span>
                            </div>
                            <div className="space-y-1">
                                {topRoles.map(([role, count]) => (
                                    <div
                                        key={role}
                                        className="flex items-center justify-between text-xs p-1.5 bg-background/50 rounded"
                                    >
                                        <span className="truncate flex-1">{role}</span>
                                        <span className="text-muted-foreground ml-2">
                                            {count}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
