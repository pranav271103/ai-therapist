import type { NextApiRequest, NextApiResponse } from 'next'

let conversationHistory: any[] = []

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST', 'OPTIONS'])
    res.status(405).end(`Method ${req.method} Not Allowed`)
    return
  }

  try {
    const { message } = req.body

    if (!message || !message.trim()) {
      res.status(400).json({ error: 'Empty message' })
      return
    }

    // Generate therapeutic response without external API
    const responses = [
      "Thank you for sharing that with me. Your feelings are valid and important.",
      "I hear you, and I want you to know that you're not alone in feeling this way.",
      "It takes courage to express what you're going through. How are you taking care of yourself today?",
      "I appreciate you opening up to me. What would feel most supportive right now?",
      "Your emotional experience matters. Let's explore what might help you feel more grounded."
    ]
    
    const aiResponse = responses[Math.floor(Math.random() * responses.length)]

    // Simple stress analysis
    const stressKeywords = ['stressed', 'anxious', 'worried', 'panic', 'overwhelmed', 'crisis', 'depressed', 'sad', 'angry', 'frustrated']
    const messageWords = message.toLowerCase().split(' ')
    const stressMatches = messageWords.filter((word: string) => 
      stressKeywords.some((keyword: string) => word.includes(keyword))
    )
    const baseStress = Math.min(Math.max(stressMatches.length + 3, 1), 10)

    const getStressColor = (level: number) => level >= 8 ? 'red' : level >= 6 ? 'orange' : level >= 4 ? 'yellow' : 'green'
    const getStressLabel = (level: number) => level >= 9 ? 'Crisis' : level >= 7 ? 'High Stress' : level >= 5 ? 'Moderate' : level >= 3 ? 'Low Stress' : 'Calm'
    const getStressAnimation = (level: number) => level >= 8 ? 'warning-pulse' : level >= 6 ? 'pulse-stress' : level >= 4 ? 'heartbeat' : 'none'

    // Store conversation
    conversationHistory.push({
      message, response: aiResponse, stress_level: baseStress, timestamp: new Date().toISOString()
    })

    const trend = conversationHistory.length > 1 ? 
      (baseStress > conversationHistory[conversationHistory.length - 2].stress_level ? 'increasing' : 
       baseStress < conversationHistory[conversationHistory.length - 2].stress_level ? 'decreasing' : 'stable') : 'stable'

    res.status(200).json({
      status: 'success',
      response: aiResponse,
      emotion_analysis: {
        primary_emotion: stressMatches.length > 0 ? 'anxious' : 'neutral',
        stress_level: baseStress,
        emotion_intensity: 0.5 + (baseStress / 20),
        risk_assessment: baseStress >= 8 ? 'high' : 'low',
        psychological_markers: stressMatches
      },
      stress_meter: {
        current: baseStress,
        percentage: (baseStress / 10) * 100,
        color: getStressColor(baseStress),
        label: getStressLabel(baseStress),
        animation: getStressAnimation(baseStress),
        trend
      },
      therapeutic_insights: {
        approach: 'Supportive',
        coping_suggestion: 'Take things one moment at a time',
        is_crisis: baseStress >= 8
      },
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({
      status: 'error',
      response: 'I apologize for the technical difficulty.',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
