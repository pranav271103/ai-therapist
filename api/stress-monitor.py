import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from lib.gemini_ai_therapist import GeminiAITherapist
import json
from datetime import datetime

therapist = None

def handler(request):
    global therapist
    
    if therapist is None:
        try:
            therapist = GeminiAITherapist()
        except:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'error',
                    'current_stress': 5,
                    'trend': 'stable'
                })
            }
    
    try:
        conversations = therapist.memory_manager.conversations
        
        if not conversations:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'current_stress': 5,
                    'trend': 'stable',
                    'last_updated': datetime.now().isoformat(),
                    'stress_history': []
                })
            }
        
        # Get recent stress data
        recent_stress = [conv.get('stress_level', 5) for conv in conversations[-10:]]
        current_stress = recent_stress[-1]
        
        # Calculate trend
        if len(recent_stress) >= 2:
            trend = 'increasing' if recent_stress[-1] > recent_stress[-2] else 'decreasing' if recent_stress[-1] < recent_stress[-2] else 'stable'
        else:
            trend = 'stable'
        
        # Build stress history for live chart
        stress_history = []
        for i, stress in enumerate(recent_stress[-5:]):  # Last 5 data points
            stress_history.append({
                'time': datetime.now().isoformat(),
                'stress': stress,
                'session': len(conversations) - 5 + i + 1
            })
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'success',
                'current_stress': current_stress,
                'trend': trend,
                'last_updated': conversations[-1].get('timestamp', datetime.now().isoformat()),
                'stress_history': stress_history,
                'average_stress': sum(recent_stress) / len(recent_stress),
                'peak_stress': max(recent_stress),
                'sessions_count': len(conversations)
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
                'error': str(e)
            })
        }
