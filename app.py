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
        'version': '2.1.1',
        'endpoints': {
            '/login': 'Test login functionality (GET)',
            '/api/health': 'Health check endpoint (GET)',
            '/api/generate/image': 'Generate AI Image with default model (GET: ?prompt=...&model=image_4.0)',
            '/api/generate/image-4.0': 'Generate with Image 4.0 model (GET: ?prompt=...)',
            '/api/generate/nano-banana': 'Generate with Nano Banana model (GET: ?prompt=...)',
            '/api/debug/screenshot': 'Get debug screenshot when generation fails (GET)',
            '/api/debug/html': 'Get debug HTML when generation fails (GET)',
            '/api/debug/login-screenshots': 'List all login debug screenshots (GET)'
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

@app.route('/login', methods=['GET'])
def login_check():
    """Dedicated endpoint to test login functionality"""
    service = None
    try:
        print("=" * 60)
        print("🔐 LOGIN ENDPOINT CALLED")
        print("=" * 60)
        
        service = init_service()
        is_authenticated = service.check_authentication()
        
        if is_authenticated:
            print("=" * 60)
            print("✅ LOGIN CHECK: SUCCESSFUL")
            print("=" * 60)
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'message': 'Login successful - Dreamina authentication is working',
                'timestamp': os.popen('date -u +"%Y-%m-%d %H:%M:%S UTC"').read().strip()
            })
        else:
            print("=" * 60)
            print("❌ LOGIN CHECK: FAILED")
            print("=" * 60)
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': 'Login failed - Could not authenticate with Dreamina',
                'action_required': 'Check your DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables',
                'instructions': 'For Fly.io: Use "fly secrets set DREAMINA_EMAIL=..." and "fly secrets set DREAMINA_PASSWORD=..."',
                'debug_info': {
                    'login_screenshots': '/api/debug/login-screenshots',
                    'auth_screenshot': '/api/debug/auth-screenshot'
                },
                'timestamp': os.popen('date -u +"%Y-%m-%d %H:%M:%S UTC"').read().strip()
            }), 401
            
    except ValueError as e:
        error_msg = str(e)
        print("=" * 60)
        print("❌ LOGIN CHECK: MISSING CREDENTIALS")
        print(f"Error: {error_msg}")
        print("=" * 60)
        
        if 'DREAMINA_EMAIL' in error_msg or 'DREAMINA_PASSWORD' in error_msg:
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': 'Missing credentials - DREAMINA_EMAIL and DREAMINA_PASSWORD are required',
                'action_required': 'Set DREAMINA_EMAIL and DREAMINA_PASSWORD as environment variables',
                'instructions': 'For Fly.io: Use "fly secrets set DREAMINA_EMAIL=your_email@example.com" and "fly secrets set DREAMINA_PASSWORD=your_password"',
                'error_details': error_msg,
                'timestamp': os.popen('date -u +"%Y-%m-%d %H:%M:%S UTC"').read().strip()
            }), 401
        else:
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': f'Configuration error: {error_msg}',
                'timestamp': os.popen('date -u +"%Y-%m-%d %H:%M:%S UTC"').read().strip()
            }), 500
            
    except Exception as e:
        print("=" * 60)
        print("❌ LOGIN CHECK: EXCEPTION")
        print(f"Error: {str(e)}")
        print("=" * 60)
        
        return jsonify({
            'status': 'error',
            'authenticated': False,
            'message': f'Login check failed: {str(e)}',
            'debug_info': {
                'login_screenshots': '/api/debug/login-screenshots',
                'error_details': str(e)
            },
            'timestamp': os.popen('date -u +"%Y-%m-%d %H:%M:%S UTC"').read().strip()
        }), 500
        
    finally:
        if service:
            service.close()
        print("=" * 60)
        print("🔚 LOGIN ENDPOINT COMPLETED")
        print("=" * 60)

