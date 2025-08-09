import json
import sys
import os
from datetime import datetime

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Global therapist instance
therapist = None

def handler(event, context):
    global therapist
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # Initialize therapist on first request
    if therapist is None:
        try:
            from lib.gemini_ai_therapist import GeminiAITherapist
            therapist = GeminiAITherapist()
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'error',
                    'response': 'AI system initialization failed. Please try again.',
                    'stress_meter': {
                        'current': 5, 
                        'percentage': 50,
                        'color': 'yellow', 
                        'label': 'Baseline',
                        'animation': 'none',
                        'trend': 'stable'
                    },
                    'error': str(e)
                })
            }
    
    try:
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'error': 'Empty message'})
            }

        # Capture therapeutic analysis
        captured_response = {}
        
        def capture_analysis(emotion_data, response_data):
            captured_response['emotion_data'] = emotion_data
            captured_response['response_data'] = response_data
            captured_response['ai_response'] = response_data.get('response')

        # Process conversation
        original_display = therapist.display_therapeutic_analysis
        therapist.display_therapeutic_analysis = capture_analysis
        therapist.process_therapeutic_conversation(user_message)
        therapist.display_therapeutic_analysis = original_display

        emotion_data = captured_response.get('emotion_data', {})
        response_data = captured_response.get('response_data', {})
        current_stress = emotion_data.get('stress_level', 5)
        
        # Helper functions
        def get_stress_color(stress_level):
            if stress_level >= 8: return 'red'
            elif stress_level >= 6: return 'orange'
            elif stress_level >= 4: return 'yellow'
            else: return 'green'
        
        def get_stress_animation(stress_level):
            if stress_level >= 8: return 'warning-pulse'
            elif stress_level >= 6: return 'pulse-stress'
            elif stress_level >= 4: return 'heartbeat'
            else: return 'none'
        
        def get_stress_label(stress_level):
            if stress_level >= 9: return 'Crisis'
            elif stress_level >= 7: return 'High Stress'
            elif stress_level >= 5: return 'Moderate'
            elif stress_level >= 3: return 'Low Stress'
            else: return 'Calm'
        
        # Determine trend
        conversations = therapist.memory_manager.conversations
        trend = 'stable'
        if len(conversations) > 1:
            prev_stress = conversations[-2].get('stress_level', 5)
            if current_stress > prev_stress: trend = 'increasing'
            elif current_stress < prev_stress: trend = 'decreasing'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'status': 'success',
                'response': captured_response.get('ai_response', 'I hear you and I\'m here to support you.'),
                'emotion_analysis': {
                    'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
                    'stress_level': current_stress,
                    'emotion_intensity': emotion_data.get('emotion_intensity', 0.5),
                    'risk_assessment': emotion_data.get('risk_assessment', 'low'),
                    'psychological_markers': emotion_data.get('psychological_markers', [])
                },
                'stress_meter': {
                    'current': current_stress,
                    'percentage': (current_stress / 10) * 100,
                    'color': get_stress_color(current_stress),
                    'label': get_stress_label(current_stress),
                    'animation': get_stress_animation(current_stress),
                    'trend': trend
                },
                'therapeutic_insights': {
                    'approach': response_data.get('therapeutic_approach', 'Supportive'),
                    'coping_suggestion': response_data.get('coping_suggestion', ''),
                    'is_crisis': current_stress >= 8
                },
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'status': 'error',
                'response': 'I apologize for the technical difficulty.',
                'stress_meter': {
                    'current': 5, 
                    'percentage': 50,
                    'color': 'yellow',
                    'label': 'Error State',
                    'animation': 'none',
                    'trend': 'stable'
                },
                'error': str(e)
            })
        }
