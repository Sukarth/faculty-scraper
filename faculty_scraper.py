"""
Faculty Scraper - Extracts professor information from university websites using Google Gemini AI
"""

import os
import sys
import logging
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import pandas as pd
from urllib.parse import urlparse
import re


# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_filename = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class FacultyScraper:
    """Main scraper class for extracting professor information from university websites"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, api_key: str):
        """
        Initialize the scraper with Google Gemini API key
        
        Args:
            api_key: Google AI Studio API key
        """
        self.api_key = api_key
        
        # Initialize Gemini client with API key
        self.client = genai.Client(api_key=api_key)
        
        logger.info("Faculty Scraper initialized successfully")
    
    def fetch_webpage_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract text content from a webpage
        
        Args:
            url: URL to fetch
            
        Returns:
            Extracted text content or None if failed
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parse HTML and extract text
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator='\n', strip=True)
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                logger.info(f"Successfully fetched {len(text)} characters from {url}")
                return text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error fetching {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.critical(f"FAILED to fetch {url} after {self.MAX_RETRIES} attempts")
                    return None
    
    def analyze_with_gemini(self, content: str, url: str) -> Optional[str]:
        """
        Send content to Gemini AI for analysis
        
        Args:
            content: Webpage content to analyze
            url: Source URL (for context)
            
        Returns:
            AI response or None if failed
        """
        prompt = f"""You are analyzing a university faculty webpage to extract professor information.

SOURCE URL: {url}

INSTRUCTIONS:
1. Extract ALL professors from the provided webpage content
2. Include professors of ALL TYPES exactly as listed (Professor, Associate Professor, Assistant Professor, etc.)
3. Do NOT include: lecturers, postdocs, researchers, retired or former professors
4. Do NOT include visiting professors
5. If a professor is on leave, include them but add 'on leave' to the notes column
6. Sometimes a professor may be called "Head of Department" or "Chair" - include these
7. If a sublist contains only visiting professors, omit it but note this in a summary

OUTPUT FORMAT:
Provide your response ONLY as a CSV format with exactly these columns: Name,Title,Notes
- Name: Full name of the professor
- Title: Their academic title (e.g., Professor, Associate Professor, Assistant Professor)
- Notes: Any special notes (e.g., "on leave", "head of department")

Do not include any markdown formatting, just plain CSV text.
Start directly with the CSV header line.

