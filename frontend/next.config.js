/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // When deployed on Vercel with the current vercel.json configuration,
  // the frontend build is accessed via the /frontend prefix.
  // We use basePath to align Next.js routing with this rewrite.
  // basePath: process.env.VERCEL ? '/frontend' : '',
}

module.exports = nextConfig
