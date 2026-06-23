'use client';

import { useState } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { ingestSampleData, ingestPubMed, uploadDocument, getIngestionStats } from '@/lib/api';

export default function IngestPage() {
  const [activeTab, setActiveTab] = useState<'sample' | 'pubmed' | 'upload'>('sample');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [resultType, setResultType] = useState<'success' | 'error'>('success');

  // PubMed form
  const [pubmedQuery, setPubmedQuery] = useState('');
  const [pubmedMax, setPubmedMax] = useState(5);

  // Upload form
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadType, setUploadType] = useState('pdf');
  const [uploadUrl, setUploadUrl] = useState('');

  const showResult = (msg: string, type: 'success' | 'error') => {
    setResult(msg);
    setResultType(type);
    setTimeout(() => setResult(null), 6000);
  };

  const handleSampleData = async () => {
    setIsLoading(true);
    try {
      const res = await ingestSampleData();
      showResult(`✅ Loaded ${res.documents_processed} documents, ${res.chunks_created} chunks (${res.processing_time_ms.toFixed(0)}ms)`, 'success');
    } catch (err: any) {
      showResult(`❌ ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePubMed = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pubmedQuery.trim()) return;
    setIsLoading(true);
    try {
      const res = await ingestPubMed(pubmedQuery, pubmedMax);
      showResult(`✅ Ingested ${res.documents_processed} PubMed articles, ${res.chunks_created} chunks`, 'success');
    } catch (err: any) {
      showResult(`❌ ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle) return;
    setIsLoading(true);
    try {
      const res = await uploadDocument(uploadFile, uploadTitle, uploadType, uploadUrl || undefined);
      showResult(`✅ Uploaded "${uploadTitle}" — ${res.chunks_created} chunks created`, 'success');
      setUploadFile(null);
      setUploadTitle('');
      setUploadUrl('');
    } catch (err: any) {
      showResult(`❌ ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const SAMPLE_DOCS = [
    { title: 'JNC 8 Hypertension Guidelines', category: 'Cardiology', icon: '❤️' },
    { title: 'ADA Standards of Care in Diabetes 2024', category: 'Endocrinology', icon: '🩸' },
    { title: 'Common Drug Interactions Reference', category: 'Pharmacology', icon: '💊' },
    { title: 'Differential Diagnosis of Chest Pain', category: 'Emergency Medicine', icon: '🫀' },
    { title: 'KDIGO CKD Management Guidelines', category: 'Nephrology', icon: '🔬' },
  ];

  return (
    <>
      <Navbar />
      <Sidebar />
      <main className="main-content">
        <div style={{ padding: 'var(--space-8)', maxWidth: 800 }}>
          {/* Header */}
          <div style={{ marginBottom: 'var(--space-8)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
              <div style={{ width: 40, height: 40, background: 'linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>📚</div>
              <h1 style={{ fontSize: '1.75rem' }}>Knowledge Base</h1>
            </div>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
              Manage your medical knowledge base. Ingest clinical guidelines, research papers, and drug references.
            </p>
          </div>

          {/* Toast */}
          {result && (
            <div className={`toast ${resultType === 'success' ? 'toast-success' : 'toast-error'}`}>
              {result}
            </div>
          )}

          {/* Tabs */}
          <div className="tabs" style={{ marginBottom: 'var(--space-6)' }}>
            {[
              { id: 'sample', label: 'Sample Data', icon: '📋' },
              { id: 'pubmed', label: 'PubMed', icon: '🔬' },
              { id: 'upload', label: 'Upload File', icon: '📤' },
            ].map(tab => (
              <button
                key={tab.id}
                className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id as any)}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Sample Data Tab */}
          {activeTab === 'sample' && (
            <div className="card" style={{ padding: 'var(--space-6)' }}>
              <h3 style={{ marginBottom: 'var(--space-2)' }}>Built-in Sample Medical Data</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: 'var(--space-5)' }}>
                Load pre-built clinical guidelines and reference documents to get started immediately.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
                {SAMPLE_DOCS.map((doc, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', padding: 'var(--space-3) var(--space-4)', background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
                    <span style={{ fontSize: '1.5rem' }}>{doc.icon}</span>
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 2 }}>{doc.title}</p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{doc.category}</p>
                    </div>
                    <span className="badge badge-success" style={{ marginLeft: 'auto' }}>Included</span>
                  </div>
                ))}
              </div>

              <button className="btn btn-primary" onClick={handleSampleData} disabled={isLoading}>
                {isLoading ? <><div className="animate-spin" style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Loading...</> : '📚 Load Sample Data'}
              </button>
            </div>
          )}

          {/* PubMed Tab */}
          {activeTab === 'pubmed' && (
            <div className="card" style={{ padding: 'var(--space-6)' }}>
              <h3 style={{ marginBottom: 'var(--space-2)' }}>Fetch from PubMed</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: 'var(--space-5)' }}>
                Search PubMed and automatically ingest matching abstracts into the knowledge base.
              </p>
              <form onSubmit={handlePubMed} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div className="form-group">
                  <label className="label">PubMed Search Query</label>
                  <input type="text" className="input" value={pubmedQuery} onChange={e => setPubmedQuery(e.target.value)}
                    placeholder="e.g., hypertension chronic kidney disease management 2024" required />
                </div>
                <div className="form-group">
                  <label className="label">Max Articles</label>
                  <select className="input" value={pubmedMax} onChange={e => setPubmedMax(Number(e.target.value))} style={{ cursor: 'pointer' }}>
                    {[5, 10, 20, 50].map(n => <option key={n} value={n}>{n} articles</option>)}
                  </select>
                </div>
                <button type="submit" className="btn btn-primary" disabled={isLoading || !pubmedQuery.trim()} style={{ alignSelf: 'flex-start' }}>
                  {isLoading ? <><div className="animate-spin" style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Fetching...</> : '🔬 Fetch & Ingest'}
                </button>
              </form>
            </div>
          )}

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div className="card" style={{ padding: 'var(--space-6)' }}>
              <h3 style={{ marginBottom: 'var(--space-2)' }}>Upload Document</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: 'var(--space-5)' }}>
                Upload clinical guidelines, drug references, or research papers (PDF, CSV, JSON, TXT).
              </p>
              <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div className="form-group">
                  <label className="label">File</label>
                  <input
                    type="file" accept=".pdf,.csv,.json,.txt"
                    onChange={e => setUploadFile(e.target.files?.[0] || null)}
                    style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: 'var(--color-text-secondary)', width: '100%', cursor: 'pointer', fontFamily: 'var(--font-sans)' }}
                    required
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                  <div className="form-group">
                    <label className="label">Document Title</label>
                    <input type="text" className="input" value={uploadTitle} onChange={e => setUploadTitle(e.target.value)} placeholder="e.g., ACC Heart Failure Guidelines 2024" required />
                  </div>
                  <div className="form-group">
                    <label className="label">Document Type</label>
                    <select className="input" value={uploadType} onChange={e => setUploadType(e.target.value)} style={{ cursor: 'pointer' }}>
                      <option value="pdf">PDF</option>
                      <option value="csv">CSV</option>
                      <option value="json">JSON</option>
                      <option value="text">Plain Text</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="label">Source URL (optional)</label>
                  <input type="url" className="input" value={uploadUrl} onChange={e => setUploadUrl(e.target.value)} placeholder="https://..." />
                </div>
                <button type="submit" className="btn btn-primary" disabled={isLoading || !uploadFile || !uploadTitle} style={{ alignSelf: 'flex-start' }}>
                  {isLoading ? <><div className="animate-spin" style={{ width: 14, height: 14, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Uploading...</> : '📤 Upload & Ingest'}
                </button>
              </form>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
