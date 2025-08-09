def handler(request):
    if request.method == 'OPTIONS':
        return Response('', status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
    
    import json
    from datetime import datetime
    
    response_data = {
        'status': 'healthy',
        'message': 'Dr. HelAI is running on Vercel',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production'
    }
    
    return Response(
        json.dumps(response_data),
        status=200,
        headers={
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    )

class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status_code = status
        self.headers = headers or {}
