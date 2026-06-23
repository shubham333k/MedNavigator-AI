'use client';

import { useState } from 'react';
import type { Citation } from '@/types';

interface CitationListProps {
  citations: Citation[];
}

const SOURCE_TYPE_ICONS: Record<string, string> = {
  pubmed: '🔬',
  guideline: '📋',
  drug_reference: '💊',
  clinical_reference: '🏥',
  pdf: '📄',
  csv: '📊',
  json: '📦',
  text: '📝',
  default: '📚',
};

const SOURCE_TYPE_COLORS: Record<string, string> = {
  pubmed: 'var(--color-info)',
  guideline: 'var(--color-success)',
  drug_reference: 'var(--color-warning)',
  clinical_reference: 'var(--color-primary)',
};

export default function CitationList({ citations }: CitationListProps) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const toggleExpand = (idx: number) => {
    setExpanded(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div style={{ padding: 'var(--space-5) var(--space-6)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
        <h4 style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          References
        </h4>
        <span className="badge badge-primary">{citations.length}</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {citations.map((citation, idx) => {
          const isExpanded = expanded[idx];
          const color = SOURCE_TYPE_COLORS[citation.source_type] || 'var(--color-primary)';
          const icon = SOURCE_TYPE_ICONS[citation.source_type] || SOURCE_TYPE_ICONS.default;

          return (
            <div
              key={idx}
              style={{
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border)',
                borderLeft: `3px solid ${color}`,
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                transition: 'all var(--transition-fast)',
              }}
            >
              {/* Citation Header */}
              <div
                style={{
                  padding: 'var(--space-3) var(--space-4)',
                  display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)',
                  cursor: 'pointer',
                }}
                onClick={() => toggleExpand(idx)}
              >
                {/* Reference number */}
                <div style={{
                  width: 24, height: 24, borderRadius: '50%',
                  background: color + '20',
                  border: `1px solid ${color}40`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.7rem', fontWeight: 800,
                  color: color,
                  flexShrink: 0,
                }}>
                  {idx + 1}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 4 }}>
                    <span>{icon}</span>
                    <span style={{ fontSize: '0.7rem', color: color, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {citation.source_type}
                    </span>
                    <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                      {Math.round(citation.relevance_score * 100)}% relevant
                    </span>
                  </div>

                  <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 2, lineHeight: 1.4 }}>
                    {citation.title}
                  </p>

                  {citation.authors && (
                    <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                      {citation.authors}
                      {citation.publication_date && ` · ${citation.publication_date}`}
                    </p>
                  )}
                </div>

                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', flexShrink: 0 }}>
                  {isExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Expanded snippet */}
              {isExpanded && (
                <div style={{
                  padding: 'var(--space-3) var(--space-4)',
                  borderTop: '1px solid var(--color-border)',
                  background: 'rgba(0,0,0,0.1)',
                  animation: 'fadeIn 0.2s ease-out',
                }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: citation.url ? 'var(--space-3)' : 0 }}>
                    {citation.snippet}
                  </p>
                  {citation.url && (
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ marginTop: 'var(--space-2)' }}
                    >
                      🔗 View Source
                    </a>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
