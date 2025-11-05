"""
Test script for LinkedIn scraper with automatic browser detection
This version automatically finds and uses any available browser on your system
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scripts.linkedin_scraper_auto import LinkedInPostScraper, BrowserDetector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """Test the LinkedIn scraper with automatic browser detection."""
    
    post_url = "https://www.linkedin.com/posts/klarna_klarnas-climate-resilience-program-activity-7346877091532959746-748v/"
    output_path = "data/json/post_data.json"
    
    print("\n" + "="*70)
    print("LINKEDIN POST SCRAPER - AUTO BROWSER DETECTION")
    print("="*70)
    
    # Detect browsers
    print("\n🔍 Scanning your system for browsers...")
    available_browsers = BrowserDetector.detect_browsers()
    
    if not available_browsers:
        print("\n❌ NO BROWSERS FOUND!")
        print("\nPlease install at least one of these browsers:")
        print("  • Google Chrome: https://www.google.com/chrome/")
        print("  • Microsoft Edge: (pre-installed on Windows 10/11)")
        print("  • Mozilla Firefox: https://www.mozilla.org/firefox/")
        print("  • Brave Browser: https://brave.com/")
        print("  • Opera: https://www.opera.com/")
        print("\n" + "="*70)
        return
    
    print(f"\n✅ Found {len(available_browsers)} browser(s):")
    for i, browser in enumerate(available_browsers, 1):
        icon = "🌐" if browser == "chrome" else "🔷" if browser == "edge" else "🦊" if browser == "firefox" else "🦁" if browser == "brave" else "⭕"
        print(f"   {i}. {icon} {browser.upper()}")
    
    print(f"\n🚀 Will use: {available_browsers[0].upper()}")
    
    print(f"\n📋 Target URL: {post_url}")
    print(f"💾 Output Path: {output_path}")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("  - Browser window will open automatically")
    print("  - If prompted to login, you have 60 seconds to authenticate")
    print("  - Data extraction happens automatically after page loads")
    print("  - Results will be saved to JSON")
    
    print("\n⏳ Starting in 3 seconds...")
    print("="*70 + "\n")
    
    import time
    time.sleep(3)
    
    # Create scraper (it will auto-detect and use first available browser)
    scraper = LinkedInPostScraper(headless=False)
    
    try:
        post_data = scraper.scrape_post(post_url, output_path)
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY")
        print("="*70)
        
        print(f"\n🌐 Browser Used: {post_data.get('browser_used', 'Unknown')}")
        print(f"📅 Extracted at: {post_data['extracted_at']}")
        print(f"✔️  Status: {post_data['extraction_status'].upper()}")
        
        if post_data.get('author'):
            print(f"\n👤 Author: {post_data['author']}")
        
        if post_data.get('post_text'):
            preview = post_data['post_text'][:200]
            print(f"\n📄 Post Text Preview:")
            print(f"   {preview}{'...' if len(post_data['post_text']) > 200 else ''}")
            print(f"   (Total: {len(post_data['post_text'])} characters)")
        
        print(f"\n📊 Engagement Metrics:")
        print(f"   👍 Likes:    {post_data.get('likes', 'Not extracted'):>8}")
        print(f"   💬 Comments: {post_data.get('comments', 'Not extracted'):>8}")
        print(f"   🔄 Shares:   {post_data.get('shares', 'Not extracted'):>8}")
        
        # Calculate total engagement
        if all([post_data.get('likes'), post_data.get('comments'), post_data.get('shares')]):
            total = post_data['likes'] + post_data['comments'] + post_data['shares']
            print(f"   ━━━━━━━━━━━━━━━━━━━")
            print(f"   📈 Total:    {total:>8}")
        
        print(f"\n💾 Data saved to: {output_path}")
        
        if post_data.get('errors'):
            print(f"\n⚠️  Warnings/Errors encountered:")
            for error in post_data['errors']:
                print(f"   • {error}")
        
        print("\n" + "="*70)
        print("🎉 All done! Check the JSON file for complete data.")
        print("="*70 + "\n")
        
        return post_data
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED!")
        print("="*70)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you have internet connection")
        print("  2. Try installing/updating one of the supported browsers")
        print("  3. Check if antivirus is blocking browser automation")
        print("="*70 + "\n")
        
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_scraper()
