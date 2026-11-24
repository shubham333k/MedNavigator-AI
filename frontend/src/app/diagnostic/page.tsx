'use client';

import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import DiagnosticChat from '@/components/DiagnosticChat';

export default function DiagnosticPage() {
  return (
    <>
      <Navbar />
      <Sidebar />
      <main className="main-content">
        <div style={{ padding: 'var(--space-8)', height: 'calc(100vh - var(--navbar-height))', display: 'flex', flexDirection: 'column' }}>
          {/* Page Header */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
              <div style={{ width: 40, height: 40, background: 'linear-gradient(135deg, #22d3ee 0%, #0ea5e9 100%)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', boxShadow: '0 0 16px rgba(34,211,238,0.25)' }}>🩺</div>
              <div>
                <h1 style={{ fontSize: '1.75rem' }}>Diagnostic Assistant</h1>
              </div>
            </div>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
              AI-powered differential diagnosis. Enter patient symptoms and receive evidence-based diagnostic considerations with supporting literature.
            </p>
          </div>

          {/* Info Banner */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: 'var(--space-3) var(--space-4)',
            background: 'rgba(59,130,246,0.08)',
            border: '1px solid rgba(59,130,246,0.2)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-5)',
          }}>
            <span>ℹ️</span>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              <strong style={{ color: 'var(--color-info)' }}>Patient data notice:</strong> All symptom data is processed in-memory only and is not stored. Do not enter identified patient information (names, DOB, MRN).
            </p>
          </div>

          {/* Diagnostic Chat */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <DiagnosticChat />
          </div>
        </div>
      </main>
    </>
  );
}
