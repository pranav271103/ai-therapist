def handler(request):
    import json
    from datetime import datetime
    
    # Simple test response without AI for now
    response_body = json.dumps({
        'status': 'success',
        'response': 'Hello! This is a test response from Dr. HelAI.',
        'emotion_analysis': {
            'primary_emotion': 'neutral',
            'stress_level': 5,
            'emotion_intensity': 0.5,
            'risk_assessment': 'low',
            'psychological_markers': []
        },
        'stress_meter': {
            'current': 5,
            'percentage': 50,
            'color': 'yellow',
            'label': 'Baseline',
            'animation': 'none',
            'trend': 'stable'
        },
        'therapeutic_insights': {
            'approach': 'Supportive',
            'coping_suggestion': 'Take deep breaths',
            'is_crisis': False
        },
        'timestamp': datetime.now().isoformat()
    })
    
    return (
        200,
        {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        response_body
    )
