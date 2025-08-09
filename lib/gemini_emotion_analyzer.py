# gemini_emotion_analyzer.py (FINAL VERSION)
import google.generativeai as genai
import json
import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiEmotionAnalyzer:
    def __init__(self, model_name='gemini-1.5-flash-latest'):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDTQRNQ2zF2cEQSmX7QFmrVX3etnt6rGoc')
        genai.configure(api_key=api_key)
        
        # Initialize Gemini 1.5 Flash Latest model
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        """Test Gemini API connection"""
        try:
            response = self.model.generate_content("Hello, respond with 'Connected!'")
            if response.text:
                print(f"Connected to Google {self.model_name}")
                return True
        except Exception as e:
            print(f"Gemini connection failed: {e}")
            return False
    
    def analyze_emotion_with_gemini(self, text: str, conversation_history: List = None) -> Dict:
        """Advanced emotion analysis using Gemini with psychological expertise"""
        
        # Build context from conversation history
        context = ""
        if conversation_history and len(conversation_history) > 0:
            recent_context = conversation_history[-3:]
            context = "\n".join([
                f"Previous: '{entry.get('context', entry.get('user_input', ''))}' -> Emotion: {entry.get('primary_emotion', 'unknown')}, Stress: {entry.get('stress_level', 5)}"
                for entry in recent_context
            ])
        
        # Simplified but effective psychological prompting for Flash model
        prompt = f"""You are an expert clinical psychologist. Analyze this message for emotional and psychological content.

CONTEXT: {context if context else "First conversation"}

MESSAGE: "{text}"

Respond with ONLY this JSON format (no extra text):
{{
    "primary_emotion": "joy|sadness|anger|fear|anxiety|disgust|surprise|neutral",
    "emotion_intensity": 0.8,
    "stress_level": 7,
    "sentiment_score": -0.3,
    "psychological_markers": ["anxiety", "overwhelm"],
    "stress_triggers": ["work", "deadline"],
    "therapeutic_priority": "high",
    "risk_assessment": "medium",
    "follow_up_questions": ["What's causing the most stress?", "How are you coping?"]
}}

Focus on psychological accuracy and therapeutic relevance."""

        try:
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Parse JSON response
                try:
                    # Clean up the response text
                    json_text = response.text.strip()
                    
                    # Remove markdown formatting if present
                    if json_text.startswith('```json'):
                        json_text = json_text.replace('```json', '').replace('```', '')
                    elif json_text.startswith('```'):
                        json_text = json_text.replace('```', '')
                    
                    # Parse JSON
                    emotion_data = json.loads(json_text)
                    
                    # Ensure required keys exist
                    required_keys = {
                        'primary_emotion': 'neutral',
                        'emotion_intensity': 0.5,
                        'stress_level': 5,
                        'sentiment_score': 0.0,
                        'psychological_markers': [],
                        'stress_triggers': [],
                        'therapeutic_priority': 'medium',
                        'risk_assessment': 'low',
                        'follow_up_questions': ["How are you feeling?"]
                    }
                    
                    for key, default_value in required_keys.items():
                        if key not in emotion_data:
                            emotion_data[key] = default_value
                    
                    # Add metadata
                    emotion_data['timestamp'] = datetime.datetime.now().isoformat()
                    emotion_data['text'] = text
                    emotion_data['ai_model'] = self.model_name
                    emotion_data['analysis_method'] = 'gemini_flash_latest'
                    
                    return emotion_data
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Raw response: {response.text[:200]}...")
                    return self.fallback_emotion_analysis(text, response.text)
            else:
                print("Empty response from Gemini")
                return self.fallback_emotion_analysis(text)
                
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return self.fallback_emotion_analysis(text)
    
    def fallback_emotion_analysis(self, text: str, gemini_response: str = "") -> Dict:
        """Enhanced fallback analysis if Gemini fails"""
        
        # Advanced keyword analysis
        emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'fantastic'],
            'sadness': ['sad', 'depressed', 'down', 'lonely', 'hopeless', 'crying', 'hurt'],
            'anger': ['angry', 'mad', 'furious', 'frustrated', 'hate', 'rage', 'irritated'],
            'anxiety': ['worried', 'anxious', 'nervous', 'scared', 'panic', 'overwhelmed', 'stressed'],
        }
        
        stress_indicators = {
            'extreme': ['suicidal', 'kill myself', 'end it all', 'can\'t go on'],
            'very_high': ['overwhelmed', 'breaking point', 'can\'t handle', 'too much'],
            'high': ['stressed', 'pressure', 'deadline', 'exhausted', 'burnt out'],
            'medium': ['busy', 'hectic', 'tired', 'worried', 'concerned'],
            'low': ['calm', 'peaceful', 'relaxed', 'comfortable', 'fine']
        }
        
        text_lower = text.lower()
        
        # Detect emotions - FIXED: Properly handle empty emotion_scores
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # FIXED: Properly handle empty emotion_scores
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            emotion_intensity = min(1.0, max(emotion_scores.values()) * 0.3)
        else:
            primary_emotion = 'neutral'
            emotion_intensity = 0.4
        
        # Assess stress level
        stress_level = 4  # baseline
        
        for level, indicators in stress_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text_lower)
            if count > 0:
                if level == 'extreme':
                    stress_level = 10
                elif level == 'very_high':
                    stress_level = 8
                elif level == 'high':
                    stress_level = 7
                elif level == 'medium':
                    stress_level = 5
                elif level == 'low':
                    stress_level = 2
                break
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_intensity': emotion_intensity,
            'stress_level': stress_level,
            'sentiment_score': -0.6 if primary_emotion in ['sadness', 'anger'] else 0.6 if primary_emotion == 'joy' else 0.0,
            'psychological_markers': [primary_emotion] if primary_emotion != 'neutral' else ['stable'],
            'stress_triggers': [indicator for indicators in stress_indicators.values() for indicator in indicators if indicator in text_lower],
            'therapeutic_priority': 'high' if stress_level >= 8 else 'medium' if stress_level >= 5 else 'low',
            'risk_assessment': 'high' if stress_level >= 9 else 'medium' if stress_level >= 6 else 'low',
            'follow_up_questions': [
                "What's been weighing on your mind?",
                "How are you taking care of yourself?",
                "What would feel most helpful right now?"
            ],
            'timestamp': datetime.datetime.now().isoformat(),
            'text': text,
            'ai_model': 'fallback_advanced',
            'analysis_method': 'keyword_psychological'
        }

if __name__ == "__main__":
    analyzer = GeminiEmotionAnalyzer()
    test_text = "I'm feeling really overwhelmed with work and I can't seem to catch up. Everything feels like too much."
    result = analyzer.analyze_emotion_with_gemini(test_text)
    print(json.dumps(result, indent=2))
