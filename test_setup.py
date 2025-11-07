"""
Quick test script to verify the Faculty Scraper setup
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        print("  ✗ requests - Run: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("  ✓ beautifulsoup4")
    except ImportError:
        print("  ✗ beautifulsoup4 - Run: pip install beautifulsoup4")
        return False
    
    try:
        from google import genai
        print("  ✓ google-genai")
    except ImportError:
        print("  ✗ google-genai - Run: pip install google-genai")
        return False
    
    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - Run: pip install pandas")
        return False
    
    try:
        import openpyxl
        print("  ✓ openpyxl")
    except ImportError:
        print("  ✗ openpyxl - Run: pip install openpyxl")
        return False
    
    return True

def test_config():
    """Test if config.json exists and is valid"""
    print("\nTesting configuration...")
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("  ✗ config.json not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if 'gemini_api_key' not in config:
            print("  ✗ gemini_api_key not found in config.json")
            return False
        
        if config['gemini_api_key'] == "your-api-key-here":
            print("  ⚠ Please update your API key in config.json")
            return False
        
        print("  ✓ config.json is valid")
        return True
        
    except json.JSONDecodeError:
        print("  ✗ config.json is not valid JSON")
        return False

def test_urls_file():
    """Test if urls.txt exists"""
    print("\nTesting input file...")
    urls_file = Path("urls.txt")
    
    if not urls_file.exists():
        print("  ✗ urls.txt not found")
        return False
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("  ⚠ urls.txt is empty")
            return False
        
        print(f"  ✓ Found {len(urls)} URLs in urls.txt")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading urls.txt: {e}")
        return False

def test_api_connection():
    """Test connection to Gemini API"""
    print("\nTesting API connection...")
    
    try:
        config_file = Path("config.json")
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('gemini_api_key')
        
        if api_key == "your-api-key-here":
            print("  ⚠ Skipping API test - please update your API key")
            return True
        
        from google import genai
        
        # Initialize client with API key
        client = genai.Client(api_key=api_key)
        print("  ✓ Successfully connected to Gemini API")
        
        # Try a simple test with the new API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Say 'test successful' if you can read this."
        )
        if response.text:
            print("  ✓ API is responding correctly")
            return True
        else:
            print("  ⚠ API responded but with empty content")
            return False
            
    except Exception as e:
        print(f"  ✗ API connection failed: {e}")
        print("     Please check your API key and internet connection")
        return False

def main():
    print("=" * 60)
    print("Faculty Scraper - Setup Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
        print("\nℹ Install missing packages with: pip install -r requirements.txt")
    
    if not test_config():
        all_passed = False
    
    if not test_urls_file():
        all_passed = False
    
    # Only test API if other tests passed
    if all_passed:
        if not test_api_connection():
            all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! You're ready to run the scraper.")
        print("\nRun the scraper with: python faculty_scraper.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
