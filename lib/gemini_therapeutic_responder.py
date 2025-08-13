# gemini_therapeutic_responder.py (FINAL VERSION)
import google.generativeai as genai
import json
import random
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiTherapeuticResponder:
    def __init__(self, model_name='gemini-1.5-flash-latest'):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        # Stress level descriptors
        self.stress_levels = {
            0: "Very Relaxed", 1: "Calm", 2: "Slightly Tense", 3: "Mildly Stressed",
            4: "Moderately Stressed", 5: "Stressed", 6: "Quite Stressed", 
            7: "Highly Stressed", 8: "Very Stressed", 9: "Extremely Stressed", 10: "Crisis Level"
        }
    
    def generate_therapeutic_response(self, emotion_data: Dict, user_input: str, 
                                    conversation_history: List = None) -> Dict:
        """Generate therapeutic response using Gemini Flash Latest"""
        
        # Simplified therapeutic prompting for Flash model
        therapeutic_prompt = f"""You are Dr. Sarah Chen, a warm and professional clinical psychologist.

PATIENT ASSESSMENT:
- Emotion: {emotion_data.get('primary_emotion', 'neutral')}
- Stress Level: {emotion_data.get('stress_level', 5)}/10
- Risk Level: {emotion_data.get('risk_assessment', 'low')}
- Message: "{user_input}"

Provide a caring, professional therapeutic response. Be empathetic and ask ONE relevant follow-up question.

If stress level is 8+, include a coping technique.
If risk is high/crisis, mention support resources.

Keep response 2-3 sentences plus one question."""

        try:
            response = self.model.generate_content(therapeutic_prompt)
            
            if response.text:
                therapeutic_response = response.text.strip()
                
                return {
                    'response': therapeutic_response,
                    'stress_interpretation': self.interpret_stress_level(emotion_data.get('stress_level', 5)),
                    'coping_suggestion': self.get_coping_suggestion(emotion_data.get('stress_level', 5)),
                    'therapeutic_approach': self.determine_approach(emotion_data),
                    'crisis_resources': self.get_crisis_resources() if emotion_data.get('risk_assessment') in ['high', 'crisis'] else None,
                    'generated_by': 'gemini_flash_latest',
                    'therapist_persona': 'Dr. Sarah Chen - Clinical Psychologist'
                }
            else:
                return self.fallback_response(emotion_data, user_input)
                
        except Exception as e:
            print(f"Gemini response error: {e}")
            return self.fallback_response(emotion_data, user_input)
    
    def interpret_stress_level(self, stress_level: int) -> str:
        """Provide detailed stress level interpretation"""
        stress_level = int(stress_level)  # Ensure it's an integer
        
        if stress_level <= 2:
            return "Your stress level is very manageable, which is excellent for your well-being."
        elif stress_level <= 4:
            return "You're experiencing mild stress, which is normal and can be motivating."
        elif stress_level <= 6:
            return "Your stress level is moderate. This is a good time to focus on stress management."
        elif stress_level <= 8:
            return "You're dealing with high stress levels that need active attention."
        else:
            return "Your stress level is extremely high and requires immediate support."
    
    def get_coping_suggestion(self, stress_level: int) -> str:
        """Provide appropriate coping suggestions"""
        stress_level = int(stress_level)  # Ensure it's an integer
        
        if stress_level >= 8:
            return "Try the 4-7-8 breathing technique: Inhale for 4, hold for 7, exhale for 8. Repeat 4 times."
        elif stress_level >= 6:
            return "Consider taking a 10-minute break for deep breathing or gentle stretching."
        elif stress_level >= 4:
            return "A short walk or listening to calming music might help you reset."
        else:
            return "Continue with your positive coping strategies and maintain this balance."
    
    def determine_approach(self, emotion_data: Dict) -> str:
        """Determine therapeutic approach"""
        stress_level = int(emotion_data.get('stress_level', 5))
        risk_level = emotion_data.get('risk_assessment', 'low')
        
        if risk_level in ['high', 'crisis']:
            return 'Crisis intervention and safety planning'
        elif stress_level >= 8:
            return 'Immediate stress reduction and grounding'
        elif stress_level >= 6:
            return 'Stress management and coping skills'
        else:
            return 'Supportive therapy and resilience building'
    
    def get_crisis_resources(self) -> Dict:
        """Crisis intervention resources"""
        return {
            'immediate_help': [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Emergency Services: 911"
            ],
            'safety_message': "You are not alone. Professional help is available 24/7."
        }
    
    def fallback_response(self, emotion_data: Dict, user_input: str) -> Dict:
        """Fallback response if Gemini fails"""
        stress_level = int(emotion_data.get('stress_level', 5))
        
        if stress_level >= 8:
            response = "I can sense you're dealing with significant stress right now. That must feel overwhelming. I'm here to support you through this. What feels most urgent to address?"
        elif stress_level >= 6:
            response = "It sounds like you're experiencing quite a bit of stress. That can be really challenging. What's been weighing on your mind the most?"
        else:
            response = "I'm here to listen and support you. Thank you for sharing with me. What would be most helpful to explore together?"
        
        return {
            'response': response,
            'stress_interpretation': self.interpret_stress_level(stress_level),
            'coping_suggestion': self.get_coping_suggestion(stress_level),
            'therapeutic_approach': 'Supportive therapy',
            'crisis_resources': None,
            'generated_by': 'fallback_professional',
            'therapist_persona': 'Dr. Sarah Chen - Fallback Mode'
        }

if __name__ == "__main__":
    responder = GeminiTherapeuticResponder()
    test_emotion = {
        'primary_emotion': 'anxiety',
        'stress_level': 8,
        'emotion_intensity': 0.9,
        'therapeutic_priority': 'high',
        'risk_assessment': 'medium'
    }
    result = responder.generate_therapeutic_response(test_emotion, "I feel like everything is falling apart")
    print(json.dumps(result, indent=2))
