"""
LinkedIn Post Scraper - Offline Version

This version uses Selenium's built-in automatic driver management (Selenium Manager)
which works better offline and doesn't require webdriver-manager.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInPostScraper:
    """
    A scraper for extracting data from LinkedIn posts.
    Uses Selenium Manager for automatic offline driver management.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the LinkedIn scraper.
        
        Args:
            headless: If True, run browser in headless mode (no GUI)
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.browser_used = None
        
    def _setup_driver(self) -> None:
        """
        Set up WebDriver using Selenium Manager (automatic driver management).
        Tries Brave first (uses existing login session), then other browsers.
        """
        browsers_to_try = [
            ('brave', self._setup_brave_simple),
            ('edge', self._setup_edge_simple),
            ('chrome', self._setup_chrome_simple),
            ('firefox', self._setup_firefox_simple),
        ]
        
        last_error = None
        for browser_name, setup_func in browsers_to_try:
            try:
                logger.info(f"Attempting to initialize {browser_name.upper()}...")
                self.driver, self.browser_used = setup_func()
                self.wait = WebDriverWait(self.driver, 20)
                logger.info(f"✅ Successfully initialized {self.browser_used}")
                return
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to initialize {browser_name}: {e}")
                continue
        
        raise WebDriverException(
            f"Failed to initialize any browser. Last error: {last_error}"
        )
    
    def _setup_brave_simple(self):
        """Setup Brave using Selenium Manager."""
        from selenium.webdriver.chrome.options import Options
        import os
        import platform
        
        options = Options()
        
        # Set Brave binary location
        if platform.system() == "Windows":
            brave_paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
            for path in brave_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    logger.info(f"Found Brave at: {path}")
                    break
        elif platform.system() == "Darwin":  # macOS
            options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        # Remove automation flags so it behaves like a regular browser
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Selenium Manager will automatically find and manage the driver
        driver = webdriver.Chrome(options=options)
        return driver, "Brave"
    
    def _setup_edge_simple(self):
        """Setup Edge using Selenium Manager (no webdriver-manager needed)."""
        from selenium.webdriver.edge.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Selenium Manager will automatically find and manage the driver
        driver = webdriver.Edge(options=options)
        return driver, "Edge"
    
    def _setup_chrome_simple(self):
        """Setup Chrome using Selenium Manager."""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = webdriver.Chrome(options=options)
        return driver, "Chrome"
    
    def _setup_firefox_simple(self):
        """Setup Firefox using Selenium Manager."""
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        driver = webdriver.Firefox(options=options)
        return driver, "Firefox"
    
    def _extract_text_safely(self, by: By, selector: str, default: str = "") -> str:
        """Safely extract text from an element."""
        try:
            element = self.driver.find_element(by, selector)
            return element.text.strip()
        except NoSuchElementException:
            logger.debug(f"Element not found: {selector}")
            return default
        except Exception as e:
            logger.warning(f"Error extracting text from {selector}: {e}")
            return default
    
    def _extract_metric_value(self, text: str) -> Optional[int]:
        """Extract numeric value from metric text."""
        if not text:
            return None
        
        try:
            text = text.lower().replace('like', '').replace('comment', '').replace('share', '').strip()
            
            if 'k' in text:
                return int(float(text.replace('k', '').strip()) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '').strip()) * 1000000)
            else:
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse metric value from '{text}': {e}")
        
        return None
    
    def _wait_for_page_load(self) -> bool:
        """Wait for the LinkedIn post page to fully load.
        
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        logger.info("Waiting for page to load...")
        
        try:
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            logger.info("Page loaded successfully")
            return True
        except TimeoutException:
            logger.warning("Timeout waiting for page load")
            return False
    
    def _load_page_with_retry(self, url: str, max_retries: int = 3, retry_delay: int = 2) -> bool:
        """Load a page with retry mechanism.
        
        Args:
            url: The URL to load
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay in seconds between retries (default: 2)
            
        Returns:
            bool: True if page loaded successfully, False if all retries failed
        """
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    logger.info(f"Retry attempt {attempt}/{max_retries} after {retry_delay}s delay...")
                    time.sleep(retry_delay)
                
                logger.info(f"Loading page (attempt {attempt}/{max_retries})...")
                self.driver.get(url)
                
                if self._wait_for_page_load():
                    logger.info(f"✅ Page loaded successfully on attempt {attempt}")
                    return True
                else:
                    logger.warning(f"⚠️ Page load failed on attempt {attempt}")
                    
            except Exception as e:
                logger.error(f"❌ Error on attempt {attempt}: {str(e)}")
                if attempt == max_retries:
                    logger.error(f"All {max_retries} attempts failed")
                    return False
        
        return False
    
    def extract_post_data(self, post_url: str) -> Dict[str, Any]:
        """Extract data from a LinkedIn post."""
        logger.info(f"Extracting data from: {post_url}")
        
        post_data = {
            "url": post_url,
            "extracted_at": datetime.now().isoformat(),
            "browser_used": self.browser_used,
            "post_text": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "author": None,
            "extraction_status": "success",
            "errors": []
        }
        
        try:
            # Load page with retry mechanism
            if not self._load_page_with_retry(post_url):
                error_msg = "Failed to load page after 3 attempts"
                logger.error(error_msg)
                post_data["extraction_status"] = "failed"
                post_data["errors"].append(error_msg)
                return post_data
            
            # Check if login is required
            if "authwall" in self.driver.current_url or "login" in self.driver.current_url:
                error_msg = "LinkedIn requires authentication. Please log in manually."
                logger.error(error_msg)
                post_data["extraction_status"] = "needs_login"
                post_data["errors"].append(error_msg)
                
                logger.info("Waiting 60 seconds for manual login...")
                time.sleep(60)
                
                # Retry loading after login
                if not self._load_page_with_retry(post_url):
                    error_msg = "Failed to load page after login"
                    logger.error(error_msg)
                    post_data["extraction_status"] = "failed"
                    post_data["errors"].append(error_msg)
                    return post_data
                    
            elif self.browser_used == "Brave":
                # For Brave, always give time to log in on first run
                logger.info("⏳ Brave browser opened. Please log in to LinkedIn if needed.")
                logger.info("⏳ Waiting 60 seconds for you to log in...")
                print("\n" + "="*70)
                print("🔐 PLEASE LOG IN TO LINKEDIN NOW")
                print("="*70)
                print("You have 60 seconds to log in to LinkedIn in the Brave browser.")
                print("If you're already logged in, just wait - extraction will continue.")
                print("="*70 + "\n")
                time.sleep(60)
                
                logger.info("Proceeding with extraction...")
                # Retry loading after login
                if not self._load_page_with_retry(post_url):
                    error_msg = "Failed to load page after login"
                    logger.error(error_msg)
                    post_data["extraction_status"] = "failed"
                    post_data["errors"].append(error_msg)
                    return post_data
            
            # Extract post text
            logger.info("Extracting post text...")
            post_text_selectors = [
                "div.feed-shared-update-v2__description",
                "div.feed-shared-text",
                "span.break-words",
                "div[data-test-id='main-feed-activity-card__commentary']"
            ]
            
            for selector in post_text_selectors:
                post_text = self._extract_text_safely(By.CSS_SELECTOR, selector)
                if post_text:
                    post_data["post_text"] = post_text
                    logger.info(f"Post text extracted: {len(post_text)} characters")
                    break
            
            if not post_data["post_text"]:
                post_data["errors"].append("Could not extract post text")
            
            # Extract author
            logger.info("Extracting author information...")
            author_selectors = [
                "span.update-components-actor__name",
                "span[aria-hidden='true'] > span[aria-hidden='true']",
                "div.update-components-actor__meta a"
            ]
            
            for selector in author_selectors:
                author = self._extract_text_safely(By.CSS_SELECTOR, selector)
                if author:
                    post_data["author"] = author
                    logger.info(f"Author extracted: {author}")
                    break
            
            # Extract engagement metrics
            logger.info("Extracting engagement metrics...")
            
            try:
                # Likes
                likes_selectors = [
                    "button[aria-label*='reaction']",
                    "button.social-counts-reactions",
                    "span.social-counts-reactions__count"
                ]
                
                for selector in likes_selectors:
                    likes_text = self._extract_text_safely(By.CSS_SELECTOR, selector)
                    if likes_text:
                        likes_value = self._extract_metric_value(likes_text)
                        if likes_value is not None:
                            post_data["likes"] = likes_value
                            logger.info(f"Likes extracted: {likes_value}")
                            break
                
                # Comments
                comments_selectors = [
                    "button[aria-label*='comment']",
                    "li.social-counts-comments"
                ]
                
                for selector in comments_selectors:
                    comments_text = self._extract_text_safely(By.CSS_SELECTOR, selector)
                    if comments_text:
                        comments_value = self._extract_metric_value(comments_text)
                        if comments_value is not None:
                            post_data["comments"] = comments_value
                            logger.info(f"Comments extracted: {comments_value}")
                            break
                
                # Shares
                shares_selectors = [
                    "button[aria-label*='repost']",
                    "button[aria-label*='share']"
                ]
                
                for selector in shares_selectors:
                    shares_text = self._extract_text_safely(By.CSS_SELECTOR, selector)
                    if shares_text:
                        shares_value = self._extract_metric_value(shares_text)
                        if shares_value is not None:
                            post_data["shares"] = shares_value
                            logger.info(f"Shares extracted: {shares_value}")
                            break
                
            except Exception as e:
                error_msg = f"Error extracting engagement metrics: {e}"
                logger.error(error_msg)
                post_data["errors"].append(error_msg)
            
            metrics_found = sum([
                post_data["post_text"] is not None,
                post_data["likes"] is not None,
                post_data["comments"] is not None,
                post_data["shares"] is not None
            ])
            logger.info(f"Extraction complete: {metrics_found}/4 key metrics extracted")
            
        except Exception as e:
            error_msg = f"Unexpected error during extraction: {e}"
            logger.error(error_msg)
            post_data["extraction_status"] = "failed"
            post_data["errors"].append(error_msg)
        
        return post_data
    
    def save_to_json(self, data: Dict[str, Any], output_path: str) -> None:
        """Save extracted data to JSON file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved successfully to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")
            raise
    
    def scrape_post(self, post_url: str, output_path: str = "data/post_data.json") -> Dict[str, Any]:
        """Main method to scrape a LinkedIn post."""
        try:
            self._setup_driver()
            post_data = self.extract_post_data(post_url)
            self.save_to_json(post_data, output_path)
            return post_data
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            self.close()
    
    def close(self) -> None:
        """Clean up and close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


def main():
    """Main function."""
    post_url = "https://www.linkedin.com/posts/klarna_klarnas-climate-resilience-program-activity-7346877091532959746-748v/"
    output_path = "data/json/post_data.json"
    
    print("\n" + "="*70)
    print("LINKEDIN POST SCRAPER - BRAVE BROWSER")
    print("="*70)
    print("🦁 Using Brave Browser - please log in when it opens")
    print("   (The script will wait 60 seconds for login if needed)")
    print("="*70 + "\n")
    
    scraper = LinkedInPostScraper(headless=False)
    
    try:
        logger.info("Starting LinkedIn post scraper...")
        post_data = scraper.scrape_post(post_url, output_path)
        
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Browser Used: {post_data.get('browser_used', 'Unknown')}")
        print(f"Status: {post_data['extraction_status']}")
        print(f"Author: {post_data.get('author', 'N/A')}")
        print(f"Post Text: {post_data['post_text'][:100] + '...' if post_data['post_text'] else 'N/A'}")
        print(f"Likes: {post_data.get('likes', 'N/A')}")
        print(f"Comments: {post_data.get('comments', 'N/A')}")
        print(f"Shares: {post_data.get('shares', 'N/A')}")
        print(f"\nData saved to: {output_path}")
        
        if post_data.get('errors'):
            print(f"\nWarnings:")
            for error in post_data['errors']:
                print(f"  - {error}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()
