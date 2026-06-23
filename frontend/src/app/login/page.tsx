'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/api';
import { saveAuth } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@healthcare.nav');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const tokens = await login(email, password);
      saveAuth(tokens);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--color-bg-base)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-4)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background decoration */}
      <div style={{ position: 'absolute', top: '-20%', left: '50%', transform: 'translateX(-50%)', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '-10%', right: '-10%', width: '400px', height: '400px', background: 'radial-gradient(circle, rgba(34,211,238,0.05) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: 440, position: 'relative', zIndex: 1 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <div style={{ width: 64, height: 64, background: 'var(--gradient-brand)', borderRadius: 'var(--radius-xl)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', margin: '0 auto var(--space-4)', boxShadow: 'var(--shadow-glow)' }}>🏥</div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: 'var(--space-2)' }}>
            <span className="glow-text">Healthcare</span> Navigator
          </h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
            HIPAA-Compliant Clinical Decision Support
          </p>
        </div>

        {/* Login Card */}
        <div className="card" style={{ padding: 'var(--space-8)' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-6)', textAlign: 'center' }}>
            Sign In
          </h2>

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="form-group">
              <label className="label">Email Address</label>
              <input
                type="email"
                className="input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="clinician@hospital.org"
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div style={{
                padding: 'var(--space-3) var(--space-4)',
                background: 'var(--color-danger-bg)',
                border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--color-danger)',
                fontSize: '0.875rem',
                display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
              }}>
                <span>❌</span> {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isLoading}
              style={{ width: '100%', marginTop: 'var(--space-2)' }}
            >
              {isLoading ? (
                <><div className="animate-spin" style={{ width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Signing in...</>
              ) : '🔐 Sign In'}
            </button>
          </form>

          {/* Demo credentials */}
          <div style={{
            marginTop: 'var(--space-6)',
            padding: 'var(--space-4)',
            background: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
          }}>
            <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 'var(--space-3)' }}>
              Demo Credentials
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {[
                { role: 'Admin', email: 'admin@healthcare.nav', pass: 'admin123', color: 'var(--color-danger)' },
              ].map(cred => (
                <button
                  key={cred.role}
                  onClick={() => { setEmail(cred.email); setPassword(cred.pass); }}
                  style={{
                    background: 'var(--color-bg-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: 'var(--space-2) var(--space-3)',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    textAlign: 'left',
                    fontFamily: 'var(--font-sans)',
                    display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                  }}
                >
                  <span className={`badge badge-danger`} style={{ fontSize: '0.65rem' }}>{cred.role}</span>
                  <span style={{ fontFamily: 'var(--font-mono)' }}>{cred.email}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Security notice */}
        <div style={{ textAlign: 'center', marginTop: 'var(--space-6)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-2)' }}>
          <span style={{ fontSize: '0.75rem' }}>🔒</span>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Secured with JWT · TLS 1.3 · HIPAA Compliant
          </p>
        </div>
      </div>
    </div>
  );
}