@app.route('/api/health', methods=['GET'])
def health_check():
    service = None
    try:
        service = init_service()
        is_authenticated = service.check_authentication()
        
        if is_authenticated:
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'message': 'Service is healthy and authenticated'
            })
        else:
            return jsonify({
                'status': 'warning',
                'authenticated': False,
                'message': 'Authentication failed - Unable to log in to Dreamina',
                'action_required': 'Verify your DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables are correct',
                'instructions': 'For Replit: Check Secrets. For Fly.io: Use "fly secrets list" and "fly secrets set"',
                'debug_screenshot': '/api/debug/auth-screenshot'
            }), 401
    except ValueError as e:
        error_msg = str(e)
        if 'DREAMINA_EMAIL' in error_msg or 'DREAMINA_PASSWORD' in error_msg:
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': 'Missing credentials - DREAMINA_EMAIL and DREAMINA_PASSWORD are required',
                'action_required': 'Set DREAMINA_EMAIL and DREAMINA_PASSWORD as environment variables',
                'instructions': 'For Replit: Add to Secrets. For Fly.io: Use "fly secrets set DREAMINA_EMAIL=..." and "fly secrets set DREAMINA_PASSWORD=..."',
                'error_details': error_msg
            }), 401
        else:
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'message': f'Configuration error: {error_msg}'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'authenticated': False,
            'message': f'Health check failed: {str(e)}'
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

@app.route('/api/debug/auth-screenshot', methods=['GET'])
def get_auth_screenshot():
    """Get the authentication check screenshot if available"""
    screenshot_path = '/tmp/dreamina_auth_check.png'
    if os.path.exists(screenshot_path):
        return send_file(screenshot_path, mimetype='image/png')
    return jsonify({
        'status': 'error',
        'message': 'Authentication screenshot not found. Call /api/health first to generate it.'
    }), 404

@app.route('/api/debug/credentials', methods=['GET'])
def check_credentials():
    """Check if credentials are properly loaded (for debugging)"""
    email = os.environ.get('DREAMINA_EMAIL')
    password = os.environ.get('DREAMINA_PASSWORD')
    
    return jsonify({
        'status': 'success',
        'credentials_loaded': {
            'email': bool(email),
            'password': bool(password)
        },
        'email_preview': f"{email[:3]}...{email[-10:]}" if email else "Not set",
        'password_length': len(password) if password else 0,
        'note': 'This endpoint is for debugging only. Never expose actual credentials.'
    })

@app.route('/api/debug/login-screenshots', methods=['GET'])
def list_login_screenshots():
    """List all available login debug screenshots"""
    screenshots = []
    for file in os.listdir('/tmp'):
        if file.startswith('login_') and file.endswith('.png'):
            screenshots.append(f"/api/debug/login-screenshot/{file}")
    
    return jsonify({
        'status': 'success',
        'screenshots': screenshots,
        'count': len(screenshots)
    })

@app.route('/api/debug/login-screenshot/<filename>', methods=['GET'])
def get_login_screenshot(filename):
    """Get a specific login debug screenshot"""
    if not filename.endswith('.png') or not filename.startswith('login_'):
        return jsonify({
            'status': 'error',
            'message': 'Invalid filename'
        }), 400
    
    screenshot_path = f'/tmp/{filename}'
    if os.path.exists(screenshot_path):
        return send_file(screenshot_path, mimetype='image/png')
    return jsonify({
        'status': 'error',
        'message': f'Screenshot {filename} not found'
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

def startup_login():
    """Perform login on server startup"""
    print("="*60)
    print("🚀 DREAMINA API SERVER STARTUP")
    print("="*60)
    
    service = None
    try:
        print("🔐 Initiating login process...")
        service = init_service()
        is_authenticated = service.check_authentication()
        
        if is_authenticated:
            print("="*60)
            print("✅ LOGIN SUCCESSFUL")
            print("="*60)
            print("✓ Server is authenticated and ready to process requests")
            print("="*60)
        else:
            print("="*60)
            print("❌ LOGIN FAILED")
            print("="*60)
            print("✗ Authentication failed - Unable to log in to Dreamina")
            print("✗ Please verify your DREAMINA_EMAIL and DREAMINA_PASSWORD")
            print("✗ For Fly.io: Use 'fly secrets list' to check secrets")
            print("="*60)
            
    except ValueError as e:
        error_msg = str(e)
        print("="*60)
        print("❌ LOGIN FAILED - MISSING CREDENTIALS")
        print("="*60)
        print(f"✗ Error: {error_msg}")
        print("✗ Set DREAMINA_EMAIL and DREAMINA_PASSWORD as secrets")
        print("✗ For Fly.io: Use 'fly secrets set DREAMINA_EMAIL=...'")
        print("="*60)
        
    except Exception as e:
        print("="*60)
        print("❌ LOGIN FAILED - UNEXPECTED ERROR")
        print("="*60)
        print(f"✗ Error: {str(e)}")
        print("="*60)
        
    finally:
        if service:
            service.close()
    
    print("\n🌐 Starting Flask server...")
    print("="*60)

if __name__ == '__main__':
    startup_login()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
