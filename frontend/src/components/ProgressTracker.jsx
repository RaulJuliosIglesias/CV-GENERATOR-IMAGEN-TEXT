import { useState, forwardRef, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, Loader2, FileText, Image, Brain, Clock, Eye, Download, Trash2 } from 'lucide-react';
import { Progress } from './ui/Progress';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { getPdfUrl, getHtmlUrl } from '../lib/api';

// Status config with color progression: gray -> yellow -> orange -> green
const STATUS_CONFIG = {
    pending: {
        icon: Clock,
        color: 'text-gray-400',
        bgColor: 'bg-gray-500/10',
        borderColor: 'border-gray-500/30',
        progressColor: 'bg-gray-400',
        label: 'Pending',
    },
    generating_content: {
        icon: Brain,
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-500/10',
        borderColor: 'border-yellow-500/30',
        progressColor: 'bg-yellow-400',
        label: 'Generating Content',
        animate: true,
    },
    generating_image: {
        icon: Image,
        color: 'text-orange-400',
        bgColor: 'bg-orange-500/10',
        borderColor: 'border-orange-500/30',
        progressColor: 'bg-orange-400',
        label: 'Generating Image',
        animate: true,
    },
    rendering_pdf: {
        icon: FileText,
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/10',
        borderColor: 'border-blue-500/30',
        progressColor: 'bg-blue-400',
        label: 'Rendering PDF',
        animate: true,
    },
    complete: {
        icon: CheckCircle2,
        color: 'text-green-400',
        bgColor: 'bg-green-500/10',
        borderColor: 'border-green-500/30',
        progressColor: 'bg-green-500',
        label: 'Complete',
    },
    error: {
        icon: AlertCircle,
        color: 'text-red-400',
        bgColor: 'bg-red-500/10',
        borderColor: 'border-red-500/30',
        progressColor: 'bg-red-500',
        label: 'Error',
    },
};

// Subtask status icons
const SUBTASK_CONFIG = {
    pending: { icon: Clock, color: 'text-gray-500' },
    running: { icon: Loader2, color: 'text-blue-500', animate: true },
    complete: { icon: CheckCircle2, color: 'text-green-500' },
    error: { icon: AlertCircle, color: 'text-red-500' }
};

// Simple, subtle card animation - just fade and slide
const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (index) => ({
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.3,
            delay: index * 0.05,
            ease: "easeOut"
        }
    }),
    exit: {
        opacity: 0,
        y: -10,
        transition: { duration: 0.2 }
    }
};

// TaskCard with forwardRef to fix React warning
const TaskCard = memo(forwardRef(function TaskCard({ task, index }, ref) {
    const [showFullError, setShowFullError] = useState(false);
    const statusConfig = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
    const Icon = statusConfig.icon;
    const isComplete = task.status === 'complete';
    const isError = task.status === 'error';

    const handleOpenCv = () => {
        const path = task.html_path || task.pdf_path;
        if (path) {
            const filename = path.split(/[\\/]/).pop();
            window.open(getHtmlUrl(filename), '_blank');
        }
    };

    const handleDownloadPdf = () => {
        const path = task.pdf_path || task.html_path;
        if (path) {
            const filename = path.split(/[\\/]/).pop();
            window.open(getPdfUrl(filename), '_blank');
        }
    };

    return (
        <motion.div
            ref={ref}
            custom={index}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            layout
            className={`
                relative rounded-xl border p-4 
                transition-all duration-500 ease-out
                ${statusConfig.borderColor} 
                ${statusConfig.bgColor}
                hover:scale-[1.02] hover:shadow-lg
                group
            `}
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    {statusConfig.animate ? (
                        <Loader2 className={`w-5 h-5 ${statusConfig.color} animate-spin`} />
                    ) : (
                        <Icon className={`w-5 h-5 ${statusConfig.color} transition-colors duration-300`} />
                    )}
                    <span className="text-xs font-medium text-muted-foreground">CV #{task.id}</span>
                </div>
                <span className={`text-xs font-semibold ${statusConfig.color} px-2 py-0.5 rounded-full ${statusConfig.bgColor} transition-colors duration-300`}>
                    {statusConfig.label}
                </span>
            </div>

            {/* Role */}
            <p className="text-sm font-bold text-foreground truncate mb-2">{task.role}</p>

            {/* Status Message */}
            <p className="text-xs text-muted-foreground truncate mb-3 min-h-[1.5em]">{task.message}</p>

            {/* Simple Progress Bar - solid color that transitions with status */}
            <div className="relative h-2 bg-secondary/50 rounded-full overflow-hidden mb-4">
                <div
                    className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out ${statusConfig.progressColor}`}
                    style={{ width: `${task.progress}%` }}
                />
            </div>

            {/* Subtasks List */}
            <div className="space-y-1.5 bg-black/10 rounded-lg p-2.5 mb-3">
                {task.subtasks?.map((subtask) => {
                    const config = SUBTASK_CONFIG[subtask.status] || SUBTASK_CONFIG.pending;
                    const SubIcon = config.icon;

                    return (
                        <div key={subtask.id} className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                                <SubIcon className={`w-3.5 h-3.5 ${config.color} ${config.animate ? 'animate-spin' : ''} transition-colors duration-300`} />
                                <span className={`transition-colors duration-200 ${subtask.status === 'pending' ? 'text-muted-foreground' : 'text-foreground'
                                    }`}>
                                    {subtask.name}
                                </span>
                            </div>
                            {subtask.status === 'running' && (
                                <span className="text-[10px] text-blue-400">Processing...</span>
                            )}
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
            {isComplete && (
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
                        <Download className="w-4 h-4 mr-1" />
                        PDF
                    </Button>
                </div>
            )}

            {/* Delete Button for Failed Tasks */}
            {isError && (
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
                        className="p-2 text-red-500 hover:bg-red-500/20 rounded-full transition-colors"
                        title="Delete failed task"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            )}
        </motion.div>
    );
}));

export default function ProgressTracker() {
    const { allTasks, isGenerating, activeBatchIds, completedBatchIds } = useGenerationStore();

    const tasks = allTasks;
    const completedCount = tasks.filter((t) => t.status === 'complete').length;
    const totalCount = tasks.length;

    // Calculate progress
    let subtaskProgressSum = 0;
    let subtaskTotal = 0;

    tasks.forEach(task => {
        if (task.subtasks && task.subtasks.length > 0) {
            task.subtasks.forEach(subtask => {
                subtaskTotal += 100;
                subtaskProgressSum += (subtask.progress || 0);
            });
        } else {
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

                {/* Simple overall progress bar */}
                <Progress value={overallProgress} className="h-2" />
            </div>

            {/* Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <AnimatePresence mode="popLayout">
                    {tasks.map((task, index) => (
                        <TaskCard key={task.id} task={task} index={index} />
                    ))}
                </AnimatePresence>
            </div>

            {/* Completion Summary */}
            {!isGenerating && completedCount === totalCount && totalCount > 0 && (
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
