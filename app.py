from flask import Flask, request, jsonify, send_file
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
        'version': '1.1.0',
        'endpoints': {
            '/api/generate/image': 'Generate AI Image with default model (GET: ?prompt=...&model=image_4.0)',
            '/api/generate/image-4.0': 'Generate with Image 4.0 model (GET: ?prompt=...)',
            '/api/generate/nano-banana': 'Generate with Nano Banana model (GET: ?prompt=...)',
            '/api/health': 'Health check endpoint (GET)',
            '/api/debug/screenshot': 'Get debug screenshot when generation fails (GET)',
            '/api/debug/html': 'Get debug HTML when generation fails (GET)'
        },
        'supported_models': [
            'image_4.0',
            'nano_banana',
            'image_3.1',
            'image_3.0',
            'image_2.1',
            'image_2.0_pro',
            'image_1.4'
        ]
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

@app.route('/api/debug/screenshot', methods=['GET'])
def get_debug_screenshot():
    """Get the debug screenshot if available"""
    screenshot_path = '/tmp/dreamina_debug.png'
    if os.path.exists(screenshot_path):
        return send_file(screenshot_path, mimetype='image/png')
    return jsonify({
        'status': 'error',
        'message': 'Debug screenshot not found. Generate an image first to create debug files.'
    }), 404

@app.route('/api/debug/html', methods=['GET'])
def get_debug_html():
    """Get the debug HTML if available"""
    html_path = '/tmp/dreamina_debug.html'
    if os.path.exists(html_path):
        return send_file(html_path, mimetype='text/html')
    return jsonify({
        'status': 'error',
        'message': 'Debug HTML not found. Generate an image first to create debug files.'
    }), 404

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
