import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Healthcare Knowledge Navigator',
  description:
    'An AI-powered clinical decision support system with HIPAA-aligned security controls (educational project, not certified).',
  keywords: ['healthcare', 'clinical decision support', 'RAG', 'medical AI', 'HIPAA'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
