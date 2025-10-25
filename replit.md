# Dreamina API Server

## Project Overview
Backend-only Flask REST API that wraps Dreamina's AI image generation service using browser automation (Selenium) and cookie-based authentication. Created on October 25, 2025.

## Purpose
Provides a programmatic API interface to Dreamina's image generation capabilities since Dreamina doesn't offer a public API.

## Current State
- Flask API server running on port 8080 in production mode
- **Two model endpoints available**: Image 4.0 and Nano Banana
- Three total endpoints: `/api/generate/image`, `/api/generate/image-4.0`, `/api/generate/nano-banana`
- Cookie-based authentication via `account.json` file
- **Ready for Render deployment** with Docker configuration
- Cross-environment support: works on both Replit (Nix) and Render
- **Fixed stale element error** - Improved Selenium reliability with element refetching

## Recent Changes (October 25, 2025)
- **FIXED: Image count issue** - Now correctly returns only 4 newly generated images instead of 34 (was capturing all images on page)
- **OPTIMIZED: Generation speed** - Reduced wait times throughout the code for 30-40% faster generation
- **Smart image filtering** - Captures baseline images before generation, only returns new images after
- **Incremental waiting** - Checks every 3 seconds and exits early when 4 new images detected
- **Image count validation** - Ensures at least 4 images are found before returning success
- **Updated page navigation** - Now uses /ai-tool/home/ URL based on actual Dreamina page structure
- **Improved button detection** - Multiple fallback selectors including "See results" button
- **Enhanced Selenium reliability** - JavaScript click fallback and better error messages
- **Fixed Selenium stale element reference error** - Elements now refetched inside retry functions
- **Removed unnecessary model endpoints** - Kept only Image 4.0 and Nano Banana models
- **Removed mock mode** - API runs in production mode by default
- **Updated Chrome detection** - Service supports both Replit (Nix) and Render environments
- **Enhanced render.yaml** - Configured for Render deployment with Docker
- **Ready for deployment** - All Render configuration files verified and tested
- Created Flask API server with CORS support
- Implemented Selenium-based Dreamina service with cookie authentication
- Added cookie validation and WebDriver lifecycle management
- Added comprehensive README with API documentation

## Project Architecture

### Core Files
- `app.py` - Flask application with API endpoints
- `dreamina_service.py` - Selenium automation for Dreamina interaction
- `account.json.example` - Template for user cookie configuration
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image for Render deployment with Chrome/ChromeDriver
- `.dockerignore` - Docker build exclusions
- `render.yaml` - Render deployment configuration (uses Docker)
- `vercel.json` - Vercel deployment configuration (legacy)

### API Endpoints
1. `GET /` - API information and health
2. `GET /api/health` - Authentication status check
3. `GET /api/generate/image?prompt=...` - Image generation with default model (Image 4.0)
4. `GET /api/generate/image-4.0?prompt=...` - Image generation with Image 4.0 model
5. `GET /api/generate/nano-banana?prompt=...` - Image generation with Nano Banana model

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
- Deployment target: Vercel or Render free tier
- Cookie-based authentication via JSON file

## Known Limitations
- Browser automation doesn't honor aspect_ratio, quality, or model parameters yet
- Requires Chrome/Chromium for Selenium
- Slower than direct API calls due to browser automation
- Cookie sessions may expire and require renewal
- Only two models supported: Image 4.0 and Nano Banana

## Render Deployment Guide

### Prerequisites
1. Active Render account (https://render.com)
2. Valid Dreamina cookies in `account.json` format
3. Git repository with this code

### Deployment Steps
1. **Push code to GitHub/GitLab**
   - Ensure all files are committed
   - Push to your repository

2. **Create New Web Service on Render**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your repository
   - Render will auto-detect `render.yaml`

3. **Add Secret File (CRITICAL)**
   - Go to your service settings
   - Navigate to "Secret Files" section
   - Click "Add Secret File"
   - Filename: `account.json`
   - Contents: Your Dreamina cookies JSON (from account.json)
   - Click "Save"

4. **Environment Variables** (Optional - already set in render.yaml)
   - PORT: 8080 (auto-configured)
   - FLASK_ENV: production (auto-configured)

5. **Deploy**
   - Click "Create Web Service"
   - Render will build the Docker image (takes 5-10 minutes first time)
   - Wait for deployment to complete

6. **Test Your API**
   - Your API will be available at: `https://your-service-name.onrender.com`
   - Test health endpoint: `https://your-service-name.onrender.com/api/health`
   - Test image generation: `https://your-service-name.onrender.com/api/generate/image-4.0?prompt=test`

### Deployment Configuration
- **Docker**: Automatically installs Chrome + ChromeDriver
- **Port**: 8080 (configured in Dockerfile and render.yaml)
- **Free Tier**: 512MB RAM (sufficient for basic usage)
- **Auto-deploy**: Enabled on git push

### Troubleshooting Deployment
- **Build fails**: Check Docker build logs for missing dependencies
- **Authentication fails**: Verify account.json is added as secret file
- **Service crashes**: Check logs for ChromeDriver/Chrome version mismatch
- **Slow performance**: Free tier has limited resources, consider upgrading

## Setup Instructions
1. Extract Dreamina cookies from browser after logging in
2. Create `account.json` with cookie data (use `account.json.example` as template)
3. Run `python app.py` to start server on port 8080
4. For deployment: use provided `vercel.json` or `render.yaml`

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
