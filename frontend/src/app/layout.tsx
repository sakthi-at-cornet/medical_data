import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Praval Agentic Analytics',
  description: 'AI-powered analytics for automotive press manufacturing',
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
