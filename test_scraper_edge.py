"""
Test script for LinkedIn scraper using Microsoft Edge
This version works with Edge browser (pre-installed on Windows)
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scripts.linkedin_scraper_edge import LinkedInPostScraper
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """Test the LinkedIn scraper with Edge browser."""
    
    post_url = "https://www.linkedin.com/posts/klarna_klarnas-climate-resilience-program-activity-7346877091532959746-748v/"
    output_path = "data/json/post_data.json"
    
    print("\n" + "="*70)
    print("LINKEDIN POST SCRAPER - MICROSOFT EDGE VERSION")
    print("="*70)
    print(f"\nTarget URL: {post_url}")
    print(f"Output Path: {output_path}")
    print("\n⚠️  IMPORTANT NOTES:")
    print("  - Microsoft Edge browser window will open")
    print("  - If prompted to login, you have 60 seconds to authenticate")
    print("  - The script will automatically extract data after page loads")
    print("  - Results will be saved to JSON automatically")
    print("\nStarting in 3 seconds...")
    print("="*70 + "\n")
    
    import time
    time.sleep(3)
    
    scraper = LinkedInPostScraper(headless=False)
    
    try:
        post_data = scraper.scrape_post(post_url, output_path)
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED")
        print("="*70)
        print(f"\nStatus: {post_data['extraction_status'].upper()}")
        print(f"Extracted at: {post_data['extracted_at']}")
        
        if post_data.get('author'):
            print(f"\n📝 Author: {post_data['author']}")
        
        if post_data.get('post_text'):
            preview = post_data['post_text'][:200]
            print(f"\n📄 Post Text Preview:")
            print(f"   {preview}{'...' if len(post_data['post_text']) > 200 else ''}")
            print(f"   (Total: {len(post_data['post_text'])} characters)")
        
        print(f"\n📊 Engagement Metrics:")
        print(f"   Likes:    {post_data.get('likes', 'Not extracted')}")
        print(f"   Comments: {post_data.get('comments', 'Not extracted')}")
        print(f"   Shares:   {post_data.get('shares', 'Not extracted')}")
        
        print(f"\n💾 Data saved to: {output_path}")
        
        if post_data.get('errors'):
            print(f"\n⚠️  Warnings/Errors encountered:")
            for error in post_data['errors']:
                print(f"   - {error}")
        
        print("\n" + "="*70 + "\n")
        
        return post_data
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_scraper()
