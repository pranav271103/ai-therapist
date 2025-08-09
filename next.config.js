/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    experimental: {
      serverComponentsExternalPackages: []
    },
    env: {
      GEMINI_API_KEY: process.env.GEMINI_API_KEY,
    },
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: '/api/:path*',
        },
      ]
    },
  }
  
  module.exports = nextConfig
  