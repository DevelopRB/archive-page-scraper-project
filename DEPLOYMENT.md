# Deployment Guide

## Deploy to Vercel

### Step 1: Push to GitHub

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: (leave empty - Vercel auto-detects)
   - **Output Directory**: (leave empty)
   - **Install Command**: `pip install -r requirements.txt`
5. Click "Deploy"
6. Wait for deployment (usually 1-2 minutes)
7. Your app will be live at: `https://your-app-name.vercel.app`

#### Option B: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts:
   - Link to existing project? No
   - Project name: archive-page-scraper
   - Directory: ./
   - Override settings? No

5. For production deployment:
```bash
vercel --prod
```

### Important Notes for Vercel:

- **Serverless Functions**: 
  - Vercel uses serverless functions (each request is handled independently)
  - Results files are stored in `/tmp` directory (temporary)
  - Files in `/tmp` are cleared between function invocations
  - Consider using external storage (S3, etc.) for persistent file storage

- **Free Plan Limitations**: 
  - 100GB bandwidth per month
   - Serverless function execution time limits
   - Perfect for this application's use case

- **Environment Variables** (optional):
   - Can be set in Vercel dashboard under Project Settings → Environment Variables
   - `FLASK_DEBUG`: Set to `false` for production

- **File Storage**: 
   - Results files are temporary (stored in `/tmp`)
   - Files are deleted after function execution
   - Users should download results immediately
   - For persistent storage, consider integrating with cloud storage services

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is correct
- Ensure all dependencies are listed
- Check Vercel build logs in dashboard for specific errors
- Verify Python version compatibility (3.12 recommended)

### App Crashes
- Check Vercel function logs in dashboard
- Verify `vercel.json` configuration is correct
- Check that all imports are available
- Review serverless function timeout limits

### File Download Issues
- Files are stored in `/tmp` (temporary)
- Files are cleared after function execution
- Users must download results immediately
- Consider adding cloud storage integration for persistence

### Slow Performance
- Check Vercel function logs for cold start times
- First request may be slower (cold start)
- Subsequent requests are faster (warm functions)
- Consider upgrading plan for better performance

