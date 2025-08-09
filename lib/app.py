from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import traceback

# Import your existing files exactly as they are
from gemini_emotion_analyzer import GeminiEmotionAnalyzer
from gemini_therapeutic_responder import GeminiTherapeuticResponder
from memory_manager import SimpleMemoryManager
from gemini_ai_therapist import GeminiAITherapist

app = Flask(__name__)
CORS(app)  # Enable CORS for web frontend

# Initialize your existing AI components
print("🧠 Initializing HelAi components...")
therapist = GeminiAITherapist()
print("✅ HelAi ready!")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'HelAi backend is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - uses your existing GeminiAITherapist class"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Use your existing therapist logic
        # We'll capture the output instead of printing to console
        original_display = therapist.display_therapeutic_analysis
        captured_response = {}
        
        def capture_analysis(emotion_data, response_data):
            """Capture the analysis instead of printing"""
            captured_response['emotion_data'] = emotion_data
            captured_response['response_data'] = response_data
            captured_response['ai_response'] = response_data.get('response', 'I hear you and I\'m here to support you.')
        
        # Temporarily replace the display method
        therapist.display_therapeutic_analysis = capture_analysis
        
        # Process using your existing method
        therapist.process_therapeutic_conversation(user_message)
        
        # Restore original method
        therapist.display_therapeutic_analysis = original_display
        
        # Get session statistics
        total_sessions = len(therapist.memory_manager.conversations)
        recent_stress = [conv.get('stress_level', 5) for conv in therapist.memory_manager.conversations[-10:]]
        avg_stress = sum(recent_stress) / len(recent_stress) if recent_stress else 5
        
        # Extract data for web response
        emotion_data = captured_response.get('emotion_data', {})
        response_data = captured_response.get('response_data', {})
        
        return jsonify({
            'status': 'success',
            'response': captured_response.get('ai_response', 'I hear you and I\'m here to support you.'),
            'emotion_analysis': {
                'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
                'stress_level': emotion_data.get('stress_level', 5),
                'emotion_intensity': emotion_data.get('emotion_intensity', 0.5),
                'risk_assessment': emotion_data.get('risk_assessment', 'low'),
                'psychological_markers': emotion_data.get('psychological_markers', []),
                'stress_triggers': emotion_data.get('stress_triggers', [])
            },
            'therapeutic_insights': {
                'approach': response_data.get('therapeutic_approach', 'Supportive'),
                'coping_suggestion': response_data.get('coping_suggestion', ''),
                'stress_interpretation': response_data.get('stress_interpretation', ''),
                'is_crisis': emotion_data.get('risk_assessment') == 'crisis' or emotion_data.get('stress_level', 5) >= 9
            },
            'session_stats': {
                'total_sessions': total_sessions,
                'average_stress': round(avg_stress, 1),
                'current_stress': emotion_data.get('stress_level', 5)
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'response': 'I apologize, but I\'m having some technical difficulties. Please try again.',
            'emotion_analysis': {
                'primary_emotion': 'neutral',
                'stress_level': 5,
                'emotion_intensity': 0.5,
                'risk_assessment': 'low'
            },
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history from your memory manager"""
    try:
        conversations = therapist.memory_manager.conversations
        
        # Format for web display
        history = []
        for conv in conversations[-20:]:  # Last 20 conversations
            history.append({
                'id': conv.get('id', ''),
                'timestamp': conv.get('timestamp', ''),
                'user_message': conv.get('context', ''),
                'emotion': conv.get('primary_emotion', 'neutral'),
                'stress_level': conv.get('stress_level', 5),
                'risk_level': conv.get('risk_assessment', 'low')
            })
        
        return jsonify({
            'status': 'success',
            'history': history,
            'total_conversations': len(conversations)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics from your memory manager"""
    try:
        conversations = therapist.memory_manager.conversations
        
        if not conversations:
            return jsonify({
                'status': 'success',
                'analytics': {
                    'total_sessions': 0,
                    'stress_trend': [],
                    'emotion_distribution': {},
                    'average_stress': 5
                }
            })
        
        # Build stress trend
        stress_trend = []
        for i, conv in enumerate(conversations[-10:]):
            stress_trend.append({
                'session': i + 1,
                'stress': conv.get('stress_level', 5),
                'emotion': conv.get('primary_emotion', 'neutral')
            })
        
        # Calculate emotion distribution
        emotions = [conv.get('primary_emotion', 'neutral') for conv in conversations]
        emotion_dist = {}
        for emotion in set(emotions):
            emotion_dist[emotion] = emotions.count(emotion)
        
        # Calculate statistics
        stress_levels = [conv.get('stress_level', 5) for conv in conversations]
        
        return jsonify({
            'status': 'success',
            'analytics': {
                'total_sessions': len(conversations),
                'stress_trend': stress_trend,
                'emotion_distribution': emotion_dist,
                'average_stress': round(sum(stress_levels) / len(stress_levels), 1),
                'current_trend': therapist.get_recent_emotional_trend() if hasattr(therapist, 'get_recent_emotional_trend') else 'stable'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n🚀 Starting HelAi Web Server...")
    print("📍 Backend API: http://localhost:5000")
    print("🔗 Endpoints:")
    print("   • POST /api/chat - Main chat")
    print("   • GET /api/history - Chat history") 
    print("   • GET /api/analytics - User analytics")
    print("   • GET /api/health - Health check")
    print("\n✨ Ready to connect with frontend!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
