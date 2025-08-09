import type { NextApiRequest, NextApiResponse } from 'next'

let conversationHistory: any[] = []

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

    // Get the Gemini API key
    const geminiApiKey = process.env.GEMINI_API_KEY
    
    let aiResponse = ''

    if (geminiApiKey) {
      try {
        // Create a more personalized therapeutic prompt
        const therapeuticPrompt = `You are Dr. HelAI, a compassionate and professional AI therapist. The user just said: "${message}"

Please provide a personalized, empathetic, and therapeutically appropriate response that:
- Acknowledges their specific concern
- Validates their feelings
- Offers gentle guidance or insight
- Asks a thoughtful follow-up question when appropriate
- Keeps the response concise (2-3 sentences)
- Uses a warm, professional tone

Respond as if you're having a real therapeutic conversation, not giving generic advice.`

        // Call Gemini AI
        const geminiResponse = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${geminiApiKey}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [{ text: therapeuticPrompt }]
              }]
            })
          }
        )

        if (geminiResponse.ok) {
          const geminiData = await geminiResponse.json()
          aiResponse = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || ''
        }
      } catch (error) {
        console.error('Gemini API error:', error)
      }
    }

    // Fallback to personalized responses if Gemini fails
    if (!aiResponse) {
      // Create more contextual responses based on the message content
      const lowerMessage = message.toLowerCase()
      
      if (lowerMessage.includes('stress')) {
        aiResponse = `I hear that you're experiencing stress right now. Stress can feel overwhelming, but you've taken an important step by reaching out. What's been the main source of your stress lately?`
      } else if (lowerMessage.includes('anxious') || lowerMessage.includes('anxiety')) {
        aiResponse = `Thank you for sharing about your anxiety with me. It takes courage to acknowledge these feelings. Can you tell me more about what's making you feel anxious today?`
      } else if (lowerMessage.includes('sad') || lowerMessage.includes('depressed')) {
        aiResponse = `I'm sorry you're feeling this way. Your sadness is valid, and I'm here to listen. Sometimes talking about what's weighing on us can help lighten the load. What's been on your mind?`
      } else if (lowerMessage.includes('angry') || lowerMessage.includes('frustrated')) {
        aiResponse = `I can sense your frustration, and those feelings are completely understandable. Anger often tells us something important about our boundaries or needs. What's been triggering these feelings for you?`
      } else if (lowerMessage.includes('help') || lowerMessage.includes('support')) {
        aiResponse = `I'm here to support you in whatever way I can. You've already shown strength by asking for help. What kind of support would feel most helpful to you right now?`
      } else {
        // More varied generic responses
        const contextualResponses = [
          `Thank you for sharing that with me. I can sense there's something important behind your words. Can you tell me more about what's going on?`,
          `I appreciate you opening up to me. Your feelings and experiences matter. What's been weighing on your mind lately?`,
          `I hear you, and I want you to know that this is a safe space for you to express yourself. What would feel most supportive right now?`,
          `It sounds like you have something on your heart. I'm here to listen without judgment. What's been your experience with this?`
        ]
        aiResponse = contextualResponses[Math.floor(Math.random() * contextualResponses.length)]
      }
    }

    // Analyze stress level based on message content
    const stressKeywords = ['stress', 'stressed', 'anxious', 'worried', 'panic', 'overwhelmed', 'crisis', 'depressed', 'sad', 'angry', 'frustrated', 'exhausted', 'hopeless']
    const messageWords = message.toLowerCase().split(' ')
    const stressMatches = messageWords.filter((word: string) => 
      stressKeywords.some((keyword: string) => word.includes(keyword))
    )
    
    // More sophisticated stress calculation
    let baseStress = 5 // baseline
    if (stressMatches.length > 0) {
      baseStress = Math.min(Math.max(stressMatches.length * 2 + 4, 1), 10)
    }
    
    // Adjust based on specific keywords
    if (message.toLowerCase().includes('crisis') || message.toLowerCase().includes('suicide')) {
      baseStress = 10
    } else if (message.toLowerCase().includes('panic') || message.toLowerCase().includes('overwhelmed')) {
      baseStress = Math.max(baseStress, 8)
    }

    const getStressColor = (level: number) => level >= 8 ? 'red' : level >= 6 ? 'orange' : level >= 4 ? 'yellow' : 'green'
    const getStressLabel = (level: number) => level >= 9 ? 'Crisis' : level >= 7 ? 'High Stress' : level >= 5 ? 'Moderate' : level >= 3 ? 'Low Stress' : 'Calm'
    const getStressAnimation = (level: number) => level >= 8 ? 'warning-pulse' : level >= 6 ? 'pulse-stress' : level >= 4 ? 'heartbeat' : 'none'

    // Store conversation
    conversationHistory.push({
      message, 
      response: aiResponse, 
      stress_level: baseStress, 
      timestamp: new Date().toISOString()
    })

    // Calculate trend
    let trend = 'stable'
    if (conversationHistory.length > 1) {
      const prevStress = conversationHistory[conversationHistory.length - 2].stress_level
      if (baseStress > prevStress) trend = 'increasing'
      else if (baseStress < prevStress) trend = 'decreasing'
    }

    res.status(200).json({
      status: 'success',
      response: aiResponse,
      emotion_analysis: {
        primary_emotion: stressMatches.length > 0 ? 'anxious' : 'neutral',
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
        coping_suggestion: baseStress >= 7 ? 'Consider taking some deep breaths and grounding yourself' : 'Continue sharing your thoughts and feelings',
        is_crisis: baseStress >= 9
      },
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Chat API Error:', error)
    res.status(500).json({
      status: 'error',
      response: 'I apologize for the technical difficulty. I\'m still here to support you.',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