WEBPAGE CONTENT:
{content[:50000]}
"""

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Sending content to Gemini AI (Attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                # Use the new API with gemini-2.5-flash
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,  # Low temperature for consistent structured output
                        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for faster response
                    )
                )
                
                if response.text:
                    logger.info(f"Received response from Gemini AI ({len(response.text)} characters)")
                    return response.text
                else:
                    logger.warning("Received empty response from Gemini AI")
                    
            except Exception as e:
                logger.warning(f"Error communicating with Gemini AI: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.critical(f"FAILED to get AI response after {self.MAX_RETRIES} attempts")
                    return None
        
        return None
    
    def parse_csv_response(self, response: str) -> Optional[List[Dict[str, str]]]:
        """
        Parse CSV response from Gemini AI
        
        Args:
            response: AI response containing CSV data
            
        Returns:
            List of dictionaries containing professor data, or None if parsing failed
        """
        try:
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                # Remove first and last lines if they contain ```
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines[-1].startswith('```'):
                    lines = lines[:-1]
                response = '\n'.join(lines)
            
            # Parse CSV
            from io import StringIO
            csv_file = StringIO(response)
            reader = csv.DictReader(csv_file)
            
            data = []
            for row in reader:
                # Ensure required columns exist and have values
                name = row.get('Name', '').strip() if row.get('Name') else ''
                title = row.get('Title', '').strip() if row.get('Title') else ''
                notes = row.get('Notes', '').strip() if row.get('Notes') else ''
                
                # Only include rows with at least a name and title
                if name and title:
                    data.append({
                        'Name': name,
                        'Title': title,
                        'Notes': notes
                    })
            
            logger.info(f"Successfully parsed {len(data)} professor entries")
            return data
            
        except Exception as e:
            logger.critical(f"FAILED to parse CSV response: {e}")
            return None
    
    def extract_university_name(self, url: str) -> str:
        """
        Extract a clean university name from URL for sheet naming
        
        Args:
            url: University website URL
            
        Returns:
            Clean university name suitable for Excel sheet name
        """
        # Parse the URL
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. and common TLDs
        domain = domain.replace('www.', '').replace('www4.', '')
        
        # Extract main domain name (before TLD)
        parts = domain.split('.')
        if len(parts) >= 2:
            # Get the main part (e.g., 'cbs' from 'cbs.dk')
            name = parts[0]
        else:
            name = domain
        
        # Clean up and capitalize
        name = name.upper()
        
        # Excel sheet name limitations: max 31 chars, no special chars
        name = re.sub(r'[\\/*?\[\]:]+', '', name)[:31]
        
        return name
    
    def save_to_excel(self, data_by_url: Dict[str, List[Dict[str, str]]], filename: str, append_mode: bool = False):
        """
        Save professor data to Excel file with separate sheets per university
        
        Args:
            data_by_url: Dictionary mapping URLs to professor data lists
            filename: Output filename
            append_mode: If True, append to existing file; if False, create new file
        """
        try:
            # Determine mode based on whether file exists and append_mode
            mode = 'a' if append_mode and Path(filename).exists() else 'w'
            
            # If appending, we need to load existing data first
            existing_data = {}
            sheet_names_used = {}
            
            if mode == 'a':
                try:
                    # Read existing sheets
                    with pd.ExcelFile(filename, engine='openpyxl') as xls:
                        for sheet_name in xls.sheet_names:
                            existing_data[sheet_name] = pd.read_excel(xls, sheet_name)
                            sheet_names_used[sheet_name] = True
                except Exception as e:
                    logger.warning(f"Could not read existing Excel file for appending: {e}")
                    mode = 'w'
            
            with pd.ExcelWriter(filename, engine='openpyxl', mode=mode, if_sheet_exists='replace' if mode == 'a' else None) as writer:
                # Write existing data back first if appending
                if mode == 'a' and existing_data:
                    for sheet_name, df in existing_data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Add new data
                for url, data in data_by_url.items():
                    if not data:
                        continue
                    
                    # Get base sheet name from URL
                    base_name = self.extract_university_name(url)
                    
                    # Handle duplicate sheet names
                    sheet_name = base_name
                    counter = 1
                    while sheet_name in sheet_names_used:
                        counter += 1
                        # Ensure we don't exceed 31 char limit
                        suffix = f"_{counter}"
                        max_base_len = 31 - len(suffix)
                        sheet_name = base_name[:max_base_len] + suffix
                    
                    sheet_names_used[sheet_name] = True
                    
                    # Create DataFrame and write to sheet
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    logger.info(f"Added sheet '{sheet_name}' with {len(data)} entries")
            
        except Exception as e:
            logger.critical(f"FAILED to save to Excel: {e}")
            raise
    
    def save_raw_response(self, response: str, url: str, output_dir: Path):
        """
        Save raw AI response to text file when parsing fails
        
        Args:
            response: Raw AI response
            url: Source URL
            output_dir: Directory to save file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"raw_response_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Source URL: {url}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write("=" * 80 + "\n\n")
                f.write(response)
            
            logger.info(f"Saved raw response to {filename}")
            print(f"⚠ Parsing failed. Raw response saved to {filename}")
        except Exception as e:
            logger.critical(f"FAILED to save raw response: {e}")
    
    def process_url(self, url: str, output_dir: Path) -> Tuple[str, Optional[List[Dict[str, str]]], Optional[str]]:
        """
        Process a single URL: fetch, analyze, and parse
        
        Args:
            url: URL to process
            output_dir: Directory for saving raw responses
            
        Returns:
            Tuple of (status, data, response_text)
            status: "success", "no_professors", "error"
        """
        logger.info(f"Processing URL: {url}")
        print(f"\nProcessing: {url}")
        
        # Fetch webpage content
        content = self.fetch_webpage_content(url)
        if not content:
            logger.critical(f"FAILED to fetch content from {url}")
            print(f"✗ FAILED to fetch content from {url}")
            return "error", None, None
        
        # Analyze with Gemini
        response = None
        parse_attempts = 0
        while parse_attempts < self.MAX_RETRIES:
            response = self.analyze_with_gemini(content, url)
            
            if not response:
                logger.critical(f"FAILED to get AI response for {url}")
                print(f"✗ FAILED to get AI response for {url}")
                return "error", None, response
            
            # Try to parse the response
            data = self.parse_csv_response(response)
            
            if data is not None:
                if len(data) > 0:
                    logger.info(f"Successfully processed {url} - found {len(data)} professors")
                    print(f"✓ Found {len(data)} professors")
                    return "success", data, response
                else:
                    logger.info(f"Processed {url} - found 0 professors [EMPTY]")
                    print(f"○ Found 0 professors")
                    return "no_professors", data, response
            else:
                parse_attempts += 1
                logger.warning(f"Parsing failed for {url} (Attempt {parse_attempts}/{self.MAX_RETRIES})")
                
                if parse_attempts >= self.MAX_RETRIES:
                    # Save raw response
                    self.save_raw_response(response, url, output_dir)
                    logger.critical(f"FAILED to parse response for {url} after {self.MAX_RETRIES} attempts")
                    print(f"✗ FAILED to parse response for {url}")
                    return "error", None, response
                else:
                    print(f"⚠ Parsing failed, retrying... ({parse_attempts}/{self.MAX_RETRIES})")
                    time.sleep(self.RETRY_DELAY)
        
        return "error", None, response
    
    def process_urls_from_file(self, input_file: str, output_file: str):
        """
        Process all URLs from input file and save results
        
        Args:
            input_file: Path to file containing URLs (one per line)
            output_file: Path to output Excel file
        """
        logger.info(f"Starting batch processing from {input_file}")
        print(f"\n{'='*60}")
        print(f"Faculty Scraper - Starting Processing")
        print(f"{'='*60}")
        
        # Create output directory for raw responses
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Read URLs
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.critical(f"FAILED to read input file: {e}")
            print(f"✗ FAILED to read {input_file}: {e}")
            return
        
        logger.info(f"Found {len(urls)} URLs to process")
        print(f"\nFound {len(urls)} URLs to process\n")
        
        # Process each URL and save immediately
        urls_with_professors = 0
        urls_no_professors = 0
        urls_with_errors = 0
        total_professors = 0
        
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{len(urls)}] ", end="")
            status, data, response_text = self.process_url(url, output_dir)
            
            if status == "success":
                # Save immediately to Excel file
                try:
                    append_mode = idx > 1  # Append for all URLs after the first
                    self.save_to_excel({url: data}, output_file, append_mode=append_mode)
                    urls_with_professors += 1
                    total_professors += len(data)
                    print(f"  ✓ Saved to {output_file}")
                except Exception as e:
                    logger.critical(f"FAILED to save data for {url}: {e}")
                    print(f"  ✗ FAILED to save: {e}")
                    # Save raw response on save failure
                    if response_text:
                        self.save_raw_response(response_text, url, output_dir)
                    urls_with_errors += 1
            elif status == "no_professors":
                urls_no_professors += 1
            else:  # error
                urls_with_errors += 1
            
            # Small delay between requests to be polite
            if idx < len(urls):
                time.sleep(1)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Processing Complete!")
        print(f"{'='*60}")
        print(f"✓ URLs with professors: {urls_with_professors}/{len(urls)} URLs")
        print(f"○ URLs with no professors: {urls_no_professors}/{len(urls)} URLs")
        print(f"✗ URLs with errors: {urls_with_errors}/{len(urls)} URLs")
        print(f"Total professors extracted: {total_professors}")
        if urls_with_professors > 0:
            print(f"Output saved to: {output_file}")
        print(f"Logs saved to: {log_filename}")
        print(f"{'='*60}\n")
        
        logger.info(f"Batch processing complete - {urls_with_professors} with professors, {urls_no_professors} with no professors, {urls_with_errors} with errors, {total_professors} total professors")


