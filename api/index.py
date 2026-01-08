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
# This ensures templates and other files are found correctly
original_cwd = os.getcwd()
try:
    os.chdir(parent_dir)
    
    # Import the Flask app from the parent directory
    from app import app
    
    # Vercel expects the handler to be exported
    # The Flask app is WSGI-compatible and works directly with Vercel's Python runtime
    handler = app
    
except Exception as e:
    # If there's an import error, create a simple error handler
    import traceback
    error_msg = f"Failed to import app: {str(e)}\n{traceback.format_exc()}\n\nParent dir: {parent_dir}\nCurrent dir: {os.getcwd()}\nPython path: {sys.path}"
    print(error_msg, file=sys.stderr)
    
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/')
    def error():
        return f"<h1>Import Error</h1><pre>{error_msg}</pre>", 500
    
    handler = error_app
finally:
    # Restore original working directory
    try:
        os.chdir(original_cwd)
    except:
        pass

