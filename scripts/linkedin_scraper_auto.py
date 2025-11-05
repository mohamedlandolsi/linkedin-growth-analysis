"""
LinkedIn Post Scraper - Auto Browser Detection

This module automatically detects and uses any available browser on your system.
Supports: Chrome, Edge, Firefox, Opera, and Brave.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
import os
import platform

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


class BrowserDetector:
    """Detects available browsers on the system."""
    
    @staticmethod
    def _check_chrome() -> bool:
        """Check if Chrome is installed."""
        if platform.system() == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
            return any(os.path.exists(path) for path in chrome_paths)
        elif platform.system() == "Darwin":  # macOS
            return os.path.exists("/Applications/Google Chrome.app")
        else:  # Linux
            import shutil
            return shutil.which("google-chrome") is not None
    
    @staticmethod
    def _check_edge() -> bool:
        """Check if Edge is installed."""
        if platform.system() == "Windows":
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            return any(os.path.exists(path) for path in edge_paths)
        elif platform.system() == "Darwin":  # macOS
            return os.path.exists("/Applications/Microsoft Edge.app")
        else:  # Linux
            import shutil
            return shutil.which("microsoft-edge") is not None
    
    @staticmethod
    def _check_firefox() -> bool:
        """Check if Firefox is installed."""
        if platform.system() == "Windows":
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            return any(os.path.exists(path) for path in firefox_paths)
        elif platform.system() == "Darwin":  # macOS
            return os.path.exists("/Applications/Firefox.app")
        else:  # Linux
            import shutil
            return shutil.which("firefox") is not None
    
    @staticmethod
    def _check_brave() -> bool:
        """Check if Brave is installed."""
        if platform.system() == "Windows":
            brave_paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
            return any(os.path.exists(path) for path in brave_paths)
        elif platform.system() == "Darwin":  # macOS
            return os.path.exists("/Applications/Brave Browser.app")
        else:  # Linux
            import shutil
            return shutil.which("brave-browser") is not None or shutil.which("brave") is not None
    
    @staticmethod
    def _check_opera() -> bool:
        """Check if Opera is installed."""
        if platform.system() == "Windows":
            opera_paths = [
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Opera\launcher.exe")
            ]
            return any(os.path.exists(path) for path in opera_paths)
        elif platform.system() == "Darwin":  # macOS
            return os.path.exists("/Applications/Opera.app")
        else:  # Linux
            import shutil
            return shutil.which("opera") is not None
    
    @classmethod
    def detect_browsers(cls) -> list:
        """
        Detect all available browsers on the system.
        
        Returns:
            List of tuples (browser_name, is_available)
        """
        browsers = [
            ("chrome", cls._check_chrome()),
            ("edge", cls._check_edge()),
            ("firefox", cls._check_firefox()),
            ("brave", cls._check_brave()),
            ("opera", cls._check_opera())
        ]
        
        available = [name for name, available in browsers if available]
        
        logger.info(f"Detected browsers: {', '.join(available) if available else 'None'}")
        return available
    
    @classmethod
    def get_first_available(cls) -> Optional[str]:
        """Get the first available browser."""
        available = cls.detect_browsers()
        return available[0] if available else None


class LinkedInPostScraper:
    """
    A scraper for extracting data from LinkedIn posts.
    Automatically detects and uses available browsers.
    """
    
    def __init__(self, headless: bool = False, preferred_browser: Optional[str] = None):
        """
        Initialize the LinkedIn scraper.
        
        Args:
            headless: If True, run browser in headless mode (no GUI)
            preferred_browser: Preferred browser ('chrome', 'edge', 'firefox', 'brave', 'opera')
                              If None, auto-detects the first available browser
        """
        self.headless = headless
        self.preferred_browser = preferred_browser
        self.driver = None
        self.wait = None
        self.browser_used = None
        
    def _setup_chrome(self) -> Tuple[webdriver.Chrome, str]:
        """Setup Chrome browser."""
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType
            
            logger.info("Setting up Chrome WebDriver...")
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use latest driver version automatically
            service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver = webdriver.Chrome(service=service, options=options)
            
            return driver, "Chrome"
        except Exception as e:
            logger.warning(f"Failed to setup Chrome: {e}")
            raise
    
    def _setup_edge(self) -> Tuple[webdriver.Edge, str]:
        """Setup Edge browser."""
        try:
            from selenium.webdriver.edge.service import Service
            from selenium.webdriver.edge.options import Options
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            
            logger.info("Setting up Edge WebDriver...")
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            )
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Simple driver installation without extra parameters
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            
            return driver, "Edge"
        except Exception as e:
            logger.warning(f"Failed to setup Edge: {e}")
            raise
    
    def _setup_firefox(self) -> Tuple[webdriver.Firefox, str]:
        """Setup Firefox browser."""
        try:
            from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.firefox.options import Options
            from webdriver_manager.firefox import GeckoDriverManager
            
            logger.info("Setting up Firefox WebDriver...")
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            
            return driver, "Firefox"
        except Exception as e:
            logger.warning(f"Failed to setup Firefox: {e}")
            raise
    
    def _setup_brave(self) -> Tuple[webdriver.Chrome, str]:
        """Setup Brave browser (uses Chrome driver)."""
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            logger.info("Setting up Brave WebDriver...")
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
                        break
            elif platform.system() == "Darwin":  # macOS
                options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use regular ChromeDriver (Brave is Chromium-based)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            return driver, "Brave"
        except Exception as e:
            logger.warning(f"Failed to setup Brave: {e}")
            raise
    
    def _setup_opera(self) -> Tuple[webdriver.Chrome, str]:
        """Setup Opera browser (uses Chrome driver)."""
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.opera import OperaDriverManager
            
            logger.info("Setting up Opera WebDriver...")
            options = Options()
            
            # Set Opera binary location
            if platform.system() == "Windows":
                opera_paths = [
                    r"C:\Program Files\Opera\launcher.exe",
                    r"C:\Program Files (x86)\Opera\launcher.exe",
                    os.path.expanduser(r"~\AppData\Local\Programs\Opera\launcher.exe")
                ]
                for path in opera_paths:
                    if os.path.exists(path):
                        options.binary_location = path
                        break
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service(OperaDriverManager().install())
            except:
                service = Service(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(service=service, options=options)
            
            return driver, "Opera"
        except Exception as e:
            logger.warning(f"Failed to setup Opera: {e}")
            raise
    
    def _setup_driver(self) -> None:
        """
        Set up WebDriver with automatic browser detection.
        """
        # Determine which browser to use
        if self.preferred_browser:
            browsers_to_try = [self.preferred_browser]
            logger.info(f"Attempting to use preferred browser: {self.preferred_browser}")
        else:
            available_browsers = BrowserDetector.detect_browsers()
            if not available_browsers:
                raise WebDriverException(
                    "No supported browsers found! Please install one of: "
                    "Chrome, Edge, Firefox, Brave, or Opera"
                )
            browsers_to_try = available_browsers
            logger.info(f"Available browsers: {', '.join(browsers_to_try)}")
        
        # Try each browser until one works
        last_error = None
        for browser in browsers_to_try:
            try:
                logger.info(f"Attempting to initialize {browser.upper()} browser...")
                
                if browser == "chrome":
                    self.driver, self.browser_used = self._setup_chrome()
                elif browser == "edge":
                    self.driver, self.browser_used = self._setup_edge()
                elif browser == "firefox":
                    self.driver, self.browser_used = self._setup_firefox()
                elif browser == "brave":
                    self.driver, self.browser_used = self._setup_brave()
                elif browser == "opera":
                    self.driver, self.browser_used = self._setup_opera()
                else:
                    continue
                
                # Set up explicit wait
                self.wait = WebDriverWait(self.driver, 20)
                
                logger.info(f"✅ Successfully initialized {self.browser_used} WebDriver")
                return
                
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to initialize {browser}: {e}")
                continue
        
        # If we get here, no browser worked
        raise WebDriverException(
            f"Failed to initialize any browser. Last error: {last_error}\n"
            f"Tried browsers: {', '.join(browsers_to_try)}"
        )
    
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
    
    def _wait_for_page_load(self) -> None:
        """Wait for the LinkedIn post page to fully load."""
        logger.info("Waiting for page to load...")
        
        try:
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            logger.info("Page loaded successfully")
        except TimeoutException:
            logger.warning("Timeout waiting for page load, proceeding anyway...")
    
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
            "post_date": None,
            "extraction_status": "success",
            "errors": []
        }
        
        try:
            logger.info("Loading LinkedIn post page...")
            self.driver.get(post_url)
            self._wait_for_page_load()
            
            # Check if login is required
            if "authwall" in self.driver.current_url or "login" in self.driver.current_url:
                error_msg = "LinkedIn requires authentication. Please log in manually."
                logger.error(error_msg)
                post_data["extraction_status"] = "failed"
                post_data["errors"].append(error_msg)
                
                logger.info("Waiting 60 seconds for manual login...")
                time.sleep(60)
                
                self.driver.get(post_url)
                self._wait_for_page_load()
            
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
                    "span.social-counts-reactions__count",
                    "button[data-test-id='social-actions__reaction']"
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
                    "li.social-counts-comments",
                    "button[data-test-id='social-actions__comment']"
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
                    "button[aria-label*='share']",
                    "li.social-counts-reposts",
                    "button[data-test-id='social-actions__repost']"
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
    
    # Detect available browsers first
    print("\n" + "="*70)
    print("🔍 DETECTING AVAILABLE BROWSERS...")
    print("="*70)
    available = BrowserDetector.detect_browsers()
    if available:
        print(f"\n✅ Found {len(available)} browser(s): {', '.join([b.upper() for b in available])}")
        print(f"   Will use: {available[0].upper()}")
    else:
        print("\n❌ No browsers found!")
        print("   Please install one of: Chrome, Edge, Firefox, Brave, or Opera")
        return
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
        print(f"URL: {post_data['url']}")
        print(f"Author: {post_data.get('author', 'N/A')}")
        print(f"Post Text: {post_data['post_text'][:100] + '...' if post_data['post_text'] else 'N/A'}")
        print(f"Likes: {post_data.get('likes', 'N/A')}")
        print(f"Comments: {post_data.get('comments', 'N/A')}")
        print(f"Shares: {post_data.get('shares', 'N/A')}")
        print(f"\nData saved to: {output_path}")
        
        if post_data.get('errors'):
            print(f"\nWarnings/Errors:")
            for error in post_data['errors']:
                print(f"  - {error}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()
