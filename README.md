# Dreamina API Server

A Flask-based REST API server that wraps Dreamina's AI image generation capabilities using browser automation and cookie-based authentication.

## Features

- 🎨 AI Image Generation via Dreamina's Image 4.0 model
- 🔐 Cookie-based authentication
- 🚀 RESTful API endpoints
- 📦 Ready for deployment on Vercel or Render
- 🔄 Automatic browser automation with Selenium

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

### Generate Image
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

### Generate Video (Not Implemented)
```
GET /api/generate/video?prompt=YOUR_PROMPT
```
Returns HTTP 501 - Not Implemented

### Check Status (Not Implemented)
```
GET /api/status/<task_id>
```
Returns HTTP 501 - Not Implemented

## Deployment

### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Upload your `account.json` via Vercel dashboard or CLI

**Note:** Selenium may have limitations on Vercel's serverless platform. Consider using Render for better compatibility.

### Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your repository
3. Render will automatically detect `render.yaml`
4. Add your `account.json` content as a secret file in Render dashboard
5. Deploy!

## Environment Variables

- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Flask environment (production/development)

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
├── vercel.json           # Vercel deployment configuration
├── render.yaml           # Render deployment configuration
└── README.md             # This file
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Dreamina or CapCut. Use at your own risk and ensure compliance with their Terms of Service.
