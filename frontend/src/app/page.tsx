'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { getQueryHistory, getIngestionStats, ingestSampleData, getHealth } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import type { QueryHistoryItem } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [seedMsg, setSeedMsg] = useState('');

  useEffect(() => {
    const init = async () => {
      try {
        const [h, s, hlt] = await Promise.all([
          getQueryHistory(5).catch(() => []),
          getIngestionStats().catch(() => null),
          getHealth().catch(() => null),
        ]);
        setHistory(h);
        setStats(s);
        setHealth(hlt);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const handleSeedData = async () => {
    setSeeding(true);
    setSeedMsg('');
    try {
      const result = await ingestSampleData();
      setSeedMsg(`✅ Loaded ${result.documents_processed} documents (${result.chunks_created} chunks)`);
      const s = await getIngestionStats().catch(() => null);
      setStats(s);
    } catch (err: any) {
      setSeedMsg(`❌ ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  const QUICK_ACTIONS = [
    { href: '/query', icon: '🔍', title: 'Medical Query', desc: 'Search clinical guidelines and literature', color: '#0ea5e9' },
    { href: '/diagnostic', icon: '🩺', title: 'Diagnostic Assistant', desc: 'AI-powered differential diagnosis', color: '#22d3ee' },
    { href: '/ingest', icon: '📚', title: 'Knowledge Base', desc: 'Manage your medical document library', color: '#38bdf8' },
  ];

  return (
    <>
      <Navbar />
      <Sidebar history={history} />
      <main className="main-content">
        <div className="content-area" style={{ padding: 'var(--space-8)' }}>
          {/* Hero */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(14,165,233,0.12) 0%, rgba(34,211,238,0.06) 100%)',
            border: '1px solid var(--color-border-bright)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--space-10)',
            marginBottom: 'var(--space-8)',
            position: 'relative',
            overflow: 'hidden',
          }}>
            {/* Background glow */}
            <div style={{ position: 'absolute', top: -60, right: -60, width: 300, height: 300, background: 'radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />

            <div style={{ position: 'relative', zIndex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                <div style={{ width: 48, height: 48, background: 'var(--gradient-brand)', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', boxShadow: 'var(--shadow-glow-sm)' }}>🏥</div>
                <div>
                  <span className="badge badge-success" style={{ marginBottom: 4, display: 'inline-flex' }}>HIPAA Compliant</span>
                </div>
              </div>
              <h1 style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>
                <span className="glow-text">Healthcare Knowledge</span>
                <br />Navigator for Clinicians
              </h1>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '1.05rem', maxWidth: 560, lineHeight: 1.7, marginBottom: 'var(--space-6)' }}>
                AI-powered evidence-based clinical decision support. Query medical literature, get cited responses, and navigate complex differential diagnoses.
              </p>
              <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                <Link href="/query" className="btn btn-primary btn-lg">
                  🔍 Start Querying
                </Link>
                {(!stats || stats.total_chunks === 0) && (
                  <button className="btn btn-secondary btn-lg" onClick={handleSeedData} disabled={seeding}>
                    {seeding ? <><div className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Loading...</> : '📚 Load Sample Data'}
                  </button>
                )}
              </div>
              {seedMsg && <p style={{ marginTop: 'var(--space-3)', fontSize: '0.875rem', color: seedMsg.startsWith('✅') ? 'var(--color-success)' : 'var(--color-danger)' }}>{seedMsg}</p>}
            </div>
          </div>

          {/* Stats Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
            {[
              { label: 'Knowledge Chunks', value: loading ? '...' : (stats?.total_chunks || 0).toLocaleString(), icon: '📊', color: '#0ea5e9' },
              { label: 'Recent Queries', value: loading ? '...' : history.length, icon: '🔍', color: '#22d3ee' },
              { label: 'System Status', value: health?.status || 'offline', icon: '🟢', color: '#10b981' },
              { label: 'LLM Model', value: 'Claude 3.5', icon: '🤖', color: '#8b5cf6' },
            ].map((stat, i) => (
              <div key={i} className="card" style={{ padding: 'var(--space-5)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
                  <span style={{ fontSize: '1.5rem' }}>{stat.icon}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{stat.label}</span>
                </div>
                <p style={{ fontSize: '1.75rem', fontWeight: 800, color: stat.color, letterSpacing: '-0.03em' }}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-5)', color: 'var(--color-text-secondary)' }}>Quick Actions</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
            {QUICK_ACTIONS.map((action, i) => (
              <Link key={i} href={action.href} style={{ textDecoration: 'none' }}>
                <div className="card" style={{ padding: 'var(--space-6)', cursor: 'pointer', borderLeft: `3px solid ${action.color}` }}>
                  <div style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>{action.icon}</div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: 'var(--space-2)', color: action.color }}>{action.title}</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>{action.desc}</p>
                </div>
              </Link>
            ))}
          </div>

          {/* Recent Queries */}
          {history.length > 0 && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                <h2 style={{ fontSize: '1.25rem', color: 'var(--color-text-secondary)' }}>Recent Queries</h2>
                <Link href="/query" style={{ fontSize: '0.875rem', color: 'var(--color-primary)' }}>View All →</Link>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {history.slice(0, 3).map(item => (
                  <div key={item.query_id} className="card" style={{ padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                    <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'rgba(14,165,233,0.1)', border: '1px solid rgba(14,165,233,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      💬
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.query}</p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{item.citation_count} citations · {new Date(item.timestamp).toLocaleDateString()}</p>
                    </div>
                    <span className="badge badge-primary">{item.query_type}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </main>
    </>
  );
}
