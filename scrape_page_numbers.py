"""
Archive.org Page Number Scraper
Scrapes page numbers from archive.org book pages using the identifier ID.
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import json
import time
from typing import Optional, List, Dict
import argparse
import pandas as pd
from datetime import datetime

# Rate limiting configuration
DEFAULT_DELAY_SECONDS = 1.5  # Default delay between requests (1.5 seconds)
MIN_DELAY_SECONDS = 0.5  # Minimum delay to prevent too aggressive scraping


def construct_url(identifier: str) -> str:
    """
    Construct the archive.org URL from the identifier.
    
    Args:
        identifier: The identifier ID (e.g., "04315104.1697", "39088000610261", "1841Minutes")
    
    Returns:
        The full URL to the archive.org details page
    """
    # Use identifier as-is (it may already include .emory.edu or be plain text/numeric)
    return f"https://archive.org/details/{identifier}"


def get_page_number_from_scandata(identifier: str) -> Optional[int]:
    """
    Try to get page number from archive.org's scandata.xml file.
    This file contains leafCount which is the total number of pages.
    
    Args:
        identifier: The identifier ID
    
    Returns:
        The total page number if found, None otherwise
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Method 1: Try to find scandata file from metadata API (most reliable)
    try:
        metadata_url = f"https://archive.org/metadata/{identifier}"
        response = requests.get(metadata_url, headers=headers, timeout=10)
        if response.status_code == 200:
            metadata = json.loads(response.text)
            files = metadata.get('files', [])
            
            # Find scandata files (both .xml and .zip)
            scandata_files = [f for f in files if 'scandata' in f.get('name', '').lower() and 
                             (f.get('name', '').endswith('.xml') or f.get('name', '').endswith('.zip'))]
            
            # Try each scandata file found
            for file_info in scandata_files:
                scandata_name = file_info.get('name')
                scandata_url = f"https://archive.org/download/{identifier}/{scandata_name}"
                try:
                    scandata_response = requests.get(scandata_url, headers=headers, timeout=10)
                    if scandata_response.status_code == 200:
                        # Handle ZIP files
                        if scandata_name.endswith('.zip'):
                            import zipfile
                            import io
                            try:
                                zip_file = zipfile.ZipFile(io.BytesIO(scandata_response.content))
                                # Look for scandata.xml in the ZIP
                                xml_files = [f for f in zip_file.namelist() if f.endswith('scandata.xml')]
                                if xml_files:
                                    xml_content = zip_file.read(xml_files[0]).decode('utf-8')
                                    soup = BeautifulSoup(xml_content, 'xml')
                                    leaf_count = soup.find('leafCount')
                                    if leaf_count and leaf_count.string:
                                        try:
                                            return int(leaf_count.string.strip())
                                        except ValueError:
                                            continue
                            except Exception:
                                continue
                        else:
                            # Handle XML files directly
                            soup = BeautifulSoup(scandata_response.text, 'xml')
                            leaf_count = soup.find('leafCount')
                            if leaf_count and leaf_count.string:
                                try:
                                    return int(leaf_count.string.strip())
                                except ValueError:
                                    continue
                except Exception:
                    continue
    except Exception:
        pass
    
    # Method 2: Try standard pattern {identifier}_scandata.xml
    try:
        scandata_url = f"https://archive.org/download/{identifier}/{identifier}_scandata.xml"
        response = requests.get(scandata_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            leaf_count = soup.find('leafCount')
            if leaf_count and leaf_count.string:
                try:
                    return int(leaf_count.string.strip())
                except ValueError:
                    pass
    except Exception:
        pass
    
    return None


def get_page_number_from_json(identifier: str) -> Optional[int]:
    """
    Try to get page number from archive.org's page_numbers.json file.
    Handles different identifier formats and tries multiple URL patterns.
    
    Args:
        identifier: The identifier ID (various formats)
    
    Returns:
        The total page number if found, None otherwise
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Try multiple patterns for finding the page_numbers.json file
    patterns_to_try = []
    
    # Pattern 1: {identifier}/{identifier_underscores}_page_numbers.json
    identifier_underscores = identifier.replace('.', '_').replace('-', '_')
    patterns_to_try.append(f"https://archive.org/download/{identifier}/{identifier_underscores}_page_numbers.json")
    
    # Pattern 2: If identifier contains dots, try splitting and reconstructing
    if '.' in identifier:
        parts = identifier.split('.')
        if len(parts) >= 2:
            # For identifiers like "04315104.1697.emory.edu" -> "04315104_1697_page_numbers.json"
            base_parts = [p for p in parts if p != 'emory' and p != 'edu']
            if base_parts:
                base_underscores = '_'.join(base_parts)
                patterns_to_try.append(f"https://archive.org/download/{identifier}/{base_underscores}_page_numbers.json")
    
    # Pattern 3: Try finding the JSON link in the HTML page
    try:
        details_url = f"https://archive.org/details/{identifier}"
        response = requests.get(details_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all links to page_numbers.json
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'page_numbers.json' in href:
                    # Convert relative URL to absolute
                    if href.startswith('/'):
                        json_url = f"https://archive.org{href}"
                    else:
                        json_url = href
                    patterns_to_try.insert(0, json_url)  # Prioritize this pattern
    except Exception:
        pass
    
    # Try all patterns
    for json_url in patterns_to_try:
        try:
            response = requests.get(json_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = json.loads(response.text)
                pages = data.get('pages', [])
                if pages:
                    return len(pages)
        except Exception:
            continue
    
    return None


def get_page_number_from_metadata(identifier: str) -> Optional[int]:
    """
    Try to get page number from archive.org's metadata API.
    Looks for JP2 ZIP files and counts pages from scandata or file patterns.
    
    Args:
        identifier: The identifier ID
    
    Returns:
        The total page number if found, None otherwise
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        metadata_url = f"https://archive.org/metadata/{identifier}"
        response = requests.get(metadata_url, headers=headers, timeout=10)
        if response.status_code == 200:
            metadata = json.loads(response.text)
            files = metadata.get('files', [])
            
            # Look for JP2 ZIP files (these contain page images)
            jp2_files = [f for f in files if 'jp2' in f.get('name', '').lower() or 
                         f.get('format') == 'Single Page Processed JP2 ZIP']
            
            # Look for page number files (JPEG images of pages)
            page_images = [f for f in files if f.get('format') in ['JPEG', 'JPEG Thumb'] 
                          and ('page' in f.get('name', '').lower() or f.get('name', '').endswith(('.jpg', '.jpeg')))]
            
            # Try to extract page numbers from filenames
            if page_images:
                max_page = 0
                for f in page_images:
                    name = f.get('name', '')
                    # Look for page numbers in filename (e.g., page_001.jpg, p123.jpg, etc.)
                    page_match = re.search(r'page[_-]?(\d+)', name, re.IGNORECASE)
                    if page_match:
                        page_num = int(page_match.group(1))
                        max_page = max(max_page, page_num)
                
                # If we found page numbers in filenames, use that
                if max_page > 0:
                    return max_page
                
                # Otherwise, count unique page-related files
                return len(page_images)
    except Exception:
        pass
    
    return None


def extract_page_number(html_content: str, identifier: str) -> Optional[int]:
    """
    Extract the total page number from the HTML content.
    
    Tries multiple methods in order of reliability:
    1. scandata.xml (contains leafCount - most reliable)
    2. page_numbers.json file
    3. Metadata API
    4. HTML parsing (fallback)
    
    Args:
        html_content: The HTML content of the page
        identifier: The identifier ID for constructing URLs
    
    Returns:
        The total page number if found, None otherwise
    """
    # Method 1: Try to parse HTML first (most accurate - shows displayed page count)
    # This gets the displayed page count which matches what users see (e.g., "1/268")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # First, search the entire HTML content for page number patterns
    # This catches dynamically loaded content and various formats
    html_text = html_content
    
    # Look for patterns like "(1/268)", "Page — (1/268)", etc.
    # Find all matches and use the one with the highest total (most likely to be correct)
    page_patterns = re.findall(r'\((\d+)/(\d+)\)', html_text)
    if page_patterns:
        # Get the maximum total page number found
        max_total = max(int(total) for current, total in page_patterns)
        # Only use if it's a reasonable number (more than 1)
        if max_total > 1:
            return max_total
    
    # Also search for "of" patterns like "(1 of 268)"
    of_patterns = re.findall(r'\((\d+)\s+of\s+(\d+)\)', html_text, re.IGNORECASE)
    if of_patterns:
        max_total = max(int(total) for current, total in of_patterns)
        if max_total > 1:
            return max_total
    
    # Try to find the span element with class "BRcurrentpage BRmax"
    span_element = soup.find('span', class_='BRcurrentpage BRmax')
    if span_element:
        text = span_element.get_text(strip=True)
        match = re.search(r'\((\d+)/(\d+)\)', text)
        if match:
            total_pages = int(match.group(2))  # group(2) is the total
            return total_pages
    
    # Try to find BRcurrentpage BRmin element
    span_element_min = soup.find('span', class_='BRcurrentpage BRmin')
    if span_element_min:
        text = span_element_min.get_text(strip=True)
        match = re.search(r'\((\d+)\s+of\s+(\d+)\)', text, re.IGNORECASE)
        if match:
            total_pages = int(match.group(2))  # group(2) is the total
            return total_pages
    
    # Search for any element with BRcurrentpage class
    all_current_page = soup.find_all(class_=re.compile('BRcurrentpage'))
    for element in all_current_page:
        text = element.get_text(strip=True)
        match = re.search(r'\((\d+)/(\d+)\)', text)
        if match:
            total_pages = int(match.group(2))  # group(2) is the total
            return total_pages
        match = re.search(r'\((\d+)\s+of\s+(\d+)\)', text, re.IGNORECASE)
        if match:
            total_pages = int(match.group(2))  # group(2) is the total
            return total_pages
    
    # Method 2: Try to get from page_numbers.json
    page_count = get_page_number_from_json(identifier)
    if page_count:
        return page_count
    
    # Method 3: Try scandata.xml (may include covers/blank pages, so less accurate than HTML)
    page_count = get_page_number_from_scandata(identifier)
    if page_count:
        return page_count
    
    # Method 4: Try metadata API
    page_count = get_page_number_from_metadata(identifier)
    if page_count:
        return page_count
    
    return None


def scrape_page_number(identifier: str) -> Dict[str, any]:
    """
    Scrape the page number for a given identifier.
    
    Args:
        identifier: The identifier ID to scrape
    
    Returns:
        A dictionary with identifier, url, page_number, and success status
    """
    url = construct_url(identifier)
    
    try:
        # Send GET request with a user agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        page_number = extract_page_number(response.text, identifier)
        
        if page_number is None:
            # Try one more time with a direct metadata check if all methods failed
            # This handles edge cases where the page loads but methods don't work
            try:
                metadata_url = f"https://archive.org/metadata/{identifier}"
                metadata_response = requests.get(metadata_url, headers=headers, timeout=10)
                if metadata_response.status_code == 200:
                    metadata = json.loads(metadata_response.text)
                    files = metadata.get('files', [])
                    # Look for any page-related files as last resort
                    # But don't count ZIP files as individual pages - they contain multiple pages
                    page_files = [f for f in files if f.get('format') == 'JPEG' and 'page' in f.get('name', '').lower()]
                    if page_files:
                        # Try to extract from filenames - get the maximum page number
                        max_page = 0
                        for f in page_files:
                            name = f.get('name', '')
                            # Look for patterns like page_001, page001, p001, etc.
                            page_match = re.search(r'page[_-]?(\d+)', name, re.IGNORECASE)
                            if page_match:
                                page_num = int(page_match.group(1))
                                max_page = max(max_page, page_num)
                        # Only use if we found a reasonable page number (more than 1)
                        if max_page > 1:
                            page_number = max_page
            except Exception:
                pass  # Silently fail if this fallback doesn't work
        
        return {
            'identifier': identifier,
            'url': url,
            'page_number': page_number,
            'success': page_number is not None,
            'error': None if page_number is not None else 'Page number could not be extracted from available sources'
        }
    
    except requests.exceptions.HTTPError as e:
        # Handle 404 and other HTTP errors more gracefully
        error_msg = str(e)
        if '404' in error_msg:
            error_msg = f"Identifier not found (404) - URL may be incorrect or item doesn't exist"
        return {
            'identifier': identifier,
            'url': url,
            'page_number': None,
            'success': False,
            'error': error_msg
        }
    except requests.exceptions.RequestException as e:
        return {
            'identifier': identifier,
            'url': url,
            'page_number': None,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'identifier': identifier,
            'url': url,
            'page_number': None,
            'success': False,
            'error': str(e)
        }


def read_ids_from_file(filename: str) -> List[str]:
    """
    Read identifiers from a text file (one per line).
    
    Args:
        filename: Path to the file containing identifiers
    
    Returns:
        List of identifier strings
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            ids = [line.strip() for line in f if line.strip()]
        return ids
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []


def save_results(results: List[Dict], output_file: str = 'results.xlsx'):
    """
    Save scraping results to an Excel file.
    
    Args:
        results: List of result dictionaries
        output_file: Output filename (should be .xlsx)
    """
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
    
    # Create DataFrame
    df = pd.DataFrame(excel_data)
    
    # Ensure output file has .xlsx extension
    if not output_file.endswith('.xlsx'):
        output_file = output_file.rsplit('.', 1)[0] + '.xlsx'
    
    # Save to Excel
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Results']
            
            # Auto-adjust column widths
            from openpyxl.utils import get_column_letter
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                )
                column_letter = get_column_letter(idx)
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"\nError saving to Excel: {e}")
        print("Falling back to JSON format...")
        json_file = output_file.replace('.xlsx', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {json_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape page numbers from archive.org books',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single ID from command line
  python scrape_page_numbers.py 04315104.1697
  
  # Multiple IDs from file
  python scrape_page_numbers.py --file ids.txt
  
  # Multiple IDs from command line
  python scrape_page_numbers.py 04315104.1697 04315104.1698 04315104.1699
  
  # Save results to file
  python scrape_page_numbers.py --file ids.txt --output results.json
        """
    )
    
    parser.add_argument(
        'identifiers',
        nargs='*',
        help='One or more identifier IDs to scrape (e.g., 04315104.1697)'
    )
    parser.add_argument(
        '--file',
        '-f',
        type=str,
        help='Path to a text file containing identifiers (one per line)'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        default='results.xlsx',
        help='Output file to save results (default: results.xlsx)'
    )
    parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output results as JSON to stdout (also saves Excel file)'
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help=f'Delay in seconds between requests (default: {DEFAULT_DELAY_SECONDS}s, minimum: {MIN_DELAY_SECONDS}s)'
    )
    
    args = parser.parse_args()
    
    # Validate delay
    delay = max(args.delay, MIN_DELAY_SECONDS)
    if args.delay < MIN_DELAY_SECONDS:
        print(f"Warning: Delay {args.delay}s is below minimum {MIN_DELAY_SECONDS}s. Using {MIN_DELAY_SECONDS}s instead.")
    
    # Collect identifiers from command line and/or file
    identifiers = []
    
    if args.identifiers:
        identifiers.extend(args.identifiers)
    
    if args.file:
        file_ids = read_ids_from_file(args.file)
        identifiers.extend(file_ids)
    
    # If no identifiers provided, prompt interactively
    if not identifiers:
        print("No identifiers provided. Enter identifiers (one per line, empty line to finish):")
        while True:
            identifier = input().strip()
            if not identifier:
                break
            identifiers.append(identifier)
    
    if not identifiers:
        print("Error: No identifiers provided.")
        parser.print_help()
        sys.exit(1)
    
    # Remove duplicates while preserving order
    seen = set()
    identifiers = [id for id in identifiers if id not in seen and not seen.add(id)]
    
    print(f"Scraping page numbers for {len(identifiers)} identifier(s)...")
    print(f"Rate limit: {delay} seconds between requests\n")
    
    results = []
    for i, identifier in enumerate(identifiers, 1):
        # Add delay before processing (except for the first one)
        if i > 1:
            time.sleep(delay)
        
        print(f"[{i}/{len(identifiers)}] Processing: {identifier}")
        result = scrape_page_number(identifier)
        results.append(result)
        
        if result['success']:
            print(f"  ✓ Found {result['page_number']} pages")
        else:
            error_msg = result.get('error', 'Page number not found')
            print(f"  ✗ Error: {error_msg}")
    
    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['success'])
    print(f"Total processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print("\nResults:")
    for result in results:
        status = f"✓ {result['page_number']} pages" if result['success'] else f"✗ {result.get('error', 'Not found')}"
        print(f"  {result['identifier']}: {status}")
    
    # Save results
    save_results(results, args.output)
    
    # Output JSON if requested
    if args.json:
        print("\nJSON Output:")
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

