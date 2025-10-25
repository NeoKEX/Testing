# Dreamina API Server

A Flask-based REST API server that wraps Dreamina's AI image generation capabilities using browser automation and email/password authentication.

## Features

- 🎨 AI Image Generation via Dreamina models:
  - **Image 4.0** - High quality, detailed images
  - **Nano Banana** - Fast, lightweight model
- 🔐 Automated email/password login (no cookie management needed)
- 🚀 RESTful API endpoints with GET method support
- 📦 Ready for deployment on Fly.io
- 🔄 Automatic browser automation with Selenium
- ✨ Improved stale element handling for reliability
- 💾 Memory optimized (~150MB idle, ~250-300MB during generation)

## Prerequisites

- Python 3.11+
- Chrome/Chromium browser (for Selenium)
- Active Dreamina account (email login method)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Dreamina credentials as environment variables

## Credentials Setup

You need to set two environment variables:

- `DREAMINA_EMAIL`: Your Dreamina login email
- `DREAMINA_PASSWORD`: Your Dreamina password

### For Local Development (Replit)

Add these to your Replit Secrets:
1. Click on "Secrets" (lock icon) in the left sidebar
2. Add `DREAMINA_EMAIL` with your email
3. Add `DREAMINA_PASSWORD` with your password

### For Local Development (Other Environments)

```bash
export DREAMINA_EMAIL="your_email@example.com"
export DREAMINA_PASSWORD="your_password"
```

## Running Locally

```bash
python app.py
```

The server will start on `http://localhost:8080`

## API Endpoints

### Home
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /api/health
```
Checks if the service is running and authenticated.

**Response:**
```json
{
  "status": "success",
  "authenticated": true,
  "message": "Service is healthy and authenticated"
}
```

### Generate Image (Default Model)
```
GET /api/generate/image?prompt=YOUR_PROMPT
```

**Parameters:**
- `prompt` (required): Text description of the image to generate
- `aspect_ratio` (optional): Image aspect ratio (default: "1:1") - **Note: Currently not implemented in browser automation**
  - Options: "1:1", "16:9", "9:16", "4:3", "3:4"
- `quality` (optional): Image quality (default: "high") - **Note: Currently not implemented in browser automation**
  - Options: "high", "medium", "low"
- `model` (optional): AI model to use (default: "image_4.0") - **Note: Currently not implemented in browser automation**

**Example:**
```bash
curl "http://localhost:8080/api/generate/image?prompt=a%20beautiful%20sunset&aspect_ratio=16:9&quality=high"
```

**Response:**
```json
{
  "status": "success",
  "prompt": "a beautiful sunset",
  "model": "image_4.0",
  "aspect_ratio": "16:9",
  "quality": "high",
  "images": [
    "https://image-url-1.jpg",
    "https://image-url-2.jpg",
    "https://image-url-3.jpg",
    "https://image-url-4.jpg"
  ],
  "count": 4,
  "generation_time": "28s"
}
```

### Model-Specific Endpoints

#### Image 4.0 Model
```
GET /api/generate/image-4.0?prompt=YOUR_PROMPT
```
Generate images using the Image 4.0 model (high quality, detailed).

#### Nano Banana Model
```
GET /api/generate/nano-banana?prompt=YOUR_PROMPT
```
Generate images using the Nano Banana model (fast, lightweight).

**Both model-specific endpoints accept the same parameters:**
- `prompt` (required): Text description
- `aspect_ratio` (optional): "1:1", "16:9", "9:16", "4:3", "3:4"
- `quality` (optional): "high", "medium", "low"

**Example:**
```bash
curl "http://localhost:8080/api/generate/nano-banana?prompt=cute%20cat&aspect_ratio=1:1"
```

### Debug Endpoints

```
GET /api/debug/screenshot
```
Get debug screenshot from the last generation attempt (useful for troubleshooting).

```
GET /api/debug/auth-screenshot
```
Get debug screenshot from the last authentication check.

```
GET /api/debug/html
```
Get debug HTML from the last generation attempt.

## Deployment

### Fly.io (Recommended)

This project is configured to deploy on Fly.io using Docker for the best compatibility with Chrome/Selenium.

**Quick Start:**
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

The Docker image automatically installs:
- Google Chrome Stable
- ChromeDriver (matching version)
- All Python dependencies

**Features:**
- Auto-stop when idle (saves costs)
- Auto-start on request
- HTTPS enabled by default
- Free tier: 3 shared-cpu-1x 256MB VMs

📚 **See `FLY_DEPLOYMENT.md` for complete deployment instructions.**

### Local Docker Testing

To test the Docker setup locally:

```bash
docker build -t dreamina-api .
docker run -p 8080:8080 \
  -e DREAMINA_EMAIL="your_email@example.com" \
  -e DREAMINA_PASSWORD="your_password" \
  dreamina-api
```

## Environment Variables

- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Flask environment (production/development)
- `DREAMINA_EMAIL`: Your Dreamina login email (required)
- `DREAMINA_PASSWORD`: Your Dreamina password (required)

## Important Notes

⚠️ **Limitations:**
- This is a reverse-proxy solution as Dreamina doesn't provide a public API
- Browser automation is slower than direct API calls (30-45 seconds typical)
- **Current implementation**: `aspect_ratio`, `quality`, and `model` parameters are accepted but not yet applied to the Dreamina UI - all generations use default settings
- Automated login requires stable network connection
- Selenium requires Chrome/Chromium to be installed
- Free tier deployments may have resource limitations
- WebDriver lifecycle managed automatically but may consume resources on long-running instances

⚠️ **Terms of Service:**
- Ensure your usage complies with Dreamina's Terms of Service
- This tool is for educational and personal use
- Heavy automation may violate service terms

⚠️ **Security:**
- Store credentials securely using environment variables or secret management
- Never commit credentials to version control
- Use Replit Secrets, Fly.io secrets, or similar secure storage
- Credentials are never logged or exposed in API responses

## Troubleshooting

### "DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables are required"
- Set the environment variables in your deployment platform
- For Replit: Add to Secrets
- For Fly.io: Use `fly secrets set`
- For local: Use `export` or `.env` file

### "Authentication failed"
- Verify your email and password are correct
- Check if Dreamina requires additional verification (2FA, captcha)
- Try logging in manually to verify your account is active
- Check logs for detailed error messages

### "Failed to click generate button"

**New in v1.1.0:** The API provides debug endpoints to help diagnose this issue.

1. **Get debug screenshot:** Visit `https://your-app.fly.dev/api/debug/screenshot` to see what the browser sees
2. **Get debug HTML:** Visit `https://your-app.fly.dev/api/debug/html` to inspect the page DOM
3. **Check logs:** Run `fly logs` to see detailed button detection attempts

📚 **See `DEBUGGING_FLYIO.md` for complete troubleshooting guide.**

### "Chrome driver not found"
- Run `pip install webdriver-manager` to auto-download drivers
- Or manually install ChromeDriver matching your Chrome version
- For Docker/Fly.io, Chrome is pre-installed

### Slow generation
- Browser automation is inherently slower than direct APIs (30-45 seconds typical)
- Dreamina generates 4 images per request
- Consider adding caching or queue mechanisms for production use

## Project Structure

```
.
├── app.py                  # Flask application and API endpoints
├── dreamina_service.py     # Selenium automation and Dreamina interaction
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration for deployment
├── fly.toml               # Fly.io deployment configuration
├── FLY_DEPLOYMENT.md      # Fly.io deployment guide
└── README.md              # This file
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Dreamina or CapCut. Use at your own risk and ensure compliance with their Terms of Service.
