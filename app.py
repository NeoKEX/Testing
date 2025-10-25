from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import atexit
from dreamina_service import DreaminaService

app = Flask(__name__)
CORS(app)

dreamina_service = None

def init_service():
    global dreamina_service
    if dreamina_service is None:
        dreamina_service = DreaminaService()
    return dreamina_service

def cleanup_service():
    global dreamina_service
    if dreamina_service is not None:
        dreamina_service.close()

atexit.register(cleanup_service)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Dreamina API Server is running',
        'version': '1.0.0',
        'endpoints': {
            '/api/generate/image': 'Generate AI Image (GET)',
            '/api/health': 'Health check endpoint (GET)',
            '/api/generate/video': 'Generate AI Video (GET) - Not implemented',
            '/api/status/<task_id>': 'Check generation status (GET) - Not implemented'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        service = init_service()
        is_authenticated = service.check_authentication()
        return jsonify({
            'status': 'success',
            'authenticated': is_authenticated,
            'message': 'Service is healthy' if is_authenticated else 'Authentication required'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'authenticated': False,
            'message': str(e)
        }), 500

@app.route('/api/generate/image', methods=['GET'])
def generate_image():
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: prompt'
            }), 400
        
        aspect_ratio = request.args.get('aspect_ratio', '1:1')
        quality = request.args.get('quality', 'high')
        model = request.args.get('model', 'image_4.0')
        
        service = init_service()
        result = service.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            quality=quality,
            model=model
        )
        
        if result.get('status') == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Image generation failed: {str(e)}'
        }), 500

@app.route('/api/generate/video', methods=['GET'])
def generate_video():
    return jsonify({
        'status': 'error',
        'message': 'Video generation is not yet implemented'
    }), 501

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    return jsonify({
        'status': 'error',
        'message': 'Status check is not yet implemented'
    }), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
