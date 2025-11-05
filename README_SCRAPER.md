# LinkedIn Post Scraper - Usage Guide

## Overview

The `linkedin_scraper.py` script extracts data from LinkedIn posts without using the official API. It uses Selenium to automate browser interactions and scrapes post content and engagement metrics.

## Features

- ✅ Extracts post text content
- ✅ Captures engagement metrics (likes, comments, shares)
- ✅ Extracts author information
- ✅ Handles authentication requirements
- ✅ Robust error handling and logging
- ✅ Saves data to JSON format
- ✅ Multiple selector strategies for reliability

## Requirements

All dependencies are already installed via `requirements.txt`:
- selenium
- webdriver-manager (automatic ChromeDriver management)

## Important Notes

⚠️ **LinkedIn Authentication Required**: LinkedIn requires you to be logged in to view posts. The script will:
1. Detect when login is required
2. Wait 60 seconds for you to manually log in
3. Continue scraping after authentication

⚠️ **Rate Limiting**: LinkedIn may rate-limit or block automated access. Use responsibly and add delays between requests.

⚠️ **Terms of Service**: Web scraping may violate LinkedIn's Terms of Service. This script is for educational purposes only.

## Usage

### Basic Usage

Run the script directly:

```powershell
D:/Ed/Projects/linkedin-growth-analysis/venv/Scripts/python.exe scripts/linkedin_scraper.py
```

### Custom Usage in Your Code

```python
from scripts.linkedin_scraper import LinkedInPostScraper

# Create scraper instance
scraper = LinkedInPostScraper(headless=False)

# Scrape a post
post_url = "https://www.linkedin.com/posts/..."
post_data = scraper.scrape_post(post_url, output_path="data/json/my_post.json")

# Access the extracted data
print(f"Likes: {post_data['likes']}")
print(f"Comments: {post_data['comments']}")
print(f"Post Text: {post_data['post_text']}")
```

### Headless Mode

For running without a visible browser window:

```python
scraper = LinkedInPostScraper(headless=True)
```

## Output Format

The script saves data in JSON format:

```json
{
  "url": "https://www.linkedin.com/posts/...",
  "extracted_at": "2025-11-05T10:30:00",
  "post_text": "Full post content here...",
  "likes": 1250,
  "comments": 45,
  "shares": 23,
  "author": "Company Name",
  "post_date": null,
  "extraction_status": "success",
  "errors": []
}
```

## Troubleshooting

### Issue: ChromeDriver not found
**Solution**: The script uses `webdriver-manager` which automatically downloads the correct ChromeDriver version. Ensure you have an internet connection.

### Issue: Login required
**Solution**: When the browser opens, manually log in to LinkedIn within 60 seconds. The script will wait for you.

### Issue: Elements not found
**Solution**: LinkedIn frequently changes their HTML structure. The script uses multiple selectors as fallbacks, but you may need to update selectors if LinkedIn makes major changes.

### Issue: Metrics showing as null
**Solution**: 
- Some posts may have metrics hidden or displayed differently
- Try running in non-headless mode to see what's happening
- Check if you're logged in properly
- Some metrics may genuinely be 0 or hidden by the post author

## Extending the Script

### Adding More Data Fields

To extract additional data, add extraction logic in the `extract_post_data` method:

```python
# Extract hashtags
hashtags = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='feed/hashtag']")
post_data["hashtags"] = [tag.text for tag in hashtags]
```

### Batch Processing Multiple Posts

```python
post_urls = [
    "https://www.linkedin.com/posts/...",
    "https://www.linkedin.com/posts/...",
]

scraper = LinkedInPostScraper(headless=False)
scraper._setup_driver()

for i, url in enumerate(post_urls):
    post_data = scraper.extract_post_data(url)
    scraper.save_to_json(post_data, f"data/json/post_{i}.json")
    time.sleep(5)  # Delay between requests

scraper.close()
```

## Best Practices

1. **Add delays**: Always add delays between requests to avoid rate limiting
2. **Respect robots.txt**: Check LinkedIn's robots.txt for allowed scraping
3. **Handle errors gracefully**: The script includes error handling, but always check logs
4. **Use headless sparingly**: Non-headless mode is more reliable for debugging
5. **Save regularly**: Don't scrape too much data at once; save incrementally

## Legal and Ethical Considerations

- This tool is for **educational and research purposes only**
- Web scraping may violate LinkedIn's Terms of Service
- Always respect website terms and conditions
- Consider using LinkedIn's official API for production use
- Be mindful of privacy and data protection regulations (GDPR, CCPA, etc.)

## Support

For issues or questions:
1. Check the logs in the console output
2. Review the `errors` field in the output JSON
3. Try running in non-headless mode to observe browser behavior
4. Update Chrome and ChromeDriver to the latest versions
