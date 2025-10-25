# Dreamina API Server

A Flask-based REST API server that wraps Dreamina's AI image generation capabilities using browser automation and cookie-based authentication.

## Features

- 🎨 AI Image Generation via two Dreamina models:
  - **Image 4.0** - High quality, detailed images
  - **Nano Banana** - Fast, lightweight model
- 🔐 Cookie-based authentication (file or environment variable)
- 🚀 RESTful API endpoints with GET method support
- 📦 Ready for deployment on Fly.io
- 🔄 Automatic browser automation with Selenium
- ✨ Improved stale element handling for reliability
- 💾 Memory optimized (~150MB idle, ~250-300MB during generation)

## Prerequisites

- Python 3.11+
- Chrome/Chromium browser (for Selenium)
- Active Dreamina account with valid cookies

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create your `account.json` file (see Cookie Setup below)

## Cookie Setup

1. Visit https://dreamina.capcut.com and log in
2. Open browser DevTools (F12)
3. Go to the **Application** or **Storage** tab
4. Navigate to **Cookies** → `https://dreamina.capcut.com`
5. Copy all cookies and create `account.json`:

```json
{
  "cookies": [
    {
      "name": "cookie_name",
      "value": "cookie_value",
      "domain": ".capcut.com"
    }
  ]
}
```

Use `account.json.example` as a template.

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
  "message": "Service is healthy"
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
    "https://image-url-2.jpg"
  ],
  "count": 2
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

## Deployment

### Fly.io (Recommended)

This project is configured to deploy on Fly.io using Docker for the best compatibility with Chrome/Selenium.

**Quick Start:**
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
docker run -p 8080:8080 -v $(pwd)/account.json:/app/account.json dreamina-api
```

## Environment Variables

- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Flask environment (production/development)
- `ACCOUNT_JSON`: Cookie data as JSON string (for Fly.io deployment)
- `ACCOUNT_JSON_BASE64`: Base64-encoded cookie data (alternative for Fly.io)

## Important Notes

⚠️ **Limitations:**
- This is a reverse-proxy solution as Dreamina doesn't provide a public API
- Browser automation is slower than direct API calls
- **Current implementation**: `aspect_ratio`, `quality`, and `model` parameters are accepted but not yet applied to the Dreamina UI - all generations use default settings
- Cookie sessions may expire and require renewal
- Selenium requires Chrome/Chromium to be installed
- Free tier deployments may have resource limitations
- WebDriver lifecycle managed automatically but may consume resources on long-running instances

⚠️ **Terms of Service:**
- Ensure your usage complies with Dreamina's Terms of Service
- This tool is for educational and personal use
- Heavy automation may violate service terms

⚠️ **Security:**
- Store `account.json` securely and never commit it to version control
- Cookies are sensitive credentials - treat them like passwords
- Consider implementing cookie rotation for production use
- The API does not encrypt cookies at rest - ensure proper file permissions
- Recommended: Use environment variables or secure secret management in production

## Troubleshooting

### "account.json not found"
- Create `account.json` using `account.json.example` as template
- Ensure cookies are properly formatted

### "Authentication failed"
- Cookies may have expired - extract fresh cookies from browser
- Ensure you're logged in to Dreamina in your browser
- Check that cookie domain is set to `.capcut.com`

### "Chrome driver not found"
- Run `pip install webdriver-manager` to auto-download drivers
- Or manually install ChromeDriver matching your Chrome version

### Slow generation
- Browser automation is inherently slower than direct APIs
- Consider adding caching or queue mechanisms for production use

## Project Structure

```
.
├── app.py                  # Flask application and API endpoints
├── dreamina_service.py     # Selenium automation and Dreamina interaction
├── account.json           # Your authentication cookies (create this)
├── account.json.example   # Template for account.json
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration for deployment
├── fly.toml              # Fly.io deployment configuration
├── FLY_DEPLOYMENT.md     # Fly.io deployment guide
└── README.md             # This file
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Dreamina or CapCut. Use at your own risk and ensure compliance with their Terms of Service.
