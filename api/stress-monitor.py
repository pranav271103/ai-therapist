from http.server import BaseHTTPRequestHandler
import sys
import os
import json
from datetime import datetime

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

therapist = None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global therapist
        
        if therapist is None:
            try:
                from lib.gemini_ai_therapist import GeminiAITherapist
                therapist = GeminiAITherapist()
            except Exception as e:
                self.send_error_response(500, {
                    'status': 'error',
                    'current_stress': 5,
                    'trend': 'stable',
                    'error': str(e)
                })
                return
        
        try:
            conversations = therapist.memory_manager.conversations
            
            if not conversations:
                response_data = {
                    'status': 'success',
                    'current_stress': 5,
                    'trend': 'stable',
                    'last_updated': datetime.now().isoformat(),
                    'stress_history': []
                }
                self.send_success_response(response_data)
                return
            
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
            
            response_data = {
                'status': 'success',
                'current_stress': current_stress,
                'trend': trend,
                'last_updated': conversations[-1].get('timestamp', datetime.now().isoformat()),
                'stress_history': stress_history,
                'average_stress': sum(recent_stress) / len(recent_stress),
                'peak_stress': max(recent_stress),
                'sessions_count': len(conversations)
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            self.send_error_response(500, {
                'status': 'error',
                'error': str(e)
            })
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
