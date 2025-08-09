import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method === 'GET') {
    res.status(200).json({
      status: 'healthy',
      message: 'Dr. HelAI is running on Vercel',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
      environment: 'production'
    })
  } else {
    res.setHeader('Allow', ['GET', 'OPTIONS'])
    res.status(405).end(`Method ${req.method} Not Allowed`)
  }
}
