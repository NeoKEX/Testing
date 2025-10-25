# Fly.io Deployment Guide for Dreamina API

This guide will help you deploy the Dreamina API server to Fly.io.

## Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io
2. **Fly CLI**: Install the Fly.io command-line tool
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```
3. **Dreamina Cookies**: Valid cookies from your Dreamina account in `account.json` format

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

### 3. Add Your Dreamina Cookies as a Secret File

Fly.io doesn't support secret files like Render, so we'll use secrets:

```bash
# Convert your account.json to a base64 string
cat account.json | base64 > account_base64.txt

# Set it as a secret
fly secrets set ACCOUNT_JSON_BASE64="$(cat account_base64.txt)"

# Clean up the temporary file
rm account_base64.txt
```

**Alternative Method (Simpler):**
```bash
# Set the JSON directly as a secret (escape quotes)
fly secrets set ACCOUNT_JSON='[{"name":"cookie_name","value":"cookie_value","domain":".dreamina.capcut.com"}]'
```

### 4. Update Code to Read from Secret

The app is already configured to read from the secret. It will:
- First try to read `account.json` file
- If not found, read from `ACCOUNT_JSON` or `ACCOUNT_JSON_BASE64` environment variable

### 5. Deploy Your App

```bash
fly deploy
```

This will:
- Build the Docker image
- Deploy to Fly.io
- Start your application

### 6. Check Your Deployment

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

#### Adjust Memory (if needed)
```bash
fly scale memory 1024  # Increase to 1GB
```

#### Keep App Running (Disable auto-stop)
Edit `fly.toml`:
```toml
[http_service]
  min_machines_running = 1  # Keep 1 instance always running
```

Then redeploy: `fly deploy`

### Environment Variables

Set additional environment variables:
```bash
fly secrets set MY_VAR=my_value
```

View current secrets:
```bash
fly secrets list
```

## Cost

Fly.io offers:
- **Free tier**: 3 shared-cpu-1x 256MB VMs with 160GB outbound transfer
- **Pricing**: See https://fly.io/docs/about/pricing/

With `auto_stop_machines = true`, your app will stop when not in use, saving costs.

## Troubleshooting

### View Logs
```bash
fly logs
```

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

## Support

- Fly.io Docs: https://fly.io/docs/
- Fly.io Community: https://community.fly.io/
- Dreamina API Issues: Check your logs with `fly logs`

## Security Notes

- **Never commit `account.json`** - It's in `.gitignore`
- Use Fly.io secrets for sensitive data
- Cookies expire - you'll need to refresh them periodically
- Monitor your app's logs for authentication errors
