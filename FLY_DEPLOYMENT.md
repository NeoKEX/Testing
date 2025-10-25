# Fly.io Deployment Guide for Dreamina API

This guide will help you deploy the Dreamina API server to Fly.io using email/password authentication.

## Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io
2. **Fly CLI**: Install the Fly.io command-line tool
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```
3. **Dreamina Account**: Valid email and password for Dreamina login

## Deployment Steps

### 1. Login to Fly.io
```bash
fly auth login
```

### 2. Create Your Fly App
```bash
fly apps create dreamina-api
# Or use a custom name: fly apps create your-custom-name
```

### 3. Set Your Dreamina Credentials as Secrets

```bash
fly secrets set DREAMINA_EMAIL="your_email@example.com"
fly secrets set DREAMINA_PASSWORD="your_password"
```

**Important**: Replace `your_email@example.com` and `your_password` with your actual Dreamina credentials.

### 4. Deploy Your App

```bash
fly deploy
```

This will:
- Build the Docker image
- Deploy to Fly.io
- Start your application

### 5. Check Your Deployment

```bash
# View your app status
fly status

# View logs
fly logs

# Open your app in browser
fly open
```

Your API will be available at: `https://your-app-name.fly.dev`

## Testing Your API

### Health Check
```bash
curl https://your-app-name.fly.dev/api/health
```

Expected response:
```json
{
  "status": "success",
  "authenticated": true,
  "message": "Service is healthy and authenticated"
}
```

### Generate Images
```bash
curl "https://your-app-name.fly.dev/api/generate/image-4.0?prompt=a%20beautiful%20sunset"
```

## Configuration

### Regions
By default, the app deploys to Singapore (`sin`). Change the region in `fly.toml`:

```toml
primary_region = "sin"  # Singapore
# primary_region = "lax"  # Los Angeles
# primary_region = "fra"  # Frankfurt
# primary_region = "syd"  # Sydney
```

View all regions: `fly platform regions`

### Scaling

#### Memory Requirements
**IMPORTANT**: Chrome requires at least 2GB of memory to run reliably. The `fly.toml` is pre-configured with 2GB.

If you need to adjust:
```bash
fly scale memory 2048  # 2GB (recommended)
fly scale memory 1024  # 1GB (minimum, may be unstable)
```

#### Keep App Running (Disable auto-stop)
Edit `fly.toml`:
```toml
[http_service]
  min_machines_running = 1  # Keep 1 instance always running
```

Then redeploy: `fly deploy`

### Environment Variables

View current secrets:
```bash
fly secrets list
```

Update credentials:
```bash
fly secrets set DREAMINA_EMAIL="new_email@example.com"
fly secrets set DREAMINA_PASSWORD="new_password"
```

## Cost

Fly.io offers:
- **Free tier**: 3 shared-cpu-1x 256MB VMs with 160GB outbound transfer
- **Pricing**: See https://fly.io/docs/about/pricing/

With `auto_stop_machines = true`, your app will stop when not in use, saving costs.

## Troubleshooting

### Authentication Failed

If you see authentication errors in the logs:

1. **Verify credentials**:
   ```bash
   fly secrets list
   ```
   Make sure both `DREAMINA_EMAIL` and `DREAMINA_PASSWORD` are set.

2. **Check logs** for detailed error messages:
   ```bash
   fly logs
   ```

3. **Test manually**: Try logging into https://dreamina.capcut.com with your credentials

4. **Update credentials** if needed:
   ```bash
   fly secrets set DREAMINA_EMAIL="your_email@example.com"
   fly secrets set DREAMINA_PASSWORD="your_password"
   fly apps restart dreamina-api
   ```

### View Logs
```bash
fly logs
```

Look for messages like:
- "Starting automated email login..."
- "✓ Login successful!"
- "Authentication check PASSED"

### SSH into Your App
```bash
fly ssh console
```

### Check App Status
```bash
fly status
```

### Restart App
```bash
fly apps restart dreamina-api
```

### View Resource Usage
```bash
fly dashboard
```

## Updating Your App

1. Make changes to your code
2. Commit changes
3. Run `fly deploy`

## Deleting Your App

```bash
fly apps destroy dreamina-api
```

## Security Notes

- **Never commit credentials** - Use Fly.io secrets exclusively
- Secrets are encrypted and secure
- Monitor your app's logs for authentication errors
- Consider rotating credentials periodically

## Performance Tips

1. **First request may be slow**: The app auto-stops when idle. First request after idle will wake it up (takes ~10-30 seconds)
2. **Subsequent requests**: Much faster once the app is running
3. **Keep warm**: If you need consistent performance, set `min_machines_running = 1` in `fly.toml`

## Support

- Fly.io Docs: https://fly.io/docs/
- Fly.io Community: https://community.fly.io/
- Dreamina API Issues: Check your logs with `fly logs`
