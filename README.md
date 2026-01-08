# Archive.org Page Number Scraper

A Python script and web application to scrape page numbers from archive.org book pages using identifier IDs.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Features

- Extract total page numbers from archive.org book pages
- Support for single or multiple identifiers
- **Web-based frontend** with modern UI
- Command-line interface for batch processing
- Input from command line, file, or interactive mode
- Save results to JSON file
- Error handling and progress tracking

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start (Web Interface)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the web server:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

4. Enter your identifier IDs (one per line) or upload a file, then click "Start Scraping"

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

1. Start the Flask web server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://localhost:5000
```

3. Enter identifier IDs in the text area (one per line) or upload a file
4. Click "Start Scraping" to begin
5. View results in the table and download as JSON if needed

The web interface provides:
- ✨ Modern, responsive UI with gradient design
- 📊 Real-time progress indication
- 📋 Results table with clickable links to archive.org pages
- 📈 Summary statistics (total, successful, failed)
- 📁 Drag-and-drop file upload support
- 💾 Download results as JSON file
- 🎨 Clean and intuitive user experience

### Command-Line Interface

### Single Identifier

```bash
python scrape_page_numbers.py 04315104.1697
```

### Multiple Identifiers

```bash
python scrape_page_numbers.py 04315104.1697 04315104.1698 04315104.1699
```

### From File

Create a text file `ids.txt` with one identifier per line:

```
04315104.1697
04315104.1698
04315104.1699
```

Then run:

```bash
python scrape_page_numbers.py --file ids.txt
```

### Save Results to Custom File

```bash
python scrape_page_numbers.py --file ids.txt --output my_results.json
```

### Rate Limiting

To prevent overloading archive.org servers, the script includes rate limiting:

```bash
# Use custom delay (in seconds) between requests
python scrape_page_numbers.py --file ids.txt --delay 2.0

# Default delay is 1.5 seconds (minimum is 0.5 seconds)
python scrape_page_numbers.py --file ids.txt --delay 1.5
```

**Note**: The default delay of 1.5 seconds is recommended to be respectful to archive.org servers. For heavy usage, consider increasing the delay to 2-3 seconds.

### Interactive Mode

If no identifiers are provided, the script will prompt you to enter them interactively:

```bash
python scrape_page_numbers.py
```

### Output JSON to Console

```bash
python scrape_page_numbers.py 04315104.1697 --json
```

## Output

The script generates a JSON file (default: `results.json`) with the following structure:

```json
[
  {
    "identifier": "04315104.1697",
    "url": "https://archive.org/details/04315104.1697.emory.edu",
    "page_number": 133,
    "success": true,
    "error": null
  },
  {
    "identifier": "04315104.1698",
    "url": "https://archive.org/details/04315104.1698.emory.edu",
    "page_number": null,
    "success": false,
    "error": "404 Client Error: Not Found"
  }
]
```

## How It Works

1. The script constructs URLs using the format: `https://archive.org/details/{identifier}` (identifier used as-is)
2. It tries multiple methods to extract page numbers (in order of reliability):
   - **Method 1**: Fetches `scandata.xml` file and extracts `<leafCount>` (most reliable for older books)
   - **Method 2**: Fetches `page_numbers.json` file from archive.org (for newer books)
   - **Method 3**: Searches for the JSON file link in the HTML page
   - **Method 4**: Uses archive.org metadata API to count page-related files
   - **Last resort**: Attempts HTML parsing (limited for JavaScript-rendered content)

## Supported Identifier Formats

The script supports various identifier formats from archive.org:

- **Numeric IDs**: `39088000610261`, `39088005796651`
- **IDs with domains**: `04315104.1697.emory.edu`, `14110158.5437.emory.edu`
- **Text identifiers**: `1841Minutes`, `1845IndianaMinutes`, `ABriefHistoryOfTheRocket`
- **Mixed formats**: `191063024.5807.emory.edu`, `2008HighPointUniversityZenithYearbook`

The identifier is used exactly as provided in the URL: `https://archive.org/details/{identifier}`

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- lxml (optional, but recommended for faster parsing)

## Notes

- The script includes proper error handling for network issues and missing pages
- A user agent header is used to avoid blocking
- The script handles duplicate identifiers automatically
- **Rate limiting**: Default 1.5 second delay between requests to prevent overloading archive.org servers
  - Configurable via `--delay` flag in CLI (minimum 0.5 seconds)
  - Web interface uses default 1.5 second delay
  - For heavy usage, consider increasing delay to 2-3 seconds

## Deployment

### Deploy to Vercel

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   
   **Option A: Via Dashboard (Recommended)**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Click "Deploy" (Vercel auto-detects Python)
   - Your app will be live at: `https://your-app-name.vercel.app`
   
   **Option B: Via CLI**
   ```bash
   npm i -g vercel
   vercel login
   vercel
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Note**: Results files are temporary on Vercel (stored in `/tmp`). Users should download results immediately after scraping.

### Local Development

```bash
python app.py
```

The app will be available at `http://localhost:5000`

