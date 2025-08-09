# gemini_ai_therapist.py (FINAL VERSION)
from gemini_emotion_analyzer import GeminiEmotionAnalyzer
from gemini_therapeutic_responder import GeminiTherapeuticResponder
from memory_manager import SimpleMemoryManager
import json
from typing import Dict
from datetime import datetime
import sys

class GeminiAITherapist:
    def __init__(self):
        print("Initializing AI Therapist with Google Gemini 1.5 Flash Latest...")
        
        try:
            self.emotion_analyzer = GeminiEmotionAnalyzer()  # Uses gemini-1.5-flash-latest by default
            self.responder = GeminiTherapeuticResponder()   # Uses gemini-1.5-flash-latest by default
            self.memory_manager = SimpleMemoryManager("gemini_user")
            print("All Gemini components initialized successfully")
        except Exception as e:
            print(f"Error during initialization: {e}")
            sys.exit(1)
        
        self.session_stats = {
            'session_start': datetime.now(),
            'exchanges': 0,
            'crisis_interventions': 0,
            'avg_stress_level': 0
        }
    
    def get_safe_intensity(self, data):
        """Safely extract intensity value from emotion data"""
        return data.get('emotion_intensity') or data.get('intensity') or 0.5
    
    def process_therapeutic_conversation(self, user_input: str):
        """Process conversation with Gemini Flash Latest"""
        print("\nAnalyzing with Gemini 1.5 Flash Latest...")
        
        try:
            # Get conversation history for context
            conversation_history = self.memory_manager.conversations[-5:] if self.memory_manager.conversations else []
            
            # Advanced emotion analysis with Gemini
            emotion_data = self.emotion_analyzer.analyze_emotion_with_gemini(user_input, conversation_history)
            
            # DEBUG: Verify we have required keys (can be removed in production)
            # print(f"Debug - Keys received: {list(emotion_data.keys())}")
            
            # Ensure required keys exist with safe defaults
            safe_emotion_data = {
                'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
                'emotion_intensity': self.get_safe_intensity(emotion_data),
                'stress_level': int(emotion_data.get('stress_level', 5)),
                'sentiment_score': emotion_data.get('sentiment_score', 0.0),
                'psychological_markers': emotion_data.get('psychological_markers', []),
                'stress_triggers': emotion_data.get('stress_triggers', []),
                'therapeutic_priority': emotion_data.get('therapeutic_priority', 'medium'),
                'risk_assessment': emotion_data.get('risk_assessment', 'low'),
                'follow_up_questions': emotion_data.get('follow_up_questions', []),
                'timestamp': emotion_data.get('timestamp', datetime.now().isoformat()),
                'text': emotion_data.get('text', user_input),
                'ai_model': emotion_data.get('ai_model', 'gemini-1.5-flash-latest'),
                'analysis_method': emotion_data.get('analysis_method', 'unknown')
            }
            
            # Store in memory
            self.memory_manager.store_emotion(safe_emotion_data, user_input)
            
            # Generate therapeutic response
            response_data = self.responder.generate_therapeutic_response(
                safe_emotion_data, user_input, conversation_history
            )
            
            # Update session statistics
            self.update_session_stats(safe_emotion_data)
            
            # Display comprehensive therapeutic analysis
            self.display_therapeutic_analysis(safe_emotion_data, response_data)
            
        except Exception as e:
            print(f"Error in conversation processing: {e}")
            print(f"Using emergency fallback...")
            
            # Emergency fallback
            emergency_data = {
                'primary_emotion': 'neutral',
                'emotion_intensity': 0.5,
                'stress_level': 5,
                'risk_assessment': 'low',
                'ai_model': 'emergency_fallback',
                'psychological_markers': [],
                'stress_triggers': []
            }
            
            emergency_response = {
                'response': "I'm experiencing some technical difficulties, but I'm still here to listen. How are you feeling right now?",
                'therapeutic_approach': 'Supportive',
                'stress_interpretation': 'Unable to assess due to technical issues',
                'coping_suggestion': 'Take a deep breath and know that I\'m here to support you'
            }
            
            self.display_therapeutic_analysis(emergency_data, emergency_response)
    
    def display_therapeutic_analysis(self, emotion_data: Dict, response_data: Dict):
        """Display comprehensive therapeutic analysis"""
        
        try:
            # Extract key metrics with SAFE ACCESS
            primary_emotion = emotion_data.get('primary_emotion', 'neutral')
            stress_level = int(emotion_data.get('stress_level', 5))
            intensity = self.get_safe_intensity(emotion_data)
            risk_level = emotion_data.get('risk_assessment', 'low')
            
            # Stress visualization
            stress_bar = "█" * stress_level + "░" * (10 - stress_level)
            
            # Color coding
            if stress_level >= 9:
                stress_color = "🔴"
                status = "CRISIS - IMMEDIATE SUPPORT NEEDED"
            elif stress_level >= 7:
                stress_color = "🟠"
                status = "HIGH STRESS - ACTIVE INTERVENTION"
            elif stress_level >= 5:
                stress_color = "🟡"
                status = "MODERATE STRESS - COPING SUPPORT"
            else:
                stress_color = "🟢"
                status = "MANAGEABLE STRESS LEVELS"
            
            # Emotion emoji mapping
            emotion_emojis = {
                'joy': '😊', 'sadness': '😢', 'anger': '😠', 'anxiety': '😰',
                'fear': '😨', 'surprise': '😲', 'disgust': '🤢', 'neutral': '😐'
            }
            emotion_emoji = emotion_emojis.get(primary_emotion, '😐')
            
            print(f"\n GEMINI 1.5 FLASH ANALYSIS:")
            print(f"   {emotion_emoji} Primary Emotion: {primary_emotion.title()}")
            print(f"   Emotional Intensity: {intensity:.1f}/1.0")
            print(f"   {stress_color} Stress Level: {stress_level}/10 [{stress_bar}]")
            print(f"   Status: {status}")
            print(f"   Risk Assessment: {risk_level.upper()}")
            
            # Show key insights
            markers = emotion_data.get('psychological_markers', [])
            if markers and markers != ['stable']:
                print(f"   Psychological Markers: {', '.join(markers[:3])}")
            
            triggers = emotion_data.get('stress_triggers', [])
            if triggers:
                print(f"   Stress Triggers: {', '.join(triggers[:3])}")
            
            print(f"   AI Model: {emotion_data.get('ai_model', 'gemini-1.5-flash-latest')}")
            print(f"   Therapeutic Approach: {response_data.get('therapeutic_approach', 'Supportive')}")
            
            # Main therapeutic response
            print(f"\n Dr. HelAI")
            print(f"   {response_data.get('response', 'I hear you and I\'m here to support you.')}")
            
            # Stress management guidance
            if stress_level >= 7:
                print(f"\n IMMEDIATE STRESS RELIEF:")
                print(f"   {response_data.get('coping_suggestion', 'Focus on slow, deep breathing.')}")
            
            # Crisis resources if needed
            crisis_resources = response_data.get('crisis_resources')
            if crisis_resources:
                print(f"\nCRISIS SUPPORT RESOURCES:")
                for resource in crisis_resources.get('immediate_help', []):
                    print(f"   {resource}")
                print(f"   {crisis_resources.get('safety_message', 'Help is available.')}")
                
                # Count crisis interventions
                self.session_stats['crisis_interventions'] += 1
                
        except Exception as e:
            print(f"❌ Display error: {e}")
            print(f"📊 Basic Analysis: Emotion detected, processing...")
    
    def start_session(self):
        print("\n" + "="*75)
        print(" AI THERAPIST POWERED BY GOOGLE GEMINI 1.5 FLASH LATEST")
        print("   Professional-Grade Emotional Intelligence & Therapeutic Support")
        print("="*75)
        print("ADVANCED CAPABILITIES:")
        print("   -  Real-time psychological assessment with Gemini 1.5 Flash")
        print("   -  Professional therapeutic responses from Dr. HelAI")
        print("   -  Crisis detection and intervention protocols")
        print("   -  Comprehensive stress monitoring (0-10 scale)")
        print("   -  Long-term emotional pattern analysis")
        print("\n COMMANDS:")
        print("   -  'quit' - End session with summary")
        print("   -  'crisis' - Access crisis resources")
        print("   -  'stress' - View stress analysis")
        print("   -  'history' - Review emotional journey")
        print("   -  'help' - Show all commands")
        print("="*75)
        
        # Welcome message
        previous_sessions = len(self.memory_manager.conversations)
        if previous_sessions > 0:
            print(f"Welcome back! I have {previous_sessions} previous conversations.")
            recent_trend = self.get_recent_emotional_trend()
            print(f"Recent emotional trend: {recent_trend}")
        else:
            print("Welcome! I'm Dr. HelAI, powered by Gemini 1.5 Flash Latest.")
            print("This is our first session together. I'm here to provide professional therapeutic support.")
        
        while True:
            try:
                user_input = input("\n You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self.end_session()
                    break
                
                if user_input.lower() == 'crisis':
                    self.show_crisis_resources()
                    continue
                
                if user_input.lower() == 'stress':
                    self.show_stress_analysis()
                    continue
                
                if user_input.lower() == 'history':
                    self.show_emotional_history()
                    continue
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    print("I'm here when you're ready to share. Take your time.")
                    continue
                
                # Process the therapeutic conversation
                self.process_therapeutic_conversation(user_input)
                self.session_stats['exchanges'] += 1
                
            except KeyboardInterrupt:
                print("\n\n Session interrupted. Remember, you're not alone. Take care!")
                break
            except Exception as e:
                print(f" Session error: {e}")
                continue
    
    def get_recent_emotional_trend(self) -> str:
        """Analyze recent emotional trends"""
        if len(self.memory_manager.conversations) < 3:
            return "Building emotional baseline"
        
        recent_emotions = [conv.get('primary_emotion', 'neutral') for conv in self.memory_manager.conversations[-5:]]
        recent_stress = [conv.get('stress_level', 5) for conv in self.memory_manager.conversations[-5:]]
        
        avg_stress = sum(recent_stress) / len(recent_stress)
        stress_trend = recent_stress[-1] - recent_stress if len(recent_stress) > 1 else 0
        
        if stress_trend > 2:
            return f"Stress increasing (avg: {avg_stress:.1f}/10) - needs attention"
        elif stress_trend < -2:
            return f"Stress decreasing (avg: {avg_stress:.1f}/10) - positive progress"
        elif avg_stress >= 7:
            return f"Consistently high stress (avg: {avg_stress:.1f}/10) - support needed"
        else:
            return f"Emotionally stable (avg stress: {avg_stress:.1f}/10)"
    
    def show_crisis_resources(self):
        """Show crisis resources"""
        print(f"\nCRISIS SUPPORT RESOURCES:")
        print(f"   IMMEDIATE HELP (24/7):")
        print(f"      -  National Suicide Prevention Lifeline: 988")
        print(f"      -  Crisis Text Line: Text HOME to 741741")
        print(f"      -  Emergency Services: 911")
        print(f"   Remember: You are not alone. Your life has value.")
    
    def show_stress_analysis(self):
        """Show stress analysis"""
        conversations = self.memory_manager.conversations
        if not conversations:
            print("\n No stress data available yet.")
            return
        
        recent_stress = [conv.get('stress_level', 5) for conv in conversations[-10:]]
        current_stress = recent_stress[-1] if recent_stress else 5
        avg_stress = sum(recent_stress) / len(recent_stress)
        
        print(f"\n STRESS ANALYSIS:")
        print(f"   Current Stress: {current_stress}/10")
        print(f"   Session Average: {avg_stress:.1f}/10")
        print(f"   Total Sessions: {len(conversations)}")
        
        # Visual representation
        print(f"\n Recent Stress Pattern:")
        for i, stress in enumerate(recent_stress[-5:]):
            bar = "█" * int(stress) + "░" * (10 - int(stress))
            print(f"   Session {len(conversations) - 5 + i + 1}: [{bar}] {stress}/10")
        
        # Recommendations
        if avg_stress >= 8:
            print(f"\n RECOMMENDATION: High stress levels detected.")
            print(f"   Consider professional counseling or medical consultation.")
        elif avg_stress >= 6:
            print(f"\n SUGGESTION: Implement stress management practices.")
            print(f"   Try daily meditation, exercise, or relaxation techniques.")
        else:
            print(f"\n GOOD NEWS: Stress levels are well-managed!")
    
    def show_emotional_history(self):
        """Show emotional history"""
        conversations = self.memory_manager.conversations
        if not conversations:
            print("\n No conversation history yet.")
            return
        
        print(f"\n EMOTIONAL JOURNEY ({len(conversations)} sessions):")
        print("-" * 50)
        
        for conv in conversations[-10:]:  # Show last 10
            timestamp = datetime.fromisoformat(conv['timestamp'])
            emotion = conv.get('primary_emotion', 'neutral').title()
            stress = conv.get('stress_level', 5)
            
            indicator = "🔴" if stress >= 8 else "🟡" if stress >= 5 else "🟢"
            
            print(f"{timestamp.strftime('%m/%d %H:%M')} | {indicator} {emotion:8} | Stress: {stress}/10")
            context = conv.get('context', '')[:60]
            if context:
                print(f"   You: \"{context}{'...' if len(conv.get('context', '')) > 60 else ''}\"")
            print()
    
    def show_help(self):
        """Show help"""
        print(f"\n AI THERAPIST HELP:")
        print("="*40)
        print(f" COMMANDS:")
        print(f"   -  'crisis' - Crisis support resources")
        print(f"   -  'stress' - Stress analysis and trends")
        print(f"   -  'history' - Your emotional journey")
        print(f"   -  'help' - This help message")
        print(f"   -  'quit' - End session")
        
        print(f"\n FEATURES:")
        print(f"   -  Gemini 1.5 Flash Latest AI analysis")
        print(f"   -  Professional therapeutic responses")
        print(f"   -  Crisis detection and intervention")
        print(f"   -  Stress monitoring (0-10 scale)")
        print(f"   -  Emotional pattern tracking")
        
        print(f"\n TIPS:")
        print(f"   -  Be open about your feelings for better analysis")
        print(f"   -  The AI learns your patterns over time")
        print(f"   -  All conversations are private and stored locally")
    
    def update_session_stats(self, emotion_data: Dict):
        """Update session stats"""
        stress_levels = [conv.get('stress_level', 5) for conv in self.memory_manager.conversations]
        if stress_levels:
            self.session_stats['avg_stress_level'] = sum(stress_levels) / len(stress_levels)
    
    def end_session(self):
        """End session with summary"""
        exchanges = self.session_stats['exchanges']
        avg_stress = self.session_stats['avg_stress_level']
        crisis_interventions = self.session_stats['crisis_interventions']
        
        print(f"\n⚕️ Dr. HelAI - Session Summary:")
        print("="*50)
        print(f"Thank you for our session today.")
        
        if exchanges > 0:
            print(f"We had {exchanges} meaningful exchanges.")
            print(f"Average stress level: {avg_stress:.1f}/10")
            
            if crisis_interventions > 0:
                print(f"Crisis interventions: {crisis_interventions}")
                print(f"Please remember the support resources provided.")
            
            current_stress = self.memory_manager.conversations[-1].get('stress_level', 5) if self.memory_manager.conversations else 5
            
            if current_stress >= 8:
                print(f"\n Your stress level is high ({current_stress}/10). Please prioritize self-care.")
                print(f"Consider reaching out to mental health professionals.")
            else:
                print(f"\n Your stress level is manageable ({current_stress}/10). Keep up the good work.")
        
        total_sessions = len(self.memory_manager.conversations)
        print(f"\nI now have {total_sessions} sessions to better support you.")
        print(f"\n Remember: Your mental health matters. Take care of yourself!")

if __name__ == "__main__":
    try:
        print("Starting AI Therapist with Gemini 1.5 Flash Latest...")
        print("Using secure API connection...")
        
        therapist = GeminiAITherapist()
        therapist.start_session()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Gemini API key is correct")
        print("2. Verify internet connection") 
        print("3. Ensure all dependencies are installed")
