import type { ComponentProps } from 'react';
import type { AnalysisStatus } from '../hooks/useAnalysis';

interface StatusIndicatorProps extends ComponentProps<'div'> {
    status: AnalysisStatus;
}

export function StatusIndicator({ status, className, ...props }: StatusIndicatorProps) {
    const config: Record<AnalysisStatus, { text: string; color: string }> = {
        idle: { text: '', color: 'text-gray-400' },
        waiting: { text: 'Keep typing...', color: 'text-gray-400' },
        analyzing: { text: 'Analyzing...', color: 'text-blue-500' },
        suggestion_available: { text: 'Suggestion available', color: 'text-purple-500' },
        needs_clarification: { text: 'Needs clarification', color: 'text-amber-500' },
        error: { text: 'Error', color: 'text-red-500' },
    };

    const current = config[status];

    return (
        <div className={`flex items-center gap-2 text-sm font-medium ${current.color} ${className || ''}`} {...props}>
            {status === 'analyzing' && (
                <span className="inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></span>
            )}
            <span>{current.text}</span>
        </div>
    );
}
