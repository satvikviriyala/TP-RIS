interface SuggestionPanelProps {
    result: {
        decision: { action: string; rationale: string };
        rewrite: { text: string | null; explanation: string | null };
        trust_assessment: { trust_score: number; flags: string[] };
        ofnr_d: {
            observation: string | null;
            feeling: string | null;
            need: string | null;
            request: string | null;
        };
    };
    onAccept: () => void;
    onIgnore: () => void;
}

export function SuggestionPanel({ result, onAccept, onIgnore }: SuggestionPanelProps) {
    if (!result) return null;

    const { decision, rewrite } = result;

    const isRewrite = ['PARTIAL_REWRITE', 'FULL_REWRITE'].includes(decision.action);
    const isClarification = decision.action === 'SUGGEST_CLARIFICATION';
    const isFlag = decision.action === 'FLAG';

    // Get panel styling based on decision type
    const getPanelStyle = () => {
        if (isFlag) return { bg: '#fef2f2', border: '#fecaca' };
        if (isClarification) return { bg: '#fef3c7', border: '#fde68a' };
        if (isRewrite) return { bg: '#f3e8ff', border: '#e9d5ff' };
        return { bg: '#f0fdf4', border: '#bbf7d0' }; // NO_OP - green (good)
    };

    const panelStyle = getPanelStyle();

    return (
        <div style={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
            {/* Header */}
            <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                        padding: '4px 8px',
                        fontSize: '11px',
                        fontWeight: '600',
                        borderRadius: '4px',
                        backgroundColor: panelStyle.bg,
                        border: `1px solid ${panelStyle.border}`,
                        color: '#333'
                    }}>
                        {decision.action.replace('_', ' ')}
                    </span>
                </div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111', margin: 0 }}>
                    {isRewrite ? '✨ Suggestion Available' :
                        isClarification ? '❓ Clarification Needed' :
                            isFlag ? '⚠️ Flagged Content' :
                                '✓ Analysis Complete'}
                </h3>
                <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
                    {decision.rationale}
                </p>
            </div>

            {/* Rewrite suggestion */}
            {isRewrite && rewrite.text && (
                <div style={{
                    backgroundColor: '#f3e8ff',
                    padding: '16px',
                    borderRadius: '8px',
                    marginBottom: '16px',
                    border: '1px solid #e9d5ff'
                }}>
                    <p style={{ fontSize: '12px', color: '#7c3aed', marginBottom: '8px', fontWeight: '600' }}>
                        Suggested Rewrite:
                    </p>
                    <p style={{ color: '#333', margin: 0, whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                        {rewrite.text}
                    </p>
                </div>
            )}

            {/* Clarification message */}
            {isClarification && (
                <div style={{
                    backgroundColor: '#fef3c7',
                    padding: '16px',
                    borderRadius: '8px',
                    marginBottom: '16px',
                    border: '1px solid #fde68a'
                }}>
                    <p style={{ color: '#92400e', margin: 0, fontSize: '14px' }}>
                        💡 The feedback could be clearer. Consider specifying what exactly you'd like addressed.
                    </p>
                    {rewrite.text && (
                        <p style={{ color: '#333', margin: '12px 0 0 0', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                            {rewrite.text}
                        </p>
                    )}
                </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                    onClick={onIgnore}
                    style={{
                        padding: '8px 16px',
                        fontSize: '14px',
                        color: '#666',
                        backgroundColor: '#f3f4f6',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer'
                    }}
                >
                    Dismiss
                </button>

                {isRewrite && rewrite.text && (
                    <button
                        onClick={onAccept}
                        style={{
                            padding: '8px 16px',
                            fontSize: '14px',
                            color: 'white',
                            backgroundColor: '#7c3aed',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer'
                        }}
                    >
                        Accept Rewrite
                    </button>
                )}
            </div>
        </div>
    );
}