def main():
    """Main entry point"""
    print("""
╔═════════════════════════════════════════════════════════╗
║                  Faculty Scraper v1.0                   ║
║     Extract Professor Data from University Websites     ║
║                   By Sukarth Acharya                    ║
║               https://github.com/sukarth                ║
╚═════════════════════════════════════════════════════════╝
    """)
    
    # Load configuration
    config_file = Path("config.json")
    if not config_file.exists():
        logger.critical("FAILED: config.json not found")
        print("✗ Error: config.json not found!")
        print("Please create config.json with your Google AI Studio API key.")
        print("\nExample config.json:")
        print('''{
    "gemini_api_key": "your-api-key-here"
}''')
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('gemini_api_key')
        
        if not api_key or api_key == "your-api-key-here":
            logger.critical("FAILED: Invalid API key in config.json")
            print("✗ Error: Please set a valid gemini_api_key in config.json")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"FAILED to read config.json: {e}")
        print(f"✗ Error reading config.json: {e}")
        sys.exit(1)
    
    # Initialize scraper
    try:
        scraper = FacultyScraper(api_key)
    except Exception as e:
        logger.critical(f"FAILED to initialize scraper: {e}")
        print(f"✗ Error initializing scraper: {e}")
        sys.exit(1)
    
    # Process URLs
    input_file = "urls.txt"
    output_file = f"professors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    if not Path(input_file).exists():
        logger.critical(f"FAILED: {input_file} not found")
        print(f"✗ Error: {input_file} not found!")
        sys.exit(1)
    
    try:
        scraper.process_urls_from_file(input_file, output_file)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\n\n⚠ Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"FAILED: Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
