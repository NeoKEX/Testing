from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import atexit
from dreamina_service import DreaminaService

app = Flask(__name__)
CORS(app)

dreamina_service = None
MOCK_MODE = os.environ.get('MOCK_MODE', 'false').lower() == 'true'

def init_service():
    global dreamina_service
    if dreamina_service is None and not MOCK_MODE:
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
        'mock_mode': MOCK_MODE,
        'endpoints': {
            '/api/generate/image': 'Generate AI Image with default model (GET)',
            '/api/generate/image-4.0': 'Generate with Image 4.0 model (GET)',
            '/api/generate/nano-banana': 'Generate with Nano Banana model (GET)',
            '/api/health': 'Health check endpoint (GET)'
        },
        'note': 'Running in MOCK mode in Replit - Deploy to Render for real functionality' if MOCK_MODE else 'Production mode'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        if MOCK_MODE:
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'mock_mode': True,
                'message': 'Running in MOCK mode - deploy to Render for real functionality'
            })
        
        service = init_service()
        is_authenticated = service.check_authentication()
        return jsonify({
            'status': 'success',
            'authenticated': is_authenticated,
            'mock_mode': False,
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
        
        if MOCK_MODE:
            return jsonify({
                'status': 'success',
                'mock_mode': True,
                'prompt': prompt,
                'model': model,
                'aspect_ratio': aspect_ratio,
                'quality': quality,
                'images': [
                    'https://example.com/mock_image_1.jpg',
                    'https://example.com/mock_image_2.jpg'
                ],
                'count': 2,
                'message': 'MOCK response - Deploy to Render for real image generation'
            })
        
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

@app.route('/api/generate/image-4.0', methods=['GET'])
def generate_image_4_0():
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: prompt'
            }), 400
        
        aspect_ratio = request.args.get('aspect_ratio', '1:1')
        quality = request.args.get('quality', 'high')
        
        if MOCK_MODE:
            return jsonify({
                'status': 'success',
                'mock_mode': True,
                'prompt': prompt,
                'model': 'image_4.0',
                'aspect_ratio': aspect_ratio,
                'quality': quality,
                'images': [
                    'https://example.com/mock_image_4.0_1.jpg',
                    'https://example.com/mock_image_4.0_2.jpg'
                ],
                'count': 2,
                'message': 'MOCK response - Deploy to Render for real image generation'
            })
        
        service = init_service()
        result = service.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            quality=quality,
            model='image_4.0'
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

@app.route('/api/generate/nano-banana', methods=['GET'])
def generate_nano_banana():
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: prompt'
            }), 400
        
        aspect_ratio = request.args.get('aspect_ratio', '1:1')
        quality = request.args.get('quality', 'high')
        
        if MOCK_MODE:
            return jsonify({
                'status': 'success',
                'mock_mode': True,
                'prompt': prompt,
                'model': 'nano_banana',
                'aspect_ratio': aspect_ratio,
                'quality': quality,
                'images': [
                    'https://example.com/mock_nano_banana_1.jpg',
                    'https://example.com/mock_nano_banana_2.jpg'
                ],
                'count': 2,
                'message': 'MOCK response - Deploy to Render for real image generation'
            })
        
        service = init_service()
        result = service.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            quality=quality,
            model='nano_banana'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    if MOCK_MODE:
        print("=" * 60)
        print("RUNNING IN MOCK MODE")
        print("Selenium/Chrome disabled - API returns mock responses")
        print("Deploy to Render for real Dreamina image generation")
        print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
