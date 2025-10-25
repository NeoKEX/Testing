# Debugging Dreamina API on Fly.io

This guide helps you debug issues when the Dreamina API is deployed on Fly.io and failing to generate images.

## Common Issue: "Failed to click generate button"

When you see this error on Fly.io but it works locally, use these debugging steps:

### Step 1: Check the Debug Screenshot

The updated API now saves a screenshot when it fails to find the generate button.

**Get the screenshot:**
```bash
# Visit this URL in your browser or use curl
https://your-app.fly.dev/api/debug/screenshot
```

This will show you exactly what the Selenium browser sees on Fly.io.

### Step 2: Check the Debug HTML

Get the full page HTML to inspect the actual DOM structure:

```bash
# Visit this URL or save to file
curl https://your-app.fly.dev/api/debug/html > debug.html
```

Then open `debug.html` in your browser and inspect the buttons to find the correct selectors.

### Step 3: Check Application Logs

View real-time logs from Fly.io:

```bash
fly logs
```

Look for:
- "Available buttons" messages showing all detected buttons
- "Button clicked" success messages
- Error messages about authentication or page loading

### Step 4: Test Authentication

```bash
curl https://your-app.fly.dev/api/health
```

Expected response:
```json
{
  "status": "success",
  "authenticated": true,
  "message": "Service is healthy"
}
```

If `authenticated: false`, your cookies have expired and need to be refreshed.

## How to Update Cookies on Fly.io

If authentication fails, update your cookies:

### Method 1: Using fly secrets
```bash
# Get fresh cookies from browser (see main README)
# Then update the secret:
fly secrets set ACCOUNT_JSON='[{"name":"sessionid","value":"NEW_VALUE","domain":".capcut.com"},{"name":"sid_tt","value":"NEW_VALUE","domain":".capcut.com"}]'
```

### Method 2: Using Base64 encoding (for complex cookies)
```bash
# Encode your account.json file
cat account.json | base64 > account.b64

# Set as secret
fly secrets set ACCOUNT_JSON_BASE64=$(cat account.b64)
```

## Understanding the Button Detection

The code tries these selectors in order:

1. `//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'generate')]` - Case-insensitive "generate"
2. `button[class*='generate']` - Class contains "generate"
3. `button[class*='Generate']` - Class contains "Generate" (case-sensitive)
4. `//button[@type='submit']` - Submit type buttons
5. `//button[contains(@class, 'primary')]` - Primary buttons
6. `//button[contains(@class, 'btn-primary')]` - Bootstrap-style primary buttons
7. `button[class*='submit']` - Class contains "submit"

If none work, check the debug files to see what buttons are actually present.

## Testing Locally with Docker

To replicate Fly.io environment locally:

```bash
# Build the Docker image
docker build -t dreamina-api .

# Run with your account.json
docker run -p 8080:8080 -v $(pwd)/account.json:/app/account.json dreamina-api

# Test in another terminal
curl "http://localhost:8080/api/generate/image?prompt=test"
```

## Advanced: SSH into Fly.io Instance

For deep debugging, SSH directly into your running Fly.io instance:

```bash
# Connect to the instance
fly ssh console

# Inside the instance, you can:
# 1. Check if Chrome is running
ps aux | grep chrome

# 2. Check available disk space
df -h

# 3. View debug files
ls -lh /tmp/dreamina_*

# 4. Check Python process
ps aux | grep python
```

## Performance Optimization

If the service is slow or times out:

1. **Increase memory allocation:**
```bash
fly scale memory 512  # Increase to 512MB
```

2. **Check current resource usage:**
```bash
fly status
```

3. **Monitor during generation:**
```bash
fly logs -a your-app-name
```

## New Features in v1.1.0

- ✅ Enhanced debug screenshot capture
- ✅ Debug HTML export for DOM inspection
- ✅ Detailed button logging (shows text, class, type, visibility)
- ✅ New debug endpoints: `/api/debug/screenshot` and `/api/debug/html`
- ✅ Updated button selectors for current Dreamina UI
- ✅ Better wait conditions and scroll-into-view
- ✅ Support for all Dreamina models (Image 4.0, Nano Banana, Image 3.1, etc.)

## Quick Diagnostic Checklist

- [ ] Check `/api/health` - Is authentication working?
- [ ] Check `/api/debug/screenshot` - What does the browser see?
- [ ] Check `fly logs` - Any error messages?
- [ ] Check cookies freshness - When were they last updated?
- [ ] Try local Docker test - Does it work in Docker locally?

## Still Having Issues?

If you're still stuck after trying these steps:

1. Share the debug screenshot
2. Share the relevant logs from `fly logs`
3. Share the output from `/api/health`
4. Check if the Dreamina website structure has changed recently

The most common causes are:
- **Expired cookies** (90% of issues) → Refresh cookies
- **UI changes on Dreamina** → Update button selectors based on debug HTML
- **Memory issues** → Increase Fly.io instance size
- **Network issues** → Check Fly.io status page
