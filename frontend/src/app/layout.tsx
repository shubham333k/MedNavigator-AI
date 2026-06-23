import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Healthcare Knowledge Navigator',
  description:
    'A HIPAA-compliant AI-powered clinical decision support system for evidence-based medical queries and differential diagnosis.',
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
