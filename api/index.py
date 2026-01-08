"""
Vercel Serverless Function Handler for Archive.org Page Number Scraper
This file is the entry point for Vercel's Python runtime
"""

import sys
import os

# Add parent directory to path to import app and modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change to parent directory so relative paths work correctly
os.chdir(parent_dir)

# Import the Flask app from the parent directory
from app import app

# Vercel expects the handler to be exported
# The Flask app is WSGI-compatible and works directly with Vercel's Python runtime
handler = app

