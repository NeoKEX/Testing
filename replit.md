# Dreamina API Server

## Project Overview
Backend-only Flask REST API that wraps Dreamina's AI image generation service using browser automation (Selenium) and cookie-based authentication. Created on October 25, 2025.

## Purpose
Provides a programmatic API interface to Dreamina's image generation capabilities since Dreamina doesn't offer a public API.

## Current State
- Flask API server running on port 8080
- Single working endpoint: `/api/generate/image` (GET)
- Unimplemented endpoints return HTTP 501: `/api/generate/video`, `/api/status/<task_id>`
- Cookie-based authentication via `account.json` file
- Configured for deployment on Vercel or Render

## Recent Changes (October 25, 2025)
- Created Flask API server with CORS support
- Implemented Selenium-based Dreamina service with cookie authentication
- Added cookie validation and WebDriver lifecycle management
- Created deployment configurations for Vercel and Render
- Added comprehensive README with API documentation
- Documented current limitations (aspect_ratio, quality, model parameters not yet implemented)

## Project Architecture

### Core Files
- `app.py` - Flask application with API endpoints
- `dreamina_service.py` - Selenium automation for Dreamina interaction
- `account.json.example` - Template for user cookie configuration
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel deployment configuration
- `render.yaml` - Render deployment configuration

### API Endpoints
1. `GET /` - API information and health
2. `GET /api/health` - Authentication status check
3. `GET /api/generate/image?prompt=...` - Image generation (working)
4. `GET /api/generate/video?prompt=...` - Returns 501 (not implemented)
5. `GET /api/status/<task_id>` - Returns 501 (not implemented)

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
- Video generation not implemented
- Task status checking not implemented

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
