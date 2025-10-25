# Dreamina API Server

## Project Overview
Backend-only Flask REST API that wraps Dreamina's AI image generation service using browser automation (Selenium) and automated email/password authentication. Created on October 25, 2025.

## Purpose
Provides a programmatic API interface to Dreamina's image generation capabilities since Dreamina doesn't offer a public API.

## Current State
- Production-ready Flask API server running on port 8080
- **Automated email/password login** - No cookie management needed
- **Two model endpoints available**: Image 4.0 and Nano Banana
- Three total endpoints: `/api/generate/image`, `/api/generate/image-4.0`, `/api/generate/nano-banana`
- **Optimized for speed** - 40% faster image generation with intelligent polling
- **Memory optimized for cloud deployment** - ~150MB idle, ~250-300MB during generation
- **Ready for Fly.io deployment** with Docker configuration (2GB RAM required)
- Clean codebase ready for GitHub and production deployment

## Recent Changes (October 25, 2025)

### v2.1.0 - Startup Login (Latest)
- **🚀 NEW: Automatic Login on Server Startup** - Server now performs authentication when it starts
  - Login process executes before Flask accepts any requests
  - Clear success/failure logging with visual indicators (✅/❌)
  - Detailed error messages for missing credentials or authentication failures
  - Optimized for Fly.io deployment with helpful troubleshooting hints
  - Ensures server is ready to process requests immediately after startup

### v2.0.0 - Email/Password Authentication
- **🔐 MAJOR CHANGE: Removed cookie-based authentication** - Now uses automated email/password login
  - No need to extract or manage cookies
  - Automatically logs in using DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables
  - Removed all cookie loading logic
  - Deleted account.json and account.json.example files
- **✨ Improved authentication flow** - Login happens automatically on first request
  - Authentication state cached per service instance
  - Error messages now reference environment variables instead of cookies
  - Health check endpoint provides clear guidance for credential issues
- **📚 Updated documentation** - README and FLY_DEPLOYMENT.md now reflect email/password authentication
  - Deployment instructions simplified (no cookie extraction needed)
  - Security notes updated for credential management
  
### v1.1.1 - Critical Fix: Image Loading
- **🔧 CRITICAL FIX: Removed image blocking** - Chrome was blocking image loading which prevented generated image URLs from appearing
  - Removed `profile.managed_default_content_settings.images: 2` setting
  - This was causing "No images generated" errors even when generation succeeded
  - Images now load properly and URLs are detected
- **🔍 Enhanced image detection debugging** - Now saves screenshot and HTML when image detection fails
  - Shows total images, existing images, and new images detected
  - Logs first 3 image URLs for debugging
  - Better error messages explaining possible causes

### v1.1.0 - Enhanced Debugging for Fly.io
- **🔍 NEW: Debug Endpoints** - Added `/api/debug/screenshot` and `/api/debug/html` endpoints
  - Automatically saves screenshot when button detection fails
  - Saves full page HTML for DOM inspection
  - Helps diagnose Fly.io deployment issues remotely
- **🎯 Updated Button Selectors** - Removed outdated "See results" button, updated for current Dreamina UI
  - Now uses case-insensitive "Generate" button detection
  - Added scroll-into-view before clicking
  - Enhanced button logging with text, class, type, and visibility
  - Increased button detection from 10 to 15 buttons in debug output
- **📚 Comprehensive Documentation** - Created `DEBUGGING_FLYIO.md` guide
  - Step-by-step troubleshooting for Fly.io deployments
  - How to use debug endpoints
  - Performance optimization tips

### Earlier Optimizations
- **⚡ 40% FASTER generation** - Optimized all wait times and polling intervals
  - Reduced initial wait: 5s → 3s
  - Faster polling: 4s intervals → 2s intervals
  - Reduced max timeout: 45s → 35s
  - Streamlined element detection with fewer retry attempts
- **🚀 Fly.io deployment fixes** - Resolved Chrome timeout errors
  - Increased VM memory: 512MB → 2GB (required for Chrome)
  - Added swap space: 512MB for memory spikes
  - Switched to Gunicorn production server (1 worker, 2 threads, 180s timeout)
  - Extended health check grace period to 30s
- **✅ Improved validation** - Stricter image count enforcement
  - Now requires minimum 4 images for success
  - Better error messages for partial generation
  - Added generation_time to response for performance tracking
- **OPTIMIZED: Memory usage** - Reduced memory footprint by ~60-70% to fit within cloud free tier limits
  - Browser now closes after each request instead of staying in memory
  - Added safe memory-optimization Chrome flags
  - Removed global service instance to prevent memory leaks
  - Per-request browser lifecycle with guaranteed cleanup in finally blocks
