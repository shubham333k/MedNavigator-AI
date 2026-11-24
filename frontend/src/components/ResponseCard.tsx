'use client';

import { useState } from 'react';
import type { QueryResponse, Citation } from '@/types';
import CitationList from '@/components/CitationList';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ResponseCardProps {
  result: QueryResponse;
}

export default function ResponseCard({ result }: ResponseCardProps) {
  const [showCitations, setShowCitations] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(result.response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const confidencePercent = result.confidence_score
    ? Math.round(result.confidence_score * 100)
    : 0;

  const confidenceColor =
    confidencePercent >= 70 ? 'var(--color-success)' :
    confidencePercent >= 40 ? 'var(--color-warning)' :
    'var(--color-danger)';

  return (
    <div className="card animate-fade-in" style={{ overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: 'var(--space-4) var(--space-6)',
        borderBottom: '1px solid var(--color-border)',
        background: 'rgba(14,165,233,0.03)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <div style={{
            width: 32, height: 32,
            background: 'var(--gradient-brand)',
            borderRadius: 'var(--radius-md)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1rem',
          }}>🤖</div>
          <div>
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 2 }}>
              Evidence-Based Response
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              {result.processing_time_ms.toFixed(0)}ms · {result.citations.length} source{result.citations.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {/* Confidence Score */}
          {result.confidence_score !== undefined && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Confidence</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 60, height: 4, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                  <div style={{ width: `${confidencePercent}%`, height: '100%', background: confidenceColor, borderRadius: 'var(--radius-full)', transition: 'width 1s ease' }} />
                </div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: confidenceColor }}>{confidencePercent}%</span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
            <button className="btn btn-ghost btn-sm" onClick={handleCopy} title="Copy response">
              {copied ? '✅' : '📋'}
            </button>
            {result.citations.length > 0 && (
              <button
                className={`btn btn-sm ${showCitations ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setShowCitations(!showCitations)}
              >
                📚 {showCitations ? 'Hide' : 'Show'} Citations
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Query echo */}
      <div style={{ padding: 'var(--space-4) var(--space-6)', borderBottom: '1px solid var(--color-border)', background: 'rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-start' }}>
          <div style={{
            width: 28, height: 28, borderRadius: '50%',
            background: 'var(--color-bg-hover)',
            border: '1px solid var(--color-border)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.75rem', flexShrink: 0,
          }}>👨‍⚕️</div>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', fontStyle: 'italic', paddingTop: 4 }}>
            &ldquo;{result.query}&rdquo;
          </p>
        </div>
      </div>

      {/* Response Content */}
      <div style={{ padding: 'var(--space-6)' }}>
        <div className="prose">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {result.response}
          </ReactMarkdown>
        </div>
      </div>

      {/* Citations */}
      {showCitations && result.citations.length > 0 && (
        <div style={{ borderTop: '1px solid var(--color-border)' }}>
          <CitationList citations={result.citations} />
        </div>
      )}

      {/* Disclaimer */}
      <div style={{
        padding: 'var(--space-4) var(--space-6)',
        borderTop: '1px solid var(--color-border)',
        background: 'rgba(245,158,11,0.03)',
        display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)',
      }}>
        <span style={{ fontSize: '1rem', flexShrink: 0 }}>⚠️</span>
        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
          This information is provided for clinical decision support only. It does not replace professional medical judgment.
          Always verify recommendations against current institutional protocols and the individual patient&apos;s clinical context.
        </p>
      </div>
    </div>
  );
}
