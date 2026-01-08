#!/bin/bash
# Quick setup script for GitHub

echo "Setting up Git repository..."

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Archive.org page number scraper with web interface"

echo ""
echo "✓ Files committed"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "2. Run these commands (replace YOUR_USERNAME and YOUR_REPO_NAME):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

