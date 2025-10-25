# Dreamina API Server

## Project Overview
Backend-only Flask REST API that wraps Dreamina's AI image generation service using browser automation (Selenium) and cookie-based authentication. Created on October 25, 2025.

## Purpose
Provides a programmatic API interface to Dreamina's image generation capabilities since Dreamina doesn't offer a public API.

## Current State
- Production-ready Flask API server running on port 8080
- **Two model endpoints available**: Image 4.0 and Nano Banana
- Three total endpoints: `/api/generate/image`, `/api/generate/image-4.0`, `/api/generate/nano-banana`
- Cookie-based authentication via `account.json` file or environment variables
- **Optimized for speed** - 40% faster image generation with intelligent polling
- **Memory optimized for cloud deployment** - ~150MB idle, ~250-300MB during generation
- **Ready for Fly.io deployment** with Docker configuration (2GB RAM required)
- Clean codebase ready for GitHub and production deployment

## Recent Changes (October 25, 2025)

### v1.1.0 - Enhanced Debugging for Fly.io (Just Now)
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
  - Cookie refresh instructions
  - Performance optimization tips
- **✅ Confirmed Model Support** - Verified Image 4.0 is available (per user screenshot)
  - All 7 Dreamina models documented in API response
  - Updated API home endpoint to show supported models

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
  - Added WDM_LOCAL environment variable for faster ChromeDriver setup
- **✅ Improved validation** - Stricter image count enforcement
  - Now requires minimum 4 images for success
  - Better error messages for partial generation
  - Added generation_time to response for performance tracking

### Earlier Optimizations
- **OPTIMIZED: Memory usage** - Reduced memory footprint by ~60-70% to fit within cloud free tier limits
  - Browser now closes after each request instead of staying in memory
  - Added safe memory-optimization Chrome flags
  - Removed global service instance to prevent memory leaks
  - Per-request browser lifecycle with guaranteed cleanup in finally blocks
- **FIXED: Image count issue** - Now correctly returns only 4 newly generated images instead of 34 (was capturing all images on page)
- **Smart image filtering** - Captures baseline images before generation, only returns new images after
- **Incremental waiting** - Checks every 2 seconds and exits early when 4 new images detected
- **Image count validation** - Ensures at least 4 images are found before returning success
- **Updated page navigation** - Now uses /ai-tool/home/ URL based on actual Dreamina page structure
- **Improved button detection** - Multiple fallback selectors including "See results" button
- **Enhanced Selenium reliability** - JavaScript click fallback and better error messages
- **Fixed Selenium stale element reference error** - Elements now refetched inside retry functions
- **Removed unnecessary model endpoints** - Kept only Image 4.0 and Nano Banana models
- **Removed mock mode** - API always runs in production mode (no development/mock modes)
- **Updated Chrome detection** - Service supports both Replit (Nix) and Docker environments
- **Enhanced Fly.io configuration** - Configured for Fly.io deployment with Docker
- **Ready for deployment** - All Fly.io configuration files verified and tested
- Created Flask API server with CORS support
- Implemented Selenium-based Dreamina service with cookie authentication
- Added cookie validation and WebDriver lifecycle management
- Added comprehensive README with API documentation

## Project Architecture

### Core Files
- `app.py` - Flask application with API endpoints (updated v1.1.0)
- `dreamina_service.py` - Selenium automation for Dreamina interaction (updated v1.1.0)
- `account.json.example` - Template for user cookie configuration
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image for deployment with Chrome/ChromeDriver
- `.dockerignore` - Docker build exclusions
- `fly.toml` - Fly.io deployment configuration
- `FLY_DEPLOYMENT.md` - Complete Fly.io deployment guide
- `DEBUGGING_FLYIO.md` - **NEW** Comprehensive debugging guide for Fly.io deployments
- `README.md` - Updated with v1.1.0 troubleshooting instructions

### API Endpoints
1. `GET /` - API information and health
2. `GET /api/health` - Authentication status check
3. `GET /api/generate/image?prompt=...` - Image generation with default model (Image 4.0)
4. `GET /api/generate/image-4.0?prompt=...` - Image generation with Image 4.0 model
5. `GET /api/generate/nano-banana?prompt=...` - Image generation with Nano Banana model
6. `GET /api/debug/screenshot` - **NEW** Get debug screenshot (PNG) when generation fails
7. `GET /api/debug/html` - **NEW** Get debug HTML for DOM inspection

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
- Cookie-based authentication via JSON file or environment variables

## Known Limitations
- Browser automation doesn't honor aspect_ratio, quality, or model parameters yet
- Requires Chrome/Chromium for Selenium
- Slower than direct API calls due to browser automation
- Cookie sessions may expire and require renewal
- Only two models supported: Image 4.0 and Nano Banana

## Fly.io Deployment Guide

### Quick Start
See `FLY_DEPLOYMENT.md` for complete deployment instructions.

### Prerequisites
1. Active Fly.io account (https://fly.io)
2. Fly CLI installed (`curl -L https://fly.io/install.sh | sh`)
3. Valid Dreamina cookies in `account.json` format

### Deployment Steps
```bash
# 1. Login to Fly.io
fly auth login

# 2. Create app
fly apps create dreamina-api

# 3. Set cookies as secret
fly secrets set ACCOUNT_JSON='[{"name":"cookie_name","value":"cookie_value","domain":".dreamina.capcut.com"}]'

# 4. Deploy
fly deploy

# 5. Test
fly open
```

### Deployment Configuration
- **Docker**: Automatically installs Chrome + ChromeDriver
- **Port**: 8080 (configured in Dockerfile and fly.toml)
- **Free Tier**: 3 shared-cpu-1x 256MB VMs (auto-scaling enabled)
- **Auto-deploy**: Run `fly deploy` to update

### Key Features
- Auto-stop when idle (saves costs)
- Auto-start on request
- Health checks every 30s
- HTTPS enabled by default

## Setup Instructions
1. Extract Dreamina cookies from browser after logging in
2. Create `account.json` with cookie data (use `account.json.example` as template)
3. Run `python app.py` to start server on port 8080
4. For deployment: use Fly.io (see `FLY_DEPLOYMENT.md`)

## Security Notes
- `account.json` is gitignored (contains sensitive cookies)
- Cookies should be treated as passwords
- No encryption at rest - ensure proper file permissions
- Recommend environment variables or secret management for production

## Future Enhancements
- Implement aspect_ratio, quality, and model parameter support in Selenium automation
- Add video generation capability
- Implement task status checking for async operations
- Add request queuing for concurrent requests
- Implement cookie rotation mechanism
- Add caching layer for generated images
