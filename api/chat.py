import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from lib.gemini_ai_therapist import GeminiAITherapist
import json
from datetime import datetime

# Global therapist instance for performance
therapist = None

def handler(request):
    global therapist
    
    # Initialize on first request
    if therapist is None:
        try:
            therapist = GeminiAITherapist()
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
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
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }
        }
    
    if request.method == 'POST':
        try:
            # Parse request body
            if hasattr(request, 'body'):
                body = request.body
            else:
                body = request.get_body()
            
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            
            data = json.loads(body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Empty message'})
                }

            # Capture therapeutic analysis
            captured_response = {}
            
            def capture_analysis(emotion_data, response_data):
                captured_response['emotion_data'] = emotion_data
                captured_response['response_data'] = response_data
                captured_response['ai_response'] = response_data.get('response')

            # Temporarily replace display method to capture output
            original_display = therapist.display_therapeutic_analysis
            therapist.display_therapeutic_analysis = capture_analysis
            
            # Process conversation
            therapist.process_therapeutic_conversation(user_message)
            
            # Restore original method
            therapist.display_therapeutic_analysis = original_display

            emotion_data = captured_response.get('emotion_data', {})
            response_data = captured_response.get('response_data', {})
            current_stress = emotion_data.get('stress_level', 5)
            
            # Helper function to get valid color string
            def get_stress_color(stress_level):
                if stress_level >= 8:
                    return 'red'
                elif stress_level >= 6:
                    return 'orange'
                elif stress_level >= 4:
                    return 'yellow'
                else:
                    return 'green'
            
            # Helper function to get valid animation string
            def get_stress_animation(stress_level):
                if stress_level >= 8:
                    return 'warning-pulse'
                elif stress_level >= 6:
                    return 'pulse-stress'
                elif stress_level >= 4:
                    return 'heartbeat'
                else:
                    return 'none'
            
            # Helper function to get stress label
            def get_stress_label(stress_level):
                if stress_level >= 9:
                    return 'Crisis'
                elif stress_level >= 7:
                    return 'High Stress'
                elif stress_level >= 5:
                    return 'Moderate'
                elif stress_level >= 3:
                    return 'Low Stress'
                else:
                    return 'Calm'
            
            # Determine trend
            conversations = therapist.memory_manager.conversations
            trend = 'stable'
            if len(conversations) > 1:
                prev_stress = conversations[-2].get('stress_level', 5)
                if current_stress > prev_stress:
                    trend = 'increasing'
                elif current_stress < prev_stress:
                    trend = 'decreasing'
            
            # Enhanced stress meter data with proper typing
            stress_meter = {
                'current': current_stress,
                'percentage': (current_stress / 10) * 100,
                'color': get_stress_color(current_stress),
                'label': get_stress_label(current_stress),
                'animation': get_stress_animation(current_stress),
                'trend': trend
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
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
                    'stress_meter': stress_meter,
                    'therapeutic_insights': {
                        'approach': response_data.get('therapeutic_approach', 'Supportive'),
                        'coping_suggestion': response_data.get('coping_suggestion', ''),
                        'is_crisis': current_stress >= 8 or emotion_data.get('risk_assessment') == 'crisis'
                    },
                    'timestamp': datetime.now().isoformat()
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'error',
                    'response': 'I apologize for the technical difficulty. I\'m still here to support you.',
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
    
    return {
        'statusCode': 405,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Method not allowed'})
    }
