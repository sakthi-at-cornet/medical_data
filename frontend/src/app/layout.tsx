import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Praval Medical Analytics',
  description: 'AI-powered analytics for radiology audits and quality metrics',
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
