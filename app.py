"""
Flask Web Application for Archive.org Page Number Scraper
"""

from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
import os
import json
import time
import pandas as pd
from scrape_page_numbers import scrape_page_number, construct_url, DEFAULT_DELAY_SECONDS, MIN_DELAY_SECONDS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use /tmp for results file on Vercel (serverless functions have limited write access)
# On local development, use current directory
RESULTS_FILE = os.path.join(os.getenv('TMPDIR', os.getcwd()), 'scraping_results.xlsx')


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape_endpoint():
    """API endpoint to scrape page numbers with progress updates"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    identifiers = data.get('identifiers', [])
    
    if not identifiers:
        return jsonify({'error': 'No identifiers provided'}), 400
    
    # Get delay from request (default to DEFAULT_DELAY_SECONDS)
    delay = max(float(data.get('delay', DEFAULT_DELAY_SECONDS)), MIN_DELAY_SECONDS)
    
    # Remove duplicates while preserving order
    seen = set()
    identifiers = [id for id in identifiers if id not in seen and not seen.add(id)]
    
    total = len(identifiers)
    results = []
    
    @stream_with_context
    def generate():
        """Generate progress updates and results"""
        for index, identifier in enumerate(identifiers):
            # Add rate limiting delay (except for the first request)
            if index > 0:
                time.sleep(delay)
            
            # Send progress update before processing
            progress_percent = int(((index) / total) * 100) if total > 0 else 0
            progress_data = {
                'type': 'progress',
                'current': index,
                'total': total,
                'percent': progress_percent,
                'identifier': identifier,
                'status': 'processing',
                'delay': delay
            }
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Scrape the identifier
            result = scrape_page_number(identifier)
            results.append(result)
            
            # Send result update with updated progress
            completed_percent = int(((index + 1) / total) * 100) if total > 0 else 100
            result_data = {
                'type': 'result',
                'result': result,
                'current': index + 1,
                'total': total,
                'percent': completed_percent
            }
            yield f"data: {json.dumps(result_data)}\n\n"
        
        # Save results to Excel file
        try:
            # Prepare data for Excel
            excel_data = []
            for result in results:
                excel_data.append({
                    'Identifier': result['identifier'],
                    'URL': result['url'],
                    'Page Number': result['page_number'] if result['page_number'] else 'N/A',
                    'Status': 'Success' if result['success'] else 'Failed',
                    'Error': result.get('error', '') if not result['success'] else ''
                })
            
            # Create DataFrame and save to Excel
            df = pd.DataFrame(excel_data)
            with pd.ExcelWriter(RESULTS_FILE, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
                
                # Auto-adjust column widths
                from openpyxl.utils import get_column_letter
                workbook = writer.book
                worksheet = writer.sheets['Results']
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    )
                    column_letter = get_column_letter(idx)
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
        except Exception as e:
            print(f"Error saving results to Excel: {e}")
            # Fallback to JSON if Excel fails
            json_file = RESULTS_FILE.replace('.xlsx', '.json')
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"Saved to JSON instead: {json_file}")
            except Exception as json_error:
                print(f"Error saving to JSON: {json_error}")
        
        # Send final summary
        summary_data = {
            'type': 'complete',
            'results': results,
            'summary': {
                'total': len(results),
                'successful': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success'])
            }
        }
        yield f"data: {json.dumps(summary_data)}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload with identifiers"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            # Read file content
            content = file.read().decode('utf-8')
            identifiers = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Remove duplicates
            seen = set()
            identifiers = [id for id in identifiers if id not in seen and not seen.add(id)]
            
            return jsonify({
                'identifiers': identifiers,
                'count': len(identifiers)
            })
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
    
    return jsonify({'error': 'Error processing file'}), 400


@app.route('/api/download', methods=['GET'])
def download_results():
    """Download results as Excel file"""
    if os.path.exists(RESULTS_FILE):
        return send_file(RESULTS_FILE, as_attachment=True, download_name='results.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        # Check if JSON fallback exists
        json_file = RESULTS_FILE.replace('.xlsx', '.json')
        if os.path.exists(json_file):
            return send_file(json_file, as_attachment=True, download_name='results.json')
        return jsonify({'error': 'No results file found'}), 404


# Vercel serverless function handler
# Vercel will use this when deployed
handler = app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

