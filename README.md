# University Faculty Scraper

<center>

An automated tool for extracting professor information from university faculty websites using AI-powered analysis via Google Gemini. Developed for the Aalto University Economics Department.

</center>

## Features

✅ **Smart Web Scraping** - Fetches and extracts clean text from university faculty pages  
✅ **AI-Powered Analysis** - Uses Google Gemini to intelligently identify and extract professor information  
✅ **Robust Error Handling** - Automatic retries for network and parsing errors with configurable timeout  
✅ **Comprehensive Logging** - Detailed logs for debugging and monitoring  
✅ **CSV Output** - Clean, structured output in CSV format for easy analysis  
✅ **Fallback System** - Saves raw AI responses when parsing fails  

## What It Does

1. **Reads** URLs from `urls.txt`
2. **Visits** each university website
3. **Extracts** the webpage content
4. **Analyzes and identifies** professors using Google Gemini AI
5. **Saves** results to an Excel file with separate sheets for each university

## Prerequisites

- Python 3.9 or higher (install latest version from https://python.org if you don't have)
- Google AI Studio API key ([Get one here](https://aistudio.google.com/app/apikey))
   - Requires an adult verified google account (18+)

## Installation

### Step 1: Clone or Download the Project

Either download the ZIP and extract it (recommended for beginners) by clicking on the green "Code" button above and selecting "Download ZIP".

Or run the below command in your terminal to clone the repo (requires Git):

```powershell
git clone https://github.com/sukarth/faculty-scraper.git
```

Then,

Navigate to the project directory:
```powershell
cd scraper
```

### Step 2: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure API Key

1. Open `config.json` in a text editor
2. Replace `"your-api-key-here"` with your actual Google AI Studio API key:

```json
{
    "gemini_api_key": "AIza..."
}
```

**How to get your API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into `config.json`

### Step 4: Prepare Input URLs

Create a file named `urls.txt` in the project directory and add the URLs of the faculty pages you want to scrape, one per line like below:

```
https://www.example.com/faculty/john-doe
https://www.example.com/faculty/jane-smith
```

### Step 5: Check setup
Run the test script to verify your setup and ensure everything is working:

```powershell
python test_setup.py
```
This will check:
- ✓ All required packages are installed
- ✓ Config file is valid
- ✓ API connection works
- ✓ Input file exists

### Step 6: Run the Scraper
```powershell
python faculty_scraper.py
```

## Usage

### Basic Usage

Simply run the script:

```powershell
python faculty_scraper.py
```

The scraper will:
1. Read URLs from `urls.txt`
2. Visit each URL and extract content
3. Analyze content using Google Gemini AI
4. Extract professor names, titles, and notes
5. Save results to a timestamped CSV file (e.g., `professors_20251106_143022.csv`)

### Input Format

Create a file named `urls.txt` with one URL per line:

```
https://econ.au.dk/research/economics/people
https://www.cbs.dk/en/research/departments-and-centres/department-of-economics/staff
https://www.economics.ku.dk/staff/vip/
```

## 📁 Output Files

The scraper generates several outputs:

1. **Excel File** (`professors_YYYYMMDD_HHMMSS.xlsx`)
   - Each university has its own sheet/tab
   - Sheet names are based on university domain (e.g., "CBS", "KU", "SDU")
   - Columns: Name, Title, Notes
   - Contains all successfully extracted professors

2. **Log File** (`logs/scraper_YYYYMMDD_HHMMSS.log`)
   - Detailed execution logs
   - Useful for debugging
   - Search for these keywords in the logs to narrow your search:
      - `INFO`: general info/successful operation 
      - `FAILED`: there was an error
      - `[EMPTY]`: 0 professors were found

3. **Raw Responses** (`output/raw_response_YYYYMMDD_HHMMSS.txt`)
   - Created when response parsing or saving to xlsx fails
   - Contains the raw AI response for manual review

All files are timestamped to prevent overwriting previous runs.

## Extraction Rules

The scraper follows these rules when identifying professors:

✅ **Include:**
- Professors of all types (Professor, Associate Professor, Assistant Professor, etc.)
- Department heads and chairs (noted in the Notes column)
- Professors on leave (with "on leave" in Notes)

❌ **Exclude:**
- Lecturers
- Postdocs
- Researchers
- Retired or former professors
- Visiting professors

## Error Handling

The scraper implements robust error handling:

### Network Errors
- **Automatic retry**: Up to 3 attempts per URL
- **Delay**: 2 seconds between retries
- **Logging**: All failures are logged

### Parsing Errors
- **Automatic retry**: Requests AI to regenerate response (up to 3 attempts)
- **Fallback**: Saves raw response to text file if parsing continues to fail
- **Continue processing**: Moves to next URL after max retries

## Configuration

You can modify these constants in `faculty_scraper.py`:

```python
MAX_RETRIES = 3      # Number of retry attempts
RETRY_DELAY = 2      # Seconds to wait between retries
```

## Project Structure

```
scraper/
├── faculty_scraper.py   # Main application
├── requirements.txt     # Python dependencies
├── readme.md            # This documentation file
├── test_setup.py        # Test script to verify setup
├── config.json          # API key configuration
├── urls.txt             # Input URLs
├── logs/                # Log files directory
└── output/              # Raw response files (when parsing fails)
```

## Troubleshooting

### "config.json not found"
- Make sure `config.json` exists in the same directory as `faculty_scraper.py`

### "Invalid API key"
- Verify your Google AI Studio API key is correct in `config.json`
- Ensure your API key starts with "AIza"

### "Failed to fetch content"
- Check your internet connection
- Some university websites may block automated requests
- The website structure might have changed

### No professors extracted
- Check the log file in `logs/` for detailed error messages
- Review raw response files in `output/` for manual inspection
- Some pages may not contain professor listings

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.9 or higher: `python --version`

## License

This tool is licensed under the MIT License. Check [LICENSE](LICENSE) for more information. 

Note: This tool is intended for educational and research purposes. Please respect university website terms of service and rate limits.

## Support

For issues or questions:
1. Check the log files in `logs/`
2. Review raw responses in `output/`
3. Verify your API key and internet connection

Create an issue on GitHub if you need further assistance.

---
**Made with ❤️ by [Sukarth](https://github.com/sukarth)**
