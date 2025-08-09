# api/health.py
import json
from datetime import datetime

def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'message': 'Dr. HelAI is running on Vercel',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production'
        })
    }
