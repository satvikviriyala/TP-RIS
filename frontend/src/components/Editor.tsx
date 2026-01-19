import { useState } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { StatusIndicator } from './StatusIndicator';
import { SuggestionPanel } from './SuggestionPanel';
import axios from 'axios';

export function Editor() {
    const { text, setText, status, result, acceptSuggestion, ignoreSuggestion } = useAnalysis({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Determine if submit is allowed - only when decision is NO_OP (feedback passed check)
    const isSubmitEnabled = result?.decision?.action === 'NO_OP' && !isSubmitting;

    const handleSubmit = async () => {
        if (!isSubmitEnabled || !result) return;

        setIsSubmitting(true);

        try {
            await axios.post('http://localhost:8000/submit-feedback', {
                feedback_text: text,
                observation: result.ofnr_d?.observation,
                feeling: result.ofnr_d?.feeling,
                need: result.ofnr_d?.need,
                request: result.ofnr_d?.request,
                trust_score: result.trust_assessment?.trust_score
            });

            alert('Feedback submitted successfully! Saved to submitted_feedback.csv');
            setText('');
        } catch (error) {
            console.error('Submit error:', error);
            alert('Failed to submit feedback. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{
            display: 'flex',
            gap: '48px',
            alignItems: 'flex-start'
        }}>
            {/* Left side - Feedback input (fills available space, aligned with header) */}
            <div style={{
                flex: '1 1 0',
                minWidth: '400px',
                position: 'relative'
            }}>
                <div style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    zIndex: 10
                }}>
                    <StatusIndicator status={status} />
                </div>
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Type your feedback here... (min 80 chars for analysis)"
                    style={{
                        width: '100%',
                        height: '500px',
                        padding: '32px',
                        paddingTop: '48px',
                        fontSize: '18px',
                        lineHeight: '1.7',
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '16px',
                        resize: 'none',
                        outline: 'none',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        fontFamily: 'inherit',
                        boxSizing: 'border-box'
                    }}
                    spellCheck={false}
                />

                {/* Bottom bar with char count and submit button */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginTop: '16px'
                }}>
                    <div style={{
                        fontSize: '13px',
                        color: text.length >= 80 ? '#22c55e' : '#999',
                        fontFamily: 'monospace',
                        fontWeight: '500'
                    }}>
                        {text.length} / 80 chars
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={!isSubmitEnabled}
                        style={{
                            padding: '12px 32px',
                            fontSize: '15px',
                            fontWeight: '600',
                            color: isSubmitEnabled ? 'white' : '#9ca3af',
                            backgroundColor: isSubmitEnabled ? '#22c55e' : '#e5e7eb',
                            border: 'none',
                            borderRadius: '10px',
                            cursor: isSubmitEnabled ? 'pointer' : 'not-allowed',
                            transition: 'all 0.2s ease',
                            boxShadow: isSubmitEnabled ? '0 2px 8px rgba(34, 197, 94, 0.3)' : 'none'
                        }}
                    >
                        {isSubmitting ? 'Submitting...' : isSubmitEnabled ? '✓ Submit Feedback' : 'Submit Feedback'}
                    </button>
                </div>
            </div>

            {/* Right side - Suggestions (smaller fixed width) */}
            <div style={{
                flex: '0 0 380px',
                position: 'sticky',
                top: '32px'
            }}>
                {result ? (
                    <SuggestionPanel
                        result={result}
                        onAccept={acceptSuggestion}
                        onIgnore={ignoreSuggestion}
                    />
                ) : (
                    <div style={{
                        padding: '32px',
                        backgroundColor: '#f9fafb',
                        borderRadius: '16px',
                        border: '1px dashed #e5e7eb',
                        textAlign: 'center',
                        color: '#9ca3af'
                    }}>
                        <p style={{ margin: 0, fontSize: '14px' }}>
                            {text.length < 80
                                ? `Type at least ${80 - text.length} more characters to trigger analysis...`
                                : 'Waiting for analysis...'}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
