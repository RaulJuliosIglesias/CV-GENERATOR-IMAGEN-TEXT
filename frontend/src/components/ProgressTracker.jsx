import { useState } from 'react';
import { CheckCircle2, AlertCircle, Loader2, FileText, Image, Brain, Clock, Eye, Download, Trash2 } from 'lucide-react';
import { Progress } from './ui/Progress';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { getPdfUrl, getHtmlUrl } from '../lib/api';

const STATUS_CONFIG = {
    pending: {
        icon: Clock,
        color: 'text-gray-400',
        bgColor: 'bg-gray-500/10',
        borderColor: 'border-gray-500/30',
        label: 'Pending',
    },
    generating_content: {
        icon: Brain,
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-500/10',
        borderColor: 'border-yellow-500/30',
        label: 'Generating Content',
        animate: true,
    },
    generating_image: {
        icon: Image,
        color: 'text-orange-400',
        bgColor: 'bg-orange-500/10',
        borderColor: 'border-orange-500/30',
        label: 'Generating Image',
        animate: true,
    },
    rendering_pdf: {
        icon: FileText,
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/10',
        borderColor: 'border-blue-500/30',
        label: 'Rendering PDF',
        animate: true,
    },
    complete: {
        icon: CheckCircle2,
        color: 'text-green-400',
        bgColor: 'bg-green-500/10',
        borderColor: 'border-green-500/30',
        label: 'Complete',
    },
    error: {
        icon: AlertCircle,
        color: 'text-red-400',
        bgColor: 'bg-red-500/10',
        borderColor: 'border-red-500/30',
        label: 'Error',
    },
};

// Subtask status icons configuration
const SUBTASK_CONFIG = {
    pending: { icon: Clock, color: 'text-gray-500' },
    running: { icon: Loader2, color: 'text-blue-500', animate: true },
    complete: { icon: CheckCircle2, color: 'text-green-500' },
    error: { icon: AlertCircle, color: 'text-red-500' }
};

function TaskCard({ task }) {
    const [showFullError, setShowFullError] = useState(false);
    const statusConfig = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
    const Icon = statusConfig.icon;

    const handleOpenCv = () => {
        const path = task.html_path || task.pdf_path;
        if (path) {
            const filename = path.split(/[\\/]/).pop();
            // Open HTML in new tab
            window.open(getHtmlUrl(filename), '_blank');
        }
    };

    const handleDownloadPdf = () => {
        const path = task.pdf_path || task.html_path;
        if (path) {
            const filename = path.split(/[\\/]/).pop();
            // Open PDF directly (browser will handle download/preview)
            window.open(getPdfUrl(filename), '_blank');
        }
    };

    return (
        <div className={`relative rounded-xl border ${statusConfig.borderColor} ${statusConfig.bgColor} p-4 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/5 group`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    {statusConfig.animate ? (
                        <Loader2 className={`w-5 h-5 ${statusConfig.color} animate-spin`} />
                    ) : (
                        <Icon className={`w-5 h-5 ${statusConfig.color}`} />
                    )}
                    <span className="text-xs font-medium text-muted-foreground">CV #{task.id}</span>
                </div>
                <span className={`text-xs font-medium ${statusConfig.color}`}>{statusConfig.label}</span>
            </div>

            {/* Role */}
            <p className="text-sm font-bold text-foreground truncate mb-3">{task.role}</p>

            {/* Status Message */}
            <p className="text-xs text-muted-foreground truncate mb-3 min-h-[1.5em]">{task.message}</p>

            {/* Progress Bar */}
            <Progress value={task.progress} className="h-1.5 mb-4" />

            {/* Subtasks List */}
            <div className="space-y-2 bg-black/5 rounded-lg p-2 mb-3">
                {task.subtasks?.map((subtask) => {
                    const config = SUBTASK_CONFIG[subtask.status] || SUBTASK_CONFIG.pending;
                    const SubIcon = config.icon;

                    return (
                        <div key={subtask.id} className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                                <SubIcon className={`w-3.5 h-3.5 ${config.color} ${config.animate ? 'animate-spin' : ''}`} />
                                <span className={subtask.status === 'pending' ? 'text-muted-foreground' : 'text-foreground'}>
                                    {subtask.name}
                                </span>
                            </div>
                            {subtask.status === 'running' && <span className="text-[10px] text-blue-500">Processing...</span>}
                        </div>
                    );
                })}
            </div>

            {/* Error Message - Expandable */}
            {task.error && (
                <div className="mt-2">
                    <button
                        onClick={() => setShowFullError(!showFullError)}
                        className="flex items-center gap-2 text-xs text-red-400 hover:text-red-300 transition-colors w-full"
                    >
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        <span className={showFullError ? '' : 'truncate'}>{showFullError ? 'Hide Error' : 'View Full Error'}</span>
                        <Eye className="w-3 h-3 ml-auto flex-shrink-0" />
                    </button>
                    {showFullError && (
                        <div className="mt-2 p-3 bg-red-950/50 border border-red-500/30 rounded-lg overflow-auto max-h-40">
                            <pre className="text-xs text-red-300 whitespace-pre-wrap break-words font-mono">
                                {task.error}
                            </pre>
                        </div>
                    )}
                </div>
            )}

            {/* Action Buttons */}
            {task.status === 'complete' && (
                <div className="flex gap-2 mt-3">
                    <Button
                        onClick={handleOpenCv}
                        size="sm"
                        variant="default"
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                    >
                        <FileText className="w-4 h-4 mr-1" />
                        View HTML
                    </Button>
                    <Button
                        onClick={handleDownloadPdf}
                        size="sm"
                        variant="outline"
                        className="flex-1 border-green-500/50 text-green-400 hover:bg-green-500/10"
                    >
                        <Eye className="w-4 h-4 mr-1" />
                        View PDF
                    </Button>
                </div>
            )}

            {/* Delete Button for Failed Tasks */}
            {task.status === 'error' && (
                <div className="flex justify-end mt-3">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            if (confirm('Delete this failed task?')) {
                                import('../lib/api').then(api => {
                                    api.deleteTask(task.id).catch(err => console.error(err));
                                });
                            }
                        }}
                        className="p-2 text-red-500 hover:bg-red-500/10 rounded-full transition-colors"
                        title="Delete failed task"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            )}
        </div>
    );
}

