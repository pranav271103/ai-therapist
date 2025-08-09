import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Brain, AlertTriangle, Heart, BarChart3 } from 'lucide-react';
import LiveStressMeter, { StressMeterData, ColorKey, getColorFromLevel } from '../components/LiveStressMeter';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  emotionData?: {
    primary_emotion: string;
    stress_level: number;
    emotion_intensity: number;
    risk_assessment: string;
    psychological_markers: string[];
  };
}

interface APIResponse {
  status: string;
  response: string;
  emotion_analysis: {
    primary_emotion: string;
    stress_level: number;
    emotion_intensity: number;
    risk_assessment: string;
    psychological_markers: string[];
  };
  stress_meter: {
    current: number;
    percentage: number;
    color: string;
    label: string;
    animation: string;
    trend: string;
  };
  therapeutic_insights: {
    approach: string;
    coping_suggestion: string;
    is_crisis: boolean;
  };
  timestamp: string;
}

export default function TherapistChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stressMeter, setStressMeter] = useState<StressMeterData | null>(null);
  const [showCrisisAlert, setShowCrisisAlert] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Helper function to create properly typed StressMeterData
  const createStressMeterData = (stress: number, trend: string = 'stable'): StressMeterData => {
    const color: ColorKey = getColorFromLevel(stress);
    const label = stress >= 9 ? 'Crisis' : 
                  stress >= 7 ? 'High Stress' : 
                  stress >= 5 ? 'Moderate' : 
                  stress >= 3 ? 'Low Stress' : 'Calm';
    
    const animation = stress >= 8 ? 'warning-pulse' : 
                     stress >= 6 ? 'pulse-stress' : 
                     stress >= 4 ? 'heartbeat' : 'none';
    
    const validTrend = (trend === 'increasing' || trend === 'decreasing') ? trend : 'stable';

    return {
      current: stress,
      percentage: (stress / 10) * 100,
      color,
      label,
      animation: animation as any,
      trend: validTrend
    };
  };

  useEffect(() => {
    // Check backend connection
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setIsConnected(true);
          // Initialize stress meter with baseline
          setStressMeter(createStressMeterData(5, 'stable'));
        }
      })
      .catch(err => {
        console.error('Backend connection failed:', err);
        setIsConnected(false);
      });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll stress monitor for real-time updates
  useEffect(() => {
    if (!isConnected) return;
    
    const pollStress = () => {
      fetch('/api/stress-monitor')
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            setStressMeter(createStressMeterData(data.current_stress, data.trend));
          }
        })
        .catch(console.error);
    };

    const interval = setInterval(pollStress, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [isConnected]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputValue }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: APIResponse = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || 'I apologize, but I\'m having trouble responding right now.',
        sender: 'ai',
        timestamp: new Date(),
        emotionData: data.emotion_analysis,
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Update live stress meter with proper typing
      if (data.stress_meter) {
        const stressMeterData = createStressMeterData(
          data.stress_meter.current, 
          data.stress_meter.trend
        );
        setStressMeter(stressMeterData);
        
        if (data.therapeutic_insights?.is_crisis) {
          setShowCrisisAlert(true);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'I\'m experiencing technical difficulties. Please try again in a moment.',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Connection Status */}
      {!isConnected && (
        <div className="fixed top-4 right-4 bg-red-500/90 text-white px-4 py-2 rounded-lg shadow-lg z-50">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm">Connecting to AI...</span>
          </div>
        </div>
      )}

      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-700"></div>
      </div>

      {/* Main Interface */}
      <div className="relative z-10 flex flex-col h-screen">
        {/* Header with Live Stress Meter */}
        <motion.header 
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="backdrop-blur-xl bg-white/10 border-b border-white/20 p-4"
        >
          <div className="max-w-6xl mx-auto">
            {/* Top Row */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <motion.div 
                  className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-500 rounded-2xl flex items-center justify-center shadow-xl"
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Brain className="w-6 h-6 text-white" />
                </motion.div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                    Dr. HelAI
                  </h1>
                  <p className="text-sm text-white/70 flex items-center">
                    AI Therapeutic Assistant
                    {isConnected && <span className="ml-2 w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>}
                  </p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex space-x-2">
                <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg backdrop-blur-sm transition-colors">
                  <BarChart3 className="w-5 h-5 text-white" />
                </button>
                {stressMeter && stressMeter.current >= 7 && (
                  <motion.button
                    className="p-2 bg-red-500/80 hover:bg-red-500 rounded-lg backdrop-blur-sm transition-colors"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                  >
                    <Heart className="w-5 h-5 text-white" />
                  </motion.button>
                )}
              </div>
            </div>

            {/* Live Stress Meter */}
            <div className="w-full">
              <LiveStressMeter 
                stressMeter={stressMeter} 
                isActive={isLoading} 
                showDetails={true} 
              />
            </div>
          </div>
        </motion.header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center text-white/70 py-12"
              >
                <Brain className="w-16 h-16 mx-auto mb-4 text-white/50" />
                <h2 className="text-2xl font-bold mb-2">Welcome to Dr. HelAI</h2>
                <p className="text-lg mb-4">I'm here to provide professional therapeutic support with live stress monitoring.</p>
                <p className="text-sm">Share what's on your mind, and watch the stress meter respond in real-time.</p>
              </motion.div>
            )}

            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-6`}
                >
                  <div className={`max-w-xs lg:max-w-lg px-6 py-4 rounded-3xl shadow-xl ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : 'bg-white/20 backdrop-blur-lg text-white border border-white/30'
                  }`}>
                    <p className="text-sm leading-relaxed">{message.text}</p>
                    
                    {message.sender === 'user' && message.emotionData && (
                      <div className="mt-3 pt-3 border-t border-white/20">
                        <div className="flex justify-between items-center text-xs">
                          <span className="opacity-75">
                            Emotion: {message.emotionData.primary_emotion}
                          </span>
                          <span className="opacity-75">
                            Stress: {message.emotionData.stress_level}/10
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start mb-6"
              >
                <div className="bg-white/20 backdrop-blur-lg rounded-3xl px-6 py-4 shadow-xl">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <motion.div 
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="backdrop-blur-xl bg-white/10 border-t border-white/20 p-6"
        >
          <div className="max-w-4xl mx-auto flex space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Share what's on your mind..."
                className="w-full bg-white/20 backdrop-blur-lg border border-white/30 rounded-2xl px-6 py-4 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                disabled={isLoading || !isConnected}
              />
            </div>
            <motion.button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading || !isConnected}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 rounded-2xl px-8 py-4 text-white font-medium shadow-xl transition-all"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </motion.div>
      </div>

      {/* Crisis Alert Modal */}
      <AnimatePresence>
        {showCrisisAlert && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          >
            <div className="bg-red-500 text-white p-6 rounded-2xl max-w-md mx-auto shadow-2xl">
              <div className="flex items-center space-x-3 mb-4">
                <Heart className="w-6 h-6" />
                <h3 className="text-lg font-bold">High Stress Detected</h3>
              </div>
              <p className="mb-4">Your stress level indicates you need immediate support.</p>
              <div className="space-y-2">
                <button className="w-full bg-white/20 hover:bg-white/30 py-2 px-4 rounded-lg transition-colors">
                  🫁 Start Breathing Exercise
                </button>
                <button className="w-full bg-white/20 hover:bg-white/30 py-2 px-4 rounded-lg transition-colors">
                  📞 Crisis Hotline: 988
                </button>
                <button 
                  onClick={() => setShowCrisisAlert(false)}
                  className="w-full bg-white/20 hover:bg-white/30 py-2 px-4 rounded-lg transition-colors"
                >
                  Continue Session
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
