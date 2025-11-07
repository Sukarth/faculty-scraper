# Contributing to Faculty Scraper

Thank you for your interest in contributing to the faculty Scraper project! We welcome contributions from the community.

## 🚀 How to Contribute

### 1. Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/faculty-scraper.git
   cd faculty-scraper
   ```

### 2. Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 4. Make Your Changes
- Follow the code style guidelines below
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass

### 5. Test Your Changes
```bash
# Run the test script
python test_setup.py

# Run additional tests if available
pytest
```

### 6. Commit and Push
```bash
git add .
git commit -m "Description of your changes"
git push origin your-branch-name
```

### 7. Create a Pull Request
1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch and provide a clear description
4. Reference any related issues

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Example:
```python
def extract_university_name(url: str) -> str:
    """
    Extract a clean university name from URL for sheet naming.

    Args:
        url: University website URL

    Returns:
        Clean university name suitable for Excel sheet name
    """
    # Implementation here
```

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

Examples:
```
Add retry mechanism for API calls
Fix parsing error when notes field is empty
Update README with new installation steps
```

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Sample URLs that cause issues

### Feature Requests
For new features, please:
- Describe the problem you're trying to solve
- Explain why the current solution isn't sufficient
- Provide examples of how you'd like it to work

## 🔧 Development Notes

### API Usage
- The project uses Google Gemini AI API
- Respect API rate limits
- Handle API errors gracefully
- Never commit API keys

### Web Scraping Ethics
- Respect website terms of service
- Use reasonable delays between requests
- Don't overload servers
- Consider robots.txt files

### Testing
- Test with multiple university websites
- Verify output formats (CSV/Excel)
- Check error handling for network issues
- Validate AI response parsing

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions
- Update requirements.txt for new dependencies
- Document any configuration changes

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow the project's goals and scope

## 📞 Getting Help

If you need help:
1. Check the README.md for setup instructions
2. Review existing issues on GitHub
3. Ask questions in new issues
4. Join discussions in pull request comments

Thank you for contributing to Faculty Scraper! 🎉