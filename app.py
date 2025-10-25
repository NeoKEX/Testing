from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dreamina_service import DreaminaService

app = Flask(__name__)
CORS(app)

def init_service():
    """Create a new service instance for each request to minimize memory usage"""
    return DreaminaService()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Dreamina API Server is running',
        'version': '1.0.0',
        'endpoints': {
            '/api/generate/image': 'Generate AI Image with default model (GET)',
            '/api/generate/image-4.0': 'Generate with Image 4.0 model (GET)',
            '/api/generate/nano-banana': 'Generate with Nano Banana model (GET)',
            '/api/health': 'Health check endpoint (GET)'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    service = None
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
    finally:
        if service:
            service.close()

@app.route('/api/generate/image', methods=['GET'])
def generate_image():
    service = None
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
    finally:
        if service:
            service.close()

@app.route('/api/generate/image-4.0', methods=['GET'])
def generate_image_4_0():
    service = None
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: prompt'
            }), 400
        
        aspect_ratio = request.args.get('aspect_ratio', '1:1')
        quality = request.args.get('quality', 'high')
        
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
    finally:
        if service:
            service.close()

@app.route('/api/generate/nano-banana', methods=['GET'])
def generate_nano_banana():
    service = None
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: prompt'
            }), 400
        
        aspect_ratio = request.args.get('aspect_ratio', '1:1')
        quality = request.args.get('quality', 'high')
        
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
    finally:
        if service:
            service.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
