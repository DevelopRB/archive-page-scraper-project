# Quick Start Guide

## Push to GitHub

### Option 1: Using Git Commands

1. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

2. **Add all files**:
   ```bash
   git add .
   ```

3. **Create initial commit**:
   ```bash
   git commit -m "Initial commit: Archive.org page number scraper"
   ```

4. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Create repository (don't initialize with README)
   - Copy the repository URL

5. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### Option 2: Using GitHub Desktop

1. Download [GitHub Desktop](https://desktop.github.com/)
2. File → Add Local Repository
3. Select this folder
4. Click "Publish repository" to GitHub

## Deploy to Vercel

### Option 1: Via Dashboard (Easiest)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Sign up/Login** (free account works, can use GitHub)
3. **Click "Add New..." → "Project"**
4. **Import your GitHub repository**
5. **Configure** (usually auto-detected):
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Install Command: `pip install -r requirements.txt`
6. **Click "Deploy"**
7. **Wait 1-2 minutes** for deployment
8. **Your app is live!** 🎉

### Option 2: Via CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# For production
vercel --prod
```

## Important Notes

- **Vercel Free Plan**: 
  - 100GB bandwidth/month
  - Serverless functions (fast cold starts)
  - Perfect for this app!
  
- **File Storage**: 
  - Results files are temporary (stored in `/tmp`)
  - Files are cleared after function execution
  - Users should download results immediately
  
- **Logs**: Check Vercel dashboard → Functions → Logs if issues occur

## Troubleshooting

**Build fails?**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility (3.12 recommended)
- Check Vercel build logs in dashboard

**App crashes?**
- Check Vercel function logs in dashboard
- Verify `vercel.json` configuration
- Check serverless function timeout limits

**Files not downloading?**
- Files are temporary (stored in `/tmp`)
- Users must download immediately
- Consider cloud storage for persistence

**Need help?**
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Review Vercel documentation: https://vercel.com/docs

