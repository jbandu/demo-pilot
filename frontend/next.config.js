/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Use standalone output only for Docker/Railway deployments, not for Vercel
  ...(process.env.VERCEL ? {} : { output: 'standalone' }),
  async rewrites() {
    // Use environment variable for backend URL (NEXT_PUBLIC_API_URL for Vercel, NEXT_PUBLIC_BACKEND_URL for local)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
