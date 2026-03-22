# Deployment Guide for Render

This guide will help you deploy your NiceGUI Simulation Project to Render.

## Files Created

1. **render.yaml** - Render's Infrastructure as Code configuration
2. **build.sh** - Build script that installs dependencies using Poetry
3. **main.py** - Updated to support production deployment

## Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create a new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Deploy**:
   - Render will use the configuration in `render.yaml`
   - Build command: `bash build.sh`
   - Start command: `python main.py`
   - The app will be available at: `https://simulation-project.onrender.com`

### Option 2: Deploy using Render Blueprint

1. **Push your code to GitHub** (including render.yaml)
2. Go to [Render Blueprints](https://dashboard.render.com/blueprints)
3. Click "New Blueprint Instance"
4. Connect your repository
5. Render will read `render.yaml` and create all services automatically

## Environment Variables

The following environment variables are automatically set by Render:
- `PORT` - The port your application should listen on (automatically configured)
- `RENDER` - Set to "true" when running on Render (used to detect production)

## Key Changes Made

### main.py
- Added `host="0.0.0.0"` to bind to all network interfaces (required for Render)
- Added `port` from environment variable `PORT` (Render assigns this dynamically)
- Disabled `reload` in production using the `RENDER` environment variable
- Still works locally for development (runs on localhost:8080 with reload enabled)

### render.yaml
- Configured Python 3.14 runtime
- Set build and start commands
- Configured health check endpoint
- Enabled auto-deploy on git push

### build.sh
- Installs Poetry
- Installs project dependencies without creating a virtual environment
- Optimized for production (--no-dev flag)

## Testing Locally

Your app still works locally! Just run:
```bash
python main.py
```

It will automatically detect it's not on Render and enable reload mode.

## Troubleshooting

- **Build fails**: Check that `pyproject.toml` has all required dependencies
- **App crashes**: Check Render logs for errors in the dashboard
- **Port issues**: Render automatically sets the PORT env variable - don't hardcode it
- **Dependencies missing**: Add them to `pyproject.toml` and redeploy

## Free Tier Notes

- Render's free tier spins down after 15 minutes of inactivity
- First request after spin down will take 30-60 seconds
- For always-on service, upgrade to a paid plan

## Support

For more information, visit:
- [Render Documentation](https://render.com/docs)
- [NiceGUI Documentation](https://nicegui.io)
