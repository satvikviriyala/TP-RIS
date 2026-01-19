import { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';

// types for API response
interface AnalysisResult {
    ofnr_d: {
        observation: string | null;
        feeling: string | null;
        need: string | null;
        request: string | null;
        confidence: {
            observation: number;
            feeling: number;
            need: number;
            request: number;
        };
    };
    trust_assessment: {
        trust_score: number;
        flags: string[];
    };
    decision: {
        action: string;
        rationale: string;
    };
    rewrite: {
        text: string | null;
        explanation: string | null;
    };
}

interface UseAnalysisProps {
    initialText?: string;
}

export type AnalysisStatus = 'idle' | 'waiting' | 'analyzing' | 'suggestion_available' | 'needs_clarification' | 'error';

export function useAnalysis({ initialText = '' }: UseAnalysisProps) {
    const [text, setText] = useState(initialText);
    const [status, setStatus] = useState<AnalysisStatus>('idle');
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [lastAnalyzedText, setLastAnalyzedText] = useState('');

    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const lastRequestTimeRef = useRef<number>(0);
    const abortControllerRef = useRef<AbortController | null>(null);

    const MIN_CHARS = 80;
    const RATE_LIMIT_MS = 2000;
    const DEBOUNCE_MS = 500;

    const analyze = useCallback(async (currentText: string) => {
        console.log('[useAnalysis] analyze called with text length:', currentText.length);

        // Basic validations
        if (currentText.length < MIN_CHARS) {
            setStatus('waiting');
            setResult(null);
            return;
        }

        if (currentText === lastAnalyzedText) {
            console.log('[useAnalysis] Text unchanged, skipping');
            return;
        }

        // Rate limiting check
        const now = Date.now();
        const timeSinceLastRequest = now - lastRequestTimeRef.current;

        if (timeSinceLastRequest < RATE_LIMIT_MS) {
            console.log('[useAnalysis] Rate limited, skipping');
            return;
        }

        // Cancel previous request if any
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();

        setStatus('analyzing');
        lastRequestTimeRef.current = Date.now();
        console.log('[useAnalysis] Sending request to backend...');

        try {
            const response = await axios.post('http://localhost:8000/analyze-feedback', {
                review_text: currentText,
            }, {
                signal: abortControllerRef.current.signal
            });

            console.log('[useAnalysis] Response received:', response.data);
            const data = response.data as AnalysisResult;
            setResult(data);
            setLastAnalyzedText(currentText);

            // Determine status based on decision - always show suggestion_available if we have a result
            if (data.decision.action === 'SUGGEST_CLARIFICATION') {
                setStatus('needs_clarification');
            } else if (data.decision.action === 'NO_OP') {
                // Still show the result for NO_OP so user sees the analysis
                setStatus('suggestion_available');
            } else {
                setStatus('suggestion_available');
            }

        } catch (error) {
            if (axios.isCancel(error)) {
                console.log('[useAnalysis] Request canceled');
            } else {
                console.error('[useAnalysis] Analysis error:', error);
                setStatus('error');
            }
        }
    }, [lastAnalyzedText]);

    // Debounce logic
    useEffect(() => {
        // If text is too short, reset state immediately
        if (text.length < MIN_CHARS) {
            setStatus('waiting');
            setResult(null);
            return;
        }

        // Clear existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        // Set new timeout
        timeoutRef.current = setTimeout(() => {
            analyze(text);
        }, DEBOUNCE_MS);

        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
        };
    }, [text, analyze]);

    const acceptSuggestion = () => {
        if (result?.rewrite?.text) {
            setText(result.rewrite.text);
            setResult(null);
            setStatus('idle');
            setLastAnalyzedText(result.rewrite.text);
        }
    };

    const ignoreSuggestion = () => {
        setResult(null);
        setStatus('idle');
    };

    return {
        text,
        setText,
        status,
        result,
        acceptSuggestion,
        ignoreSuggestion
    };
}
