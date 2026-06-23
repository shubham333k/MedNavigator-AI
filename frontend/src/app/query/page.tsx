'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import QueryInput from '@/components/QueryInput';
import ResponseCard from '@/components/ResponseCard';
import { queryKnowledgeBase, getQueryHistory } from '@/lib/api';
import type { QueryResponse, QueryHistoryItem } from '@/types';

export default function QueryPage() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);

  useEffect(() => {
    getQueryHistory(20).then(setHistory).catch(() => {});
  }, []);

  const handleQuery = async (query: string, queryType: string, maxResults: number) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await queryKnowledgeBase(query, queryType, maxResults);
      setResult(response);

      // Refresh history
      getQueryHistory(20).then(setHistory).catch(() => {});
    } catch (err: any) {
      setError(err.message || 'Query failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <Sidebar history={history} />
      <main className="main-content">
        <div style={{ padding: 'var(--space-8)', maxWidth: 900, margin: '0 auto' }}>
          {/* Page Header */}
          <div style={{ marginBottom: 'var(--space-8)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
              <div style={{ width: 40, height: 40, background: 'var(--gradient-brand)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', boxShadow: 'var(--shadow-glow-sm)' }}>🔍</div>
              <h1 style={{ fontSize: '1.75rem' }}>Medical Query</h1>
            </div>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
              Ask clinical questions in natural language. Every response is grounded in your medical knowledge base with mandatory citations.
            </p>
          </div>

          {/* Query Input */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="card" style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-4)' }}>
                <div style={{ position: 'relative', width: 64, height: 64 }}>
                  <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '3px solid var(--color-border)', }} />
                  <div className="animate-spin" style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '3px solid transparent', borderTopColor: 'var(--color-primary)' }} />
                  <div style={{ position: 'absolute', inset: 8, borderRadius: '50%', background: 'var(--gradient-brand)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>🔍</div>
                </div>
                <div>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 4 }}>Searching Knowledge Base</p>
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Retrieving relevant documents and generating evidence-based response...</p>
                </div>
                <div style={{ display: 'flex', gap: 'var(--space-8)', marginTop: 'var(--space-2)' }}>
                  {['Embedding Query', 'Semantic Search', 'Synthesizing Response'].map((step, i) => (
                    <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                      <div className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--color-primary)' }} />
                      <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div style={{
              padding: 'var(--space-4) var(--space-5)',
              background: 'var(--color-danger-bg)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-danger)',
              display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            }}>
              <span>❌</span>
              <div>
                <p style={{ fontWeight: 600, marginBottom: 2 }}>Query Failed</p>
                <p style={{ fontSize: '0.875rem', opacity: 0.8 }}>{error}</p>
                {error.includes('ANTHROPIC_API_KEY') && (
                  <p style={{ fontSize: '0.8rem', marginTop: 4, opacity: 0.7 }}>
                    Please add your Anthropic API key to the backend <code>.env</code> file.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Result */}
          {result && !isLoading && (
            <ResponseCard result={result} />
          )}

          {/* Empty State */}
          {!result && !isLoading && !error && (
            <div className="empty-state">
              <div className="empty-state-icon" style={{ width: 80, height: 80 }}>
                <span style={{ fontSize: '2rem' }}>🔬</span>
              </div>
              <h3>Ready to search</h3>
              <p>
                Ask a medical question above. Your query will be matched against clinical guidelines, PubMed abstracts, and drug references.
              </p>
              <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap', justifyContent: 'center', marginTop: 'var(--space-2)' }}>
                {['Hypertension in CKD', 'Warfarin interactions', 'Chest pain DDx'].map(tag => (
                  <span key={tag} className="badge badge-primary" style={{ cursor: 'pointer', padding: '4px 12px' }}>{tag}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
