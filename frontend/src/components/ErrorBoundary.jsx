import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from './ui/Button';

/**
 * ErrorBoundary - Captura errores de React y muestra UI amigable
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error,
            errorInfo
        });

        // Log to error tracking service (if available)
        if (window.errorTracker) {
            window.errorTracker.logError(error, errorInfo);
        }
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-background p-4">
                    <div className="max-w-2xl w-full bg-card border border-border rounded-lg p-6 space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                                <AlertTriangle className="w-6 h-6 text-red-500" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold">Something went wrong</h1>
                                <p className="text-sm text-muted-foreground">
                                    An unexpected error occurred. Don't worry, your data is safe.
                                </p>
                            </div>
                        </div>

                        {this.state.error && (
                            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                                <p className="text-sm font-mono text-destructive break-all">
                                    {this.state.error.toString()}
                                </p>
                                {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                                    <details className="mt-2">
                                        <summary className="text-xs text-muted-foreground cursor-pointer">
                                            Stack Trace
                                        </summary>
                                        <pre className="text-xs text-muted-foreground mt-2 overflow-auto max-h-48">
                                            {this.state.errorInfo.componentStack}
                                        </pre>
                                    </details>
                                )}
                            </div>
                        )}

                        <div className="flex items-center gap-2">
                            <Button onClick={this.handleReset} className="flex items-center gap-2">
                                <RefreshCw className="w-4 h-4" />
                                Try Again
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => window.location.href = '/'}
                                className="flex items-center gap-2"
                            >
                                <Home className="w-4 h-4" />
                                Go Home
                            </Button>
                        </div>

                        <p className="text-xs text-muted-foreground text-center">
                            If this problem persists, please refresh the page or contact support.
                        </p>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
