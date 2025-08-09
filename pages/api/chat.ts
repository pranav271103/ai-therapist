import type { NextApiRequest, NextApiResponse } from 'next'

// Simple in-memory storage for demo (replace with database in production)
let conversationHistory: any[] = []
let sessionCount = 0

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
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

    // Simulate AI processing with Google Gemini
    const geminiApiKey = process.env.GEMINI_API_KEY
    
    if (!geminiApiKey) {
      throw new Error('GEMINI_API_KEY not configured')
    }

    // Call Google Gemini API
    const geminiResponse = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + geminiApiKey, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `You are Dr. HelAI, a professional AI therapeutic assistant. Analyze this message for emotional content and stress level (1-10), then provide a supportive therapeutic response: "${message}"`
          }]
        }]
      })
    })

    if (!geminiResponse.ok) {
      throw new Error(`Gemini API error: ${geminiResponse.status}`)
    }

    const geminiData = await geminiResponse.json()
    const aiResponse = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || 'I hear you and I\'m here to support you.'

    // Simple stress level estimation (replace with your complex logic)
    const stressKeywords = ['stressed', 'anxious', 'worried', 'panic', 'overwhelmed', 'crisis', 'depressed', 'sad', 'angry', 'frustrated']
    const messageWords = message.toLowerCase().split(' ')
    const stressMatches = messageWords.filter(word => stressKeywords.some(keyword => word.includes(keyword)))
    const baseStress = Math.min(Math.max(stressMatches.length + 3, 1), 10)
    
    // Simulate emotion analysis
    const emotions = ['neutral', 'happy', 'sad', 'anxious', 'angry', 'frustrated', 'hopeful']
    const primaryEmotion = stressMatches.length > 0 ? 'anxious' : emotions[Math.floor(Math.random() * emotions.length)]

    // Helper functions for stress meter
    const getStressColor = (level: number) => {
      if (level >= 8) return 'red'
      if (level >= 6) return 'orange'
      if (level >= 4) return 'yellow'
      return 'green'
    }

    const getStressAnimation = (level: number) => {
      if (level >= 8) return 'warning-pulse'
      if (level >= 6) return 'pulse-stress'
      if (level >= 4) return 'heartbeat'
      return 'none'
    }

    const getStressLabel = (level: number) => {
      if (level >= 9) return 'Crisis'
      if (level >= 7) return 'High Stress'
      if (level >= 5) return 'Moderate'
      if (level >= 3) return 'Low Stress'
      return 'Calm'
    }

    // Store conversation
    const conversation = {
      message,
      response: aiResponse,
      stress_level: baseStress,
      primary_emotion: primaryEmotion,
      timestamp: new Date().toISOString()
    }
    conversationHistory.push(conversation)
    sessionCount++

    // Calculate trend
    let trend = 'stable'
    if (conversationHistory.length > 1) {
      const prevStress = conversationHistory[conversationHistory.length - 2].stress_level
      if (baseStress > prevStress) trend = 'increasing'
      else if (baseStress < prevStress) trend = 'decreasing'
    }

    const responseData = {
      status: 'success',
      response: aiResponse,
      emotion_analysis: {
        primary_emotion: primaryEmotion,
        stress_level: baseStress,
        emotion_intensity: 0.5 + (baseStress / 20),
        risk_assessment: baseStress >= 8 ? 'high' : baseStress >= 6 ? 'moderate' : 'low',
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
        coping_suggestion: baseStress >= 7 ? 'Consider deep breathing exercises' : 'Continue sharing your thoughts',
        is_crisis: baseStress >= 8
      },
      timestamp: new Date().toISOString()
    }

    res.status(200).json(responseData)
  } catch (error) {
    console.error('Chat API Error:', error)
    
    res.status(500).json({
      status: 'error',
      response: 'I apologize for the technical difficulty. I\'m still here to support you.',
      stress_meter: {
        current: 5,
        percentage: 50,
        color: 'yellow',
        label: 'Error State',
        animation: 'none',
        trend: 'stable'
      },
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
