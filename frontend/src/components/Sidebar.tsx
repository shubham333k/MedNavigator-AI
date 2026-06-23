'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface HistoryItem {
  query_id: string;
  query: string;
  timestamp: string;
  query_type: string;
  citation_count: number;
}

interface SidebarProps {
  history?: HistoryItem[];
}

const QUERY_TYPE_ICONS: Record<string, string> = {
  general: '💬',
  diagnostic: '🩺',
  drug_interaction: '💊',
  guideline: '📋',
};

export default function Sidebar({ history = [] }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside style={{
      position: 'fixed',
      top: 'var(--navbar-height)',
      left: 0,
      width: 'var(--sidebar-width)',
      height: 'calc(100vh - var(--navbar-height))',
      background: 'var(--color-bg-surface)',
      borderRight: '1px solid var(--color-border)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      zIndex: 50,
    }}>
      {/* Quick Actions */}
      <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--color-border)' }}>
        <p style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--color-text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 'var(--space-3)' }}>
          Quick Actions
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <Link href="/query" style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: '10px var(--space-3)',
            background: pathname === '/query' ? 'rgba(14,165,233,0.1)' : 'var(--color-bg-elevated)',
            border: `1px solid ${pathname === '/query' ? 'var(--color-border-bright)' : 'var(--color-border)'}`,
            borderRadius: 'var(--radius-md)',
            color: pathname === '/query' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 500,
            transition: 'all var(--transition-fast)',
          }}>
            <span>🔍</span> Medical Query
          </Link>

          <Link href="/diagnostic" style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: '10px var(--space-3)',
            background: pathname === '/diagnostic' ? 'rgba(14,165,233,0.1)' : 'var(--color-bg-elevated)',
            border: `1px solid ${pathname === '/diagnostic' ? 'var(--color-border-bright)' : 'var(--color-border)'}`,
            borderRadius: 'var(--radius-md)',
            color: pathname === '/diagnostic' ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 500,
            transition: 'all var(--transition-fast)',
          }}>
            <span>🩺</span> Diagnostic Assistant
          </Link>
        </div>
      </div>

      {/* Query History */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 'var(--space-4) var(--space-4) var(--space-2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--color-text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Recent Queries
          </p>
          {history.length > 0 && (
            <span className="badge badge-primary">{history.length}</span>
          )}
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--space-3) var(--space-4)' }}>
          {history.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 'var(--space-8) var(--space-4)', color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>📋</div>
              <div>No queries yet</div>
              <div style={{ marginTop: 4 }}>Start searching to see history</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {history.map(item => (
                <div
                  key={item.query_id}
                  style={{
                    padding: 'var(--space-3)',
                    background: 'var(--color-bg-elevated)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                  }}
                  onMouseEnter={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-border-bright)';
                    (e.currentTarget as HTMLElement).style.background = 'var(--color-bg-hover)';
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-border)';
                    (e.currentTarget as HTMLElement).style.background = 'var(--color-bg-elevated)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 4 }}>
                    <span>{QUERY_TYPE_ICONS[item.query_type] || '💬'}</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)', marginLeft: 'auto' }}>
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <p style={{
                    fontSize: '0.8rem',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.4,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    margin: 0,
                  }}>
                    {item.query}
                  </p>
                  {item.citation_count > 0 && (
                    <div style={{ marginTop: 4, fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                      {item.citation_count} citation{item.citation_count > 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      <div style={{
        padding: 'var(--space-4)',
        borderTop: '1px solid var(--color-border)',
        background: 'var(--color-bg-elevated)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: 'var(--color-success)',
            boxShadow: '0 0 6px var(--color-success)',
          }} />
          HIPAA Compliant
          <span style={{ marginLeft: 'auto', color: 'var(--color-text-muted)' }}>v1.0</span>
        </div>
      </div>
    </aside>
  );
}
