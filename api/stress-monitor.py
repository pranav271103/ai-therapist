from flask import Flask, jsonify
import sys
import os
from datetime import datetime

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

app = Flask(__name__)

therapist = None

@app.route('/', methods=['GET', 'OPTIONS'])
def stress_monitor():
    global therapist
    
    # Handle CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    if therapist is None:
        try:
            from lib.gemini_ai_therapist import GeminiAITherapist
            therapist = GeminiAITherapist()
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'current_stress': 5,
                'trend': 'stable',
                'error': str(e)
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    try:
        conversations = therapist.memory_manager.conversations
        
        if not conversations:
            response = jsonify({
                'status': 'success',
                'current_stress': 5,
                'trend': 'stable',
                'last_updated': datetime.now().isoformat(),
                'stress_history': []
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Get recent stress data
        recent_stress = [conv.get('stress_level', 5) for conv in conversations[-10:]]
        current_stress = recent_stress[-1]
        
        # Calculate trend
        if len(recent_stress) >= 2:
            trend = 'increasing' if recent_stress[-1] > recent_stress[-2] else 'decreasing' if recent_stress[-1] < recent_stress[-2] else 'stable'
        else:
            trend = 'stable'
        
        response = jsonify({
            'status': 'success',
            'current_stress': current_stress,
            'trend': trend,
            'last_updated': conversations[-1].get('timestamp', datetime.now().isoformat()),
            'average_stress': sum(recent_stress) / len(recent_stress),
            'peak_stress': max(recent_stress),
            'sessions_count': len(conversations)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'error': str(e)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# For Vercel
handler = app
