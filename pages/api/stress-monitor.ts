import type { NextApiRequest, NextApiResponse } from 'next'

// This would connect to your actual conversation storage in production
const getConversationHistory = () => {
  // Simulate conversation history - replace with actual data source
  return []
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET', 'OPTIONS'])
    res.status(405).end(`Method ${req.method} Not Allowed`)
    return
  }

  try {
    const conversations = getConversationHistory()
    
    if (conversations.length === 0) {
      res.status(200).json({
        status: 'success',
        current_stress: 5,
        trend: 'stable',
        last_updated: new Date().toISOString(),
        stress_history: [],
        average_stress: 5,
        peak_stress: 5,
        sessions_count: 0
      })
      return
    }

    // Calculate stress metrics
    const recentStress = conversations.slice(-10).map((conv: any) => conv.stress_level || 5)
    const currentStress = recentStress[recentStress.length - 1] || 5
    
    let trend = 'stable'
    if (recentStress.length > 1) {
      const prevStress = recentStress[recentStress.length - 2]
      if (currentStress > prevStress) trend = 'increasing'
      else if (currentStress < prevStress) trend = 'decreasing'
    }

    res.status(200).json({
      status: 'success',
      current_stress: currentStress,
      trend,
      last_updated: new Date().toISOString(),
      stress_history: recentStress.slice(-5).map((stress, i) => ({
        time: new Date().toISOString(),
        stress,
        session: i + 1
      })),
      average_stress: recentStress.reduce((a, b) => a + b, 0) / recentStress.length,
      peak_stress: Math.max(...recentStress),
      sessions_count: conversations.length
    })
  } catch (error) {
    console.error('Stress Monitor Error:', error)
    
    res.status(500).json({
      status: 'error',
      current_stress: 5,
      trend: 'stable',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
