import type { NextApiRequest, NextApiResponse } from 'next'

// Simple in-memory storage for demo
let conversationHistory: any[] = []

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('Chat API called:', req.method)
  
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
    console.log('Request body:', req.body)
    
    const { message } = req.body

    if (!message || !message.trim()) {
      console.log('Empty message received')
      res.status(400).json({ error: 'Empty message' })
      return
    }

    console.log('Processing message:', message)

    // Check environment variable
    const geminiApiKey = process.env.GEMINI_API_KEY
    console.log('API Key available:', !!geminiApiKey)
    
    if (!geminiApiKey) {
      console.error('GEMINI_API_KEY not found in environment')
      throw new Error('GEMINI_API_KEY not configured')
    }

    // Prepare Gemini API request
    const geminiPayload = {
      contents: [{
        parts: [{
          text: `You are Dr. HelAI, a professional AI therapeutic assistant. Please provide a supportive, empathetic response to this message. Keep your response concise and therapeutic: "${message}"`
        }]
      }]
    }

    console.log('Calling Gemini API...')

    // Call Google Gemini API with better error handling
    const geminiResponse = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${geminiApiKey}`,
      {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(geminiPayload)
      }
    )

    console.log('Gemini API response status:', geminiResponse.status)

    if (!geminiResponse.ok) {
      const errorText = await geminiResponse.text()
      console.error('Gemini API error:', geminiResponse.status, errorText)
      throw new Error(`Gemini API error: ${geminiResponse.status} - ${errorText}`)
    }

    const geminiData = await geminiResponse.json()
    console.log('Gemini API response received')
    
    const aiResponse = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || 
                      'I hear you and I\'m here to support you. Thank you for sharing with me.'

    // Simple stress level estimation
    const stressKeywords: string[] = ['stressed', 'anxious', 'worried', 'panic', 'overwhelmed', 'crisis', 'depressed', 'sad', 'angry', 'frustrated']
    const messageWords: string[] = message.toLowerCase().split(' ')
    const stressMatches = messageWords.filter((word: string) => 
      stressKeywords.some((keyword: string) => word.includes(keyword))
    )
    const baseStress = Math.min(Math.max(stressMatches.length + 3, 1), 10)
    
    // Determine emotion
    const primaryEmotion = stressMatches.length > 0 ? 'anxious' : 'neutral'

    // Helper functions for stress meter
    const getStressColor = (level: number): string => {
      if (level >= 8) return 'red'
      if (level >= 6) return 'orange'
      if (level >= 4) return 'yellow'
      return 'green'
    }

    const getStressAnimation = (level: number): string => {
      if (level >= 8) return 'warning-pulse'
      if (level >= 6) return 'pulse-stress'
      if (level >= 4) return 'heartbeat'
      return 'none'
    }

    const getStressLabel = (level: number): string => {
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
        coping_suggestion: baseStress >= 7 ? 'Consider taking some deep breaths and grounding yourself' : 'Continue sharing your thoughts',
        is_crisis: baseStress >= 8
      },
      timestamp: new Date().toISOString()
    }

    console.log('Sending successful response')
    res.status(200).json(responseData)

  } catch (error) {
    console.error('Chat API Error Details:', error)
    
    // Provide a detailed error response
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    
    res.status(500).json({
      status: 'error',
      response: 'I apologize for the technical difficulty. I\'m still here to support you.',
      emotion_analysis: {
        primary_emotion: 'neutral',
        stress_level: 5,
        emotion_intensity: 0.5,
        risk_assessment: 'low',
        psychological_markers: []
      },
      stress_meter: {
        current: 5,
        percentage: 50,
        color: 'yellow',
        label: 'Error State',
        animation: 'none',
        trend: 'stable'
      },
      therapeutic_insights: {
        approach: 'Supportive',
        coping_suggestion: 'Please try again in a moment',
        is_crisis: false
      },
      timestamp: new Date().toISOString(),
      error: errorMessage,
      debug: {
        hasApiKey: !!process.env.GEMINI_API_KEY,
        nodeEnv: process.env.NODE_ENV
      }
    })
  }
}
