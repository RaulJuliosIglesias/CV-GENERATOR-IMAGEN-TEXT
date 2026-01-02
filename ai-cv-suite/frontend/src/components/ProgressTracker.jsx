import { CheckCircle2, AlertCircle, Loader2, FileText, Image, Brain, Clock } from 'lucide-react';
import { Progress } from './ui/Progress';
import { Button } from './ui/Button';
import useGenerationStore from '../stores/useGenerationStore';
import { getPdfUrl } from '../lib/api';

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

function TaskCard({ task }) {
    const statusConfig = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
    const Icon = statusConfig.icon;

    const handleOpenPdf = () => {
        if (task.pdf_path) {
            const filename = task.pdf_path.split(/[\\/]/).pop();
            window.open(getPdfUrl(filename), '_blank');
        }
    };

    return (
        <div
            className={`relative rounded-xl border ${statusConfig.borderColor} ${statusConfig.bgColor} p-4 transition-all duration-300 ${statusConfig.animate ? 'animate-pulse-glow' : ''
                }`}
        >
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

            {/* Progress Bar */}
            <Progress value={task.progress} className="h-1.5 mb-3" />

            {/* Status Message */}
            <p className="text-xs text-muted-foreground truncate mb-2">{task.status_message}</p>

            {/* Role */}
            <p className="text-sm font-medium text-foreground/80 truncate">{task.role}</p>

            {/* Error Message */}
            {task.error_message && (
                <p className="text-xs text-red-400 mt-2 truncate">{task.error_message}</p>
            )}

            {/* Open PDF Button */}
            {task.status === 'complete' && task.pdf_path && (
                <Button
                    onClick={handleOpenPdf}
                    size="sm"
                    variant="outline"
                    className="w-full mt-3"
                >
                    <FileText className="w-4 h-4 mr-2" />
                    Open PDF
                </Button>
            )}
        </div>
    );
}

export default function ProgressTracker() {
    const { tasks, isGenerating, currentBatch } = useGenerationStore();

    const completedCount = tasks.filter((t) => t.status === 'complete').length;
    const totalCount = tasks.length;
    const overallProgress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

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
                            Batch #{currentBatch} • {completedCount} of {totalCount} complete
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
