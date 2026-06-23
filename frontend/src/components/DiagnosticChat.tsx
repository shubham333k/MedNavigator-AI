'use client';

import { useState, useRef, useEffect } from 'react';
import { startDiagnostic, respondToDiagnostic } from '@/lib/api';
import type { DiagnosticResponse, Diagnosis } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'agent' | 'system';
  content: string;
  isFollowUp?: boolean;
}

export default function DiagnosticChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<string>('idle');
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientSex, setPatientSex] = useState('');
  const [medHistory, setMedHistory] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleStart = async () => {
    if (!symptoms.trim() || isLoading) return;

    const symptomList = symptoms.split(',').map(s => s.trim()).filter(Boolean);
    const historyList = medHistory ? medHistory.split(',').map(s => s.trim()).filter(Boolean) : [];

    setIsLoading(true);
    setMessages([{
      role: 'user',
      content: `**Symptoms:** ${symptomList.join(', ')}${patientAge ? `\n**Age:** ${patientAge}` : ''}${patientSex ? `\n**Sex:** ${patientSex}` : ''}${historyList.length ? `\n**Medical History:** ${historyList.join(', ')}` : ''}`,
    }]);

    try {
      const response = await startDiagnostic(
        symptomList,
        patientAge ? parseInt(patientAge) : undefined,
        patientSex || undefined,
        historyList.length ? historyList : undefined,
      );

      setSessionId(response.session_id);
      setCurrentStage(response.stage);
      setIsComplete(response.is_complete);

      const agentMsg: Message = { role: 'agent', content: response.message };
      if (response.follow_up_question) {
        agentMsg.isFollowUp = true;
        agentMsg.content += `\n\n---\n\n**Follow-up Question:** ${response.follow_up_question}`;
      }
      setMessages(prev => [...prev, agentMsg]);

      if (response.differential_diagnoses?.length) {
        setDiagnoses(response.differential_diagnoses);
      }
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ Error: ${err.message}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRespond = async () => {
    if (!inputValue.trim() || !sessionId || isLoading || isComplete) return;

    const userMsg = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const response = await respondToDiagnostic(sessionId, userMsg);
      setCurrentStage(response.stage);
      setIsComplete(response.is_complete);

      const agentMsg: Message = { role: 'agent', content: response.message };
      if (response.follow_up_question && !response.is_complete) {
        agentMsg.isFollowUp = true;
        agentMsg.content += `\n\n---\n\n**Follow-up Question:** ${response.follow_up_question}`;
      }
      setMessages(prev => [...prev, agentMsg]);

      if (response.differential_diagnoses?.length) {
        setDiagnoses(response.differential_diagnoses);
      }
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'system', content: `❌ Error: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setSessionId(null);
    setCurrentStage('idle');
    setIsComplete(false);
    setDiagnoses([]);
    setSymptoms('');
    setPatientAge('');
    setPatientSex('');
    setMedHistory('');
    setInputValue('');
  };

  const LIKELIHOOD_COLORS: Record<string, string> = {
    High: 'var(--color-danger)',
    Medium: 'var(--color-warning)',
    Low: 'var(--color-success)',
  };

  const STAGE_LABELS: Record<string, string> = {
    idle: '⬡ Ready',
    gathering: '🔍 Gathering information',
    reasoning: '🧠 Analyzing conditions',
    refining: '🔬 Refining diagnosis',
    complete: '✅ Analysis complete',
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: diagnoses.length ? '1fr 340px' : '1fr', gap: 'var(--space-6)', height: 'calc(100vh - 180px)' }}>
      {/* Main Chat Area */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', overflow: 'hidden' }}>
        {/* Stage indicator */}
        {currentStage !== 'idle' && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: 'var(--space-3) var(--space-4)',
            background: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
          }}>
            <div className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: isComplete ? 'var(--color-success)' : 'var(--color-primary)' }} />
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
              {STAGE_LABELS[currentStage] || currentStage}
            </span>
            {!isComplete && (
              <button className="btn btn-ghost btn-sm" onClick={handleReset} style={{ marginLeft: 'auto' }}>
                🔄 Reset
              </button>
            )}
            {isComplete && (
              <button className="btn btn-secondary btn-sm" onClick={handleReset} style={{ marginLeft: 'auto' }}>
                New Session
              </button>
            )}
          </div>
        )}

        {/* Initial Form */}
        {currentStage === 'idle' && (
          <div className="card" style={{ padding: 'var(--space-6)' }}>
            <h3 style={{ marginBottom: 'var(--space-5)', color: 'var(--color-text-primary)' }}>
              🩺 Patient Presentation
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div className="form-group">
                <label className="label">Symptoms * (comma-separated)</label>
                <textarea
                  className="textarea"
                  value={symptoms}
                  onChange={e => setSymptoms(e.target.value)}
                  placeholder="e.g., chest pain, shortness of breath, diaphoresis"
                  style={{ minHeight: 80 }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <div className="form-group">
                  <label className="label">Age</label>
                  <input
                    type="number" className="input"
                    value={patientAge} onChange={e => setPatientAge(e.target.value)}
                    placeholder="e.g., 55" min={0} max={150}
                  />
                </div>
                <div className="form-group">
                  <label className="label">Sex</label>
                  <select
                    className="input"
                    value={patientSex}
                    onChange={e => setPatientSex(e.target.value)}
                    style={{ cursor: 'pointer' }}
                  >
                    <option value="">Not specified</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="label">Relevant Medical History (optional, comma-separated)</label>
                <input
                  type="text" className="input"
                  value={medHistory} onChange={e => setMedHistory(e.target.value)}
                  placeholder="e.g., hypertension, diabetes, prior MI"
                />
              </div>

              <button
                className="btn btn-primary btn-lg"
                onClick={handleStart}
                disabled={!symptoms.trim() || isLoading}
                style={{ alignSelf: 'flex-start' }}
              >
                {isLoading ? (
                  <><div className="animate-spin" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} /> Analyzing...</>
                ) : '🩺 Start Diagnostic'}
              </button>
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.length > 0 && (
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{
                display: 'flex',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                gap: 'var(--space-3)',
                animation: 'fadeIn 0.3s ease-out',
              }}>
                <div style={{
                  width: 32, height: 32,
                  borderRadius: '50%',
                  background: msg.role === 'user' ? 'var(--gradient-brand)' : msg.role === 'agent' ? 'rgba(14,165,233,0.15)' : 'var(--color-danger-bg)',
                  border: `1px solid ${msg.role === 'user' ? 'transparent' : 'var(--color-border)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.9rem',
                  flexShrink: 0,
                  marginTop: 4,
                }}>
                  {msg.role === 'user' ? '👨‍⚕️' : msg.role === 'agent' ? '🤖' : '⚠️'}
                </div>

                <div style={{
                  maxWidth: '80%',
                  background: msg.role === 'user' ? 'rgba(14,165,233,0.12)' : 'var(--color-bg-elevated)',
                  border: `1px solid ${msg.role === 'user' ? 'rgba(14,165,233,0.2)' : 'var(--color-border)'}`,
                  borderRadius: 'var(--radius-lg)',
                  padding: 'var(--space-4)',
                }}>
                  <div className="prose" style={{ fontSize: '0.9rem' }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(14,165,233,0.15)', border: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🤖</div>
                <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Response Input */}
        {sessionId && !isComplete && currentStage !== 'idle' && (
          <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-end' }}>
            <input
              type="text"
              className="input"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleRespond()}
              placeholder="Respond to the follow-up question..."
              disabled={isLoading}
            />
            <button
              className="btn btn-primary"
              onClick={handleRespond}
              disabled={!inputValue.trim() || isLoading}
              style={{ flexShrink: 0 }}
            >
              Send
            </button>
          </div>
        )}
      </div>

      {/* Differential Diagnoses Panel */}
      {diagnoses.length > 0 && (
        <div style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--color-border)', background: 'rgba(14,165,233,0.05)' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Differential Diagnoses
            </h4>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {diagnoses.map((d, i) => (
              <div key={i} style={{
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border)',
                borderLeft: `3px solid ${LIKELIHOOD_COLORS[d.likelihood] || 'var(--color-primary)'}`,
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>{d.condition}</p>
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: LIKELIHOOD_COLORS[d.likelihood] || 'var(--color-primary)', background: (LIKELIHOOD_COLORS[d.likelihood] || 'var(--color-primary)') + '15', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                    {d.likelihood}
                  </span>
                </div>
                <div style={{ height: 4, background: 'var(--color-bg-card)', borderRadius: 'var(--radius-full)', overflow: 'hidden', marginBottom: 6 }}>
                  <div style={{ width: `${d.confidence_score * 100}%`, height: '100%', background: LIKELIHOOD_COLORS[d.likelihood] || 'var(--color-primary)', borderRadius: 'var(--radius-full)', transition: 'width 1s ease' }} />
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{Math.round(d.confidence_score * 100)}% confidence</p>
              </div>
            ))}
          </div>
          <div style={{ padding: 'var(--space-3) var(--space-4)', borderTop: '1px solid var(--color-border)', background: 'rgba(245,158,11,0.05)' }}>
            <p style={{ fontSize: '0.7rem', color: 'var(--color-warning)', lineHeight: 1.5 }}>
              ⚠️ For clinical decision support only. Requires physician judgment.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
