# Push to GitHub and Deploy to Vercel

## ✅ Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `archive-page-scraper` (or your choice)
3. Description: "Archive.org page number scraper with web interface"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## ✅ Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these (replace YOUR_USERNAME and YOUR_REPO_NAME):

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## ✅ Step 3: Deploy to Vercel

### Option A: Via Dashboard (Easiest)

1. Go to https://vercel.com/dashboard
2. Sign up/Login (use GitHub for easy connection)
3. Click "Add New..." → "Project"
4. Import your GitHub repository
5. Configure:
   - Framework Preset: **Other**
   - Root Directory: `./` (default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`
6. Click "Deploy"
7. Wait 1-2 minutes
8. Your app is live! 🎉

### Option B: Via CLI

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

## Your App URL

After deployment, your app will be available at:
`https://your-app-name.vercel.app`