export default function ProgressTracker() {
    const { allTasks, isGenerating, activeBatchIds, completedBatchIds } = useGenerationStore();

    // Use allTasks for aggregated view
    const tasks = allTasks;
    const completedCount = tasks.filter((t) => t.status === 'complete').length;
    const totalCount = tasks.length;

    // Calculate REAL progress based on subtasks
    // Each task has 5 subtasks (Profile, CV Content, Image, HTML, PDF)
    // We calculate the sum of all subtask progress / total possible
    let subtaskProgressSum = 0;
    let subtaskTotal = 0;

    tasks.forEach(task => {
        if (task.subtasks && task.subtasks.length > 0) {
            task.subtasks.forEach(subtask => {
                subtaskTotal += 100; // Each subtask can be 0-100
                subtaskProgressSum += (subtask.progress || 0);
            });
        } else {
            // Fallback: use task.progress directly
            subtaskTotal += 100;
            subtaskProgressSum += (task.progress || 0);
        }
    });

    const overallProgress = subtaskTotal > 0 ? Math.round((subtaskProgressSum / subtaskTotal) * 100) : 0;

    if (tasks.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center max-w-md p-8">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mx-auto mb-6">
                        <FileText className="w-10 h-10 text-blue-400" />
                    </div>
                    <h2 className="text-2xl font-bold gradient-text mb-3">Ready to Generate</h2>
                    <p className="text-muted-foreground">
                        Configure your batch settings in the sidebar and click "Generate Batch" to start creating professional CVs.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-6">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-bold text-foreground">Generation Progress</h2>
                        <p className="text-sm text-muted-foreground">
                            {activeBatchIds.length} Active Batch(es) • {completedCount} of {totalCount} complete
                        </p>
                    </div>
                    <div className="text-right">
                        <span className="text-3xl font-bold gradient-text">{overallProgress}%</span>
                    </div>
                </div>
                <Progress value={overallProgress} className="h-2" />
            </div>

            {/* Task Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {tasks.map((task) => (
                    <TaskCard key={task.id} task={task} />
                ))}
            </div>

            {/* Status Summary */}
            {!isGenerating && completedCount === totalCount && (
                <div className="mt-8 p-6 rounded-xl bg-green-500/10 border border-green-500/30 text-center">
                    <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-3" />
                    <h3 className="text-lg font-bold text-green-400 mb-1">All CVs Generated!</h3>
                    <p className="text-sm text-muted-foreground">
                        {totalCount} professional résumés have been created and saved.
                    </p>
                </div>
            )}
        </div>
    );
}
