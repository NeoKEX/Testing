# Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Required Files (All Present ✓)
- [x] `app.py` - Flask application
- [x] `dreamina_service.py` - Selenium automation service
- [x] `requirements.txt` - Python dependencies
- [x] `Dockerfile` - Docker configuration with Chrome/ChromeDriver
- [x] `render.yaml` - Render deployment configuration
- [x] `.dockerignore` - Docker build exclusions
- [x] `account.json.example` - Cookie template
- [x] `README.md` - API documentation

### 2. Configuration Verified ✓
- [x] Port: 8080 (configured in app.py, Dockerfile, render.yaml)
- [x] Docker builds Chrome Stable + ChromeDriver automatically
- [x] FLASK_ENV: production
- [x] Selenium stale element error: FIXED
- [x] Only 2 models enabled: Image 4.0 and Nano Banana

### 3. Code Quality ✓
- [x] Stale element reference error fixed with element refetching
- [x] Proper retry logic in place
- [x] Error handling implemented
- [x] CORS enabled for API access

## 🚀 Deployment Steps

### Step 1: Prepare Repository
```bash
# Ensure all changes are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Web Service
1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/GitLab repository
4. Render auto-detects `render.yaml` configuration

### Step 3: Add Secret File (CRITICAL!)
⚠️ **IMPORTANT**: Your `account.json` file contains sensitive Dreamina cookies and must be added as a secret file in Render.

1. In Render service settings, go to **"Secret Files"**
2. Click **"Add Secret File"**
3. Set filename: `account.json`
4. Paste your cookie JSON content:
```json
{
  "cookies": [
    {
      "name": "your_cookie_name",
      "value": "your_cookie_value",
      "domain": ".capcut.com"
    }
  ]
}
```
5. Click **"Save"**

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for Docker build (5-10 minutes first time)
3. Monitor build logs for any errors

### Step 5: Test Your Deployment
Your API will be available at: `https://YOUR-SERVICE-NAME.onrender.com`

Test endpoints:
```bash
# Health check
curl https://YOUR-SERVICE-NAME.onrender.com/api/health

# Image 4.0 model
curl "https://YOUR-SERVICE-NAME.onrender.com/api/generate/image-4.0?prompt=beautiful%20sunset"

# Nano Banana model
curl "https://YOUR-SERVICE-NAME.onrender.com/api/generate/nano-banana?prompt=cute%20cat"
```

## 📊 Render Free Tier Specifications
- **RAM**: 512 MB (sufficient for basic usage)
- **Build time**: ~5-10 minutes (Chrome + ChromeDriver installation)
- **Cold start**: ~30 seconds after inactivity
- **Requests**: Browser automation is slower than direct APIs (~15-30 seconds per image)

## 🔧 Troubleshooting

### Build Failures
- Check Render build logs for missing dependencies
- Verify Dockerfile syntax is correct
- Ensure requirements.txt has all dependencies

### Authentication Failures
- Verify `account.json` is added as a secret file (not environment variable)
- Check cookie format matches the example
- Cookies may have expired - extract fresh ones from browser

### Service Crashes
- Check Render logs for Chrome/ChromeDriver errors
- Verify Chrome version matches ChromeDriver version
- Check memory usage (may need to upgrade from free tier)

### Slow Performance
- Browser automation inherently slower than APIs
- Free tier has limited resources
- Consider upgrading to paid tier for better performance

## 🎯 Expected Behavior

### Successful Deployment
- Build completes without errors
- Service status: "Live"
- Health endpoint returns `{"authenticated": true}`
- Image generation returns valid image URLs

### Common Issues
1. **Stale element errors**: FIXED in current version
2. **Cookie expiration**: Re-extract cookies and update secret file
3. **Timeout errors**: Increase wait times or retry logic

## 📝 Post-Deployment

### Monitoring
- Check Render logs regularly
- Monitor API response times
- Watch for cookie expiration warnings

### Maintenance
- Update cookies when they expire
- Monitor Chrome/ChromeDriver version compatibility
- Review error logs for issues

### Auto-Deploy
- Render auto-deploys on git push to main branch
- Monitor build status after each push

## 🔒 Security Notes
- Never commit `account.json` to git (already in .gitignore)
- Use Render's secret file feature for sensitive data
- Cookies are treated as passwords
- Consider implementing rate limiting for production use

## ✨ You're Ready to Deploy!
All configuration files are verified and ready for Render deployment.
