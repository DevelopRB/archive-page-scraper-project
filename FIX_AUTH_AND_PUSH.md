# Fix Authentication and Push to GitHub

## 🔐 Authentication Issue

You're logged in as: **AbhishekMasand**  
But repository belongs to: **DevelopRB**

## ✅ Solution: Use Personal Access Token

### Step 1: Create Personal Access Token

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill in:
   - **Note**: `archive-scraper-push`
   - **Expiration**: Choose your preference (90 days recommended)
   - **Select scopes**: Check **`repo`** (full control of private repositories)
4. Click **"Generate token"**
5. **⚠️ IMPORTANT**: Copy the token immediately (you won't see it again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Push Using Token

Run this command:
```powershell
git push -u origin main
```

When prompted:
- **Username**: `DevelopRB`
- **Password**: Paste your Personal Access Token (not your GitHub password)

## 🚀 After Successful Push

Your code will be at: https://github.com/DevelopRB/archive-page-scraper-project

Then deploy to Vercel:
1. Go to: https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your repository
4. Click "Deploy"

## 🔄 Alternative: Clear Cached Credentials

If you want to clear old credentials:

```powershell
# Clear Windows credential manager
cmdkey /list
# Find and delete GitHub credentials if needed
cmdkey /delete:git:https://github.com

# Then try push again
git push -u origin main
```