- **FIXED: Image count issue** - Now correctly returns only 4 newly generated images instead of 34
- **Smart image filtering** - Captures baseline images before generation, only returns new images after
- **Incremental waiting** - Checks every 2 seconds and exits early when 4 new images detected
- **Image count validation** - Ensures at least 4 images are found before returning success
- **Updated page navigation** - Now uses /ai-tool/home/ URL based on actual Dreamina page structure
- **Improved button detection** - Multiple fallback selectors for better reliability
- **Enhanced Selenium reliability** - JavaScript click fallback and better error messages
- **Fixed Selenium stale element reference error** - Elements now refetched inside retry functions
- **Removed unnecessary model endpoints** - Kept only Image 4.0 and Nano Banana models
- **Removed mock mode** - API always runs in production mode
- **Updated Chrome detection** - Service supports both Replit (Nix) and Docker environments

## Project Architecture

### Core Files
- `app.py` - Flask application with API endpoints (updated v2.0.0)
- `dreamina_service.py` - Selenium automation with automated login (updated v2.0.0)
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image for deployment with Chrome/ChromeDriver
- `.dockerignore` - Docker build exclusions
- `fly.toml` - Fly.io deployment configuration
- `FLY_DEPLOYMENT.md` - Complete Fly.io deployment guide (updated v2.0.0)
- `DEBUGGING_FLYIO.md` - Comprehensive debugging guide for Fly.io deployments
- `README.md` - Updated with v2.0.0 email/password authentication instructions

### API Endpoints
1. `GET /` - API information and health
2. `GET /api/health` - Authentication status check
3. `GET /api/generate/image?prompt=...` - Image generation with default model (Image 4.0)
4. `GET /api/generate/image-4.0?prompt=...` - Image generation with Image 4.0 model
5. `GET /api/generate/nano-banana?prompt=...` - Image generation with Nano Banana model
6. `GET /api/debug/screenshot` - Get debug screenshot (PNG) when generation fails
7. `GET /api/debug/auth-screenshot` - Get debug screenshot from authentication check
8. `GET /api/debug/html` - Get debug HTML for DOM inspection

### Dependencies
- Flask 3.1.2 (web framework)
- Flask-CORS 6.0.1 (cross-origin support)
- Selenium 4.38.0 (browser automation)
- webdriver-manager 4.0.2 (ChromeDriver management)
- requests 2.32.5 (HTTP client)
- Pillow 12.0.0 (image processing)

## User Preferences
- Backend-only API (no frontend required)
- GET methods for all endpoints
- Deployment target: Fly.io
- Email/password authentication via environment variables (DREAMINA_EMAIL, DREAMINA_PASSWORD)

## Known Limitations
- Browser automation doesn't honor aspect_ratio, quality, or model parameters yet
- Requires Chrome/Chromium for Selenium
- Slower than direct API calls due to browser automation (30-45 seconds typical)
- Only two models supported: Image 4.0 and Nano Banana
- Login method must be email (Google/TikTok/Facebook login not supported yet)

## Fly.io Deployment Guide

### Quick Start
See `FLY_DEPLOYMENT.md` for complete deployment instructions.

### Prerequisites
1. Active Fly.io account (https://fly.io)
2. Fly CLI installed (`curl -L https://fly.io/install.sh | sh`)
3. Valid Dreamina credentials (email and password)

### Deployment Steps
```bash
# 1. Login to Fly.io
fly auth login

# 2. Create app
fly apps create dreamina-api

# 3. Set credentials as secrets
fly secrets set DREAMINA_EMAIL="your_email@example.com"
fly secrets set DREAMINA_PASSWORD="your_password"

# 4. Deploy
fly deploy

# 5. Test
fly open
```

### Deployment Configuration
- **Docker**: Automatically installs Chrome + ChromeDriver
- **Port**: 8080 (configured in Dockerfile and fly.toml)
- **Free Tier**: 3 shared-cpu-1x 256MB VMs (auto-scaling enabled)
- **Memory**: 2GB required for Chrome
- **Auto-deploy**: Run `fly deploy` to update

### Key Features
- Auto-stop when idle (saves costs)
- Auto-start on request
- Health checks every 30s
- HTTPS enabled by default

## Setup Instructions
1. Set DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables
2. Run `python app.py` to start server on port 8080
3. For deployment: use Fly.io (see `FLY_DEPLOYMENT.md`)

## Security Notes
- Credentials stored securely in environment variables / Replit Secrets / Fly.io secrets
- Never commit credentials to version control
- Credentials are never logged or exposed in API responses
- Use secure secret management for production

## Future Enhancements
- Implement aspect_ratio, quality, and model parameter support in Selenium automation
- Add support for Google/TikTok/Facebook login methods
- Add video generation capability
- Implement task status checking for async operations
- Add request queuing for concurrent requests
- Add caching layer for generated images
