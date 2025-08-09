from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        'status': 'healthy',
        'message': 'Dr. HelAI is running on Vercel',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production'
    })

# For Vercel
handler = app
