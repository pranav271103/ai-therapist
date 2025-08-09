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
                    'stress_meter': {'current': 5, 'trend': 'stable', 'color': 'yellow'},
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
            
            # Enhanced stress meter data
            stress_meter = {
                'current': current_stress,
                'percentage': (current_stress / 10) * 100,
                'color': 'red' if current_stress >= 8 else 'orange' if current_stress >= 6 else 'yellow' if current_stress >= 4 else 'green',
                'label': 'Crisis' if current_stress >= 9 else 'High Stress' if current_stress >= 7 else 'Moderate' if current_stress >= 5 else 'Low Stress' if current_stress >= 3 else 'Calm',
                'animation': 'warning-pulse' if current_stress >= 8 else 'pulse-stress' if current_stress >= 6 else 'heartbeat' if current_stress >= 4 else 'none',
                'trend': 'increasing' if len(therapist.memory_manager.conversations) > 1 and current_stress > therapist.memory_manager.conversations[-2].get('stress_level', 5) else 'stable'
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
                    'stress_meter': {'current': 5, 'trend': 'stable', 'color': 'yellow'},
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
