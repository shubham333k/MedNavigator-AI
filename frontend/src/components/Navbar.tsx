'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getStoredUser, clearAuth } from '@/lib/auth';
import type { User } from '@/types';

const NAV_LINKS = [
  { href: '/',           label: 'Dashboard',   icon: '⬡' },
  { href: '/query',      label: 'Query',        icon: '🔍' },
  { href: '/diagnostic', label: 'Diagnostic',   icon: '🩺' },
  { href: '/ingest',     label: 'Knowledge Base',icon: '📚' },
];

const ROLE_BADGE_COLORS: Record<string, string> = {
  admin:      'badge-danger',
  clinician:  'badge-primary',
  researcher: 'badge-success',
};

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  const handleLogout = () => {
    clearAuth();
    router.push('/login');
  };

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: 'var(--navbar-height)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 var(--space-6)',
      background: 'rgba(8, 13, 20, 0.9)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid var(--color-border)',
      boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
    }}>
      {/* Logo */}
      <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', textDecoration: 'none' }}>
        <div style={{
          width: 36, height: 36,
          background: 'var(--gradient-brand)',
          borderRadius: 'var(--radius-md)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.1rem',
          boxShadow: 'var(--shadow-glow-sm)',
        }}>🏥</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--color-text-primary)', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            Healthcare
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', lineHeight: 1 }}>
            Knowledge Navigator
          </div>
        </div>
      </Link>

      {/* Nav Links */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
        {NAV_LINKS.map(link => {
          const isActive = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
              style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                padding: '6px 14px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
                fontWeight: 500,
                textDecoration: 'none',
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                background: isActive ? 'rgba(14,165,233,0.1)' : 'transparent',
                border: isActive ? '1px solid rgba(14,165,233,0.2)' : '1px solid transparent',
                transition: 'all var(--transition-fast)',
              }}
            >
              <span style={{ fontSize: '1rem' }}>{link.icon}</span>
              {link.label}
            </Link>
          );
        })}
      </div>

      {/* User Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', position: 'relative' }}>
        {user ? (
          <>
            <span className={`badge ${ROLE_BADGE_COLORS[user.role] || 'badge-primary'}`}>
              {user.role}
            </span>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: '6px 12px',
                cursor: 'pointer',
                color: 'var(--color-text-primary)',
                fontSize: '0.875rem',
                fontWeight: 500,
                fontFamily: 'var(--font-sans)',
              }}
            >
              <div style={{
                width: 28, height: 28,
                background: 'var(--gradient-brand)',
                borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 700,
              }}>
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <span>{user.full_name.split(' ')[0]}</span>
              <span style={{ fontSize: '0.6rem', color: 'var(--color-text-muted)' }}>▼</span>
            </button>

            {menuOpen && (
              <div style={{
                position: 'absolute', top: '110%', right: 0,
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-2)',
                minWidth: 180,
                boxShadow: 'var(--shadow-lg)',
                zIndex: 100,
                animation: 'fadeIn 0.15s ease-out',
              }}>
                <div style={{ padding: 'var(--space-2) var(--space-3)', borderBottom: '1px solid var(--color-border)', marginBottom: 'var(--space-2)' }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>{user.full_name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{user.email}</div>
                </div>
                <button
                  onClick={handleLogout}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                    padding: 'var(--space-2) var(--space-3)',
                    background: 'transparent', border: 'none',
                    color: 'var(--color-danger)', cursor: 'pointer',
                    fontSize: '0.875rem', borderRadius: 'var(--radius-sm)',
                    fontFamily: 'var(--font-sans)',
                  }}
                >
                  🚪 Sign Out
                </button>
              </div>
            )}
          </>
        ) : (
          <Link href="/login" className="btn btn-primary btn-sm">Sign In</Link>
        )}
      </div>
    </nav>
  );
}
