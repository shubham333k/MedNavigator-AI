'use client';

import { useState, useRef, useEffect } from 'react';

const SUGGESTED_QUERIES = [
  'What are the latest guidelines for managing hypertension in CKD patients?',
  'Drug interactions between warfarin and amiodarone',
  'Differential diagnosis for acute chest pain',
  'HbA1c targets in type 2 diabetes with cardiovascular disease',
  'SGLT2 inhibitors benefits in heart failure',
];

const QUERY_TYPES = [
  { value: 'general', label: 'General', icon: '💬' },
  { value: 'diagnostic', label: 'Diagnostic', icon: '🩺' },
  { value: 'drug_interaction', label: 'Drug Interaction', icon: '💊' },
  { value: 'guideline', label: 'Guideline', icon: '📋' },
];

interface QueryInputProps {
  onSubmit: (query: string, queryType: string, maxResults: number) => void;
  isLoading: boolean;
}

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [queryType, setQueryType] = useState('general');
  const [maxResults, setMaxResults] = useState(5);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit(query.trim(), queryType, maxResults);
  };

  const handleSuggestion = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      {/* Query Type Selector */}
      <div className="tabs">
        {QUERY_TYPES.map(type => (
          <button
            key={type.value}
            className={`tab ${queryType === type.value ? 'active' : ''}`}
            onClick={() => setQueryType(type.value)}
          >
            <span>{type.icon}</span>
            {type.label}
          </button>
        ))}
      </div>

      {/* Query Form */}
      <form onSubmit={handleSubmit}>
        <div style={{
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-4)',
          transition: 'all var(--transition-fast)',
        }}>
          <textarea
            ref={textareaRef}
            className="textarea"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Ask a medical question... (e.g., 'What are the first-line treatments for newly diagnosed type 2 diabetes?')"
            style={{
              background: 'transparent',
              border: 'none',
              borderRadius: 0,
              padding: 0,
              minHeight: 80,
              resize: 'none',
              outline: 'none',
              boxShadow: 'none',
              fontSize: '1rem',
            }}
            disabled={isLoading}
          />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'var(--space-3)', paddingTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
              {/* Results Count */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <label style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>Sources:</label>
                <select
                  value={maxResults}
                  onChange={e => setMaxResults(Number(e.target.value))}
                  style={{
                    background: 'var(--color-bg-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--color-text-secondary)',
                    padding: '2px 8px',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-sans)',
                  }}
                >
                  {[3, 5, 8, 10].map(n => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>

              {/* Character count */}
              <span style={{ fontSize: '0.75rem', color: query.length > 1800 ? 'var(--color-danger)' : 'var(--color-text-muted)' }}>
                {query.length}/2000
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              {query && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setQuery('')}
                >
                  Clear
                </button>
              )}
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!query.trim() || isLoading}
                style={{ minWidth: 120 }}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin" style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
                    Searching...
                  </>
                ) : (
                  <>🔍 Search</>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Suggestions */}
      {showSuggestions && !query && (
        <div style={{
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-3)',
          animation: 'fadeIn 0.2s ease-out',
        }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Suggested Queries
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
            {SUGGESTED_QUERIES.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => handleSuggestion(suggestion)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--color-text-secondary)',
                  padding: '8px var(--space-3)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '0.875rem',
                  fontFamily: 'var(--font-sans)',
                  transition: 'all var(--transition-fast)',
                  display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
                }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLElement).style.background = 'var(--color-bg-hover)';
                  (e.currentTarget as HTMLElement).style.color = 'var(--color-text-primary)';
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLElement).style.background = 'transparent';
                  (e.currentTarget as HTMLElement).style.color = 'var(--color-text-secondary)';
                }}
              >
                <span style={{ color: 'var(--color-primary)', flexShrink: 0 }}>→</span>
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
