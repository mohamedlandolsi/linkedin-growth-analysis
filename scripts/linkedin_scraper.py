"""
LinkedIn Post Scraper

This module provides functionality to scrape LinkedIn posts using Selenium.
It extracts post content, engagement metrics (likes, comments, shares), and saves
the data to JSON format.

Note: LinkedIn requires authentication to view full posts. This script assumes
you'll handle authentication manually in the browser session.
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInPostScraper:
    """
    A scraper for extracting data from LinkedIn posts.
    
    This class handles browser initialization, page loading, data extraction,
    and saving results to JSON format.
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
        
    def _setup_driver(self) -> None:
        """
        Set up and configure the Chrome WebDriver with optimal settings.
        """
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        # Run in headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Additional options for stability and performance
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        
        # Set a realistic user agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Initialize the driver with webdriver-manager for automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set up explicit wait with 20 second timeout
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("Chrome WebDriver initialized successfully")
        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _extract_text_safely(self, by: By, selector: str, default: str = "") -> str:
        """
        Safely extract text from an element.
        
        Args:
            by: Selenium By locator type
            selector: Element selector string
            default: Default value if element not found
            
        Returns:
            Extracted text or default value
        """
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
        """
        Extract numeric value from metric text (e.g., "1.2K" -> 1200).
        
        Args:
            text: Text containing the metric (e.g., "1.2K likes", "500 comments")
            
        Returns:
            Numeric value or None if parsing fails
        """
        if not text:
            return None
        
        try:
            # Remove common words
            text = text.lower().replace('like', '').replace('comment', '').replace('share', '').strip()
            
            # Handle K (thousands) and M (millions)
            if 'k' in text:
                return int(float(text.replace('k', '').strip()) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '').strip()) * 1000000)
            else:
                # Try to extract any numeric value
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse metric value from '{text}': {e}")
        
        return None
    
    def _wait_for_page_load(self) -> None:
        """
        Wait for the LinkedIn post page to fully load.
        Implements multiple strategies to ensure content is ready.
        """
        logger.info("Waiting for page to load...")
        
        try:
            # Wait for the main feed container to be present
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Additional wait for dynamic content to render
            time.sleep(3)
            
            # Scroll to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            logger.info("Page loaded successfully")
        except TimeoutException:
            logger.warning("Timeout waiting for page load, proceeding anyway...")
    
    def extract_post_data(self, post_url: str) -> Dict[str, Any]:
        """
        Extract data from a LinkedIn post.
        
        Args:
            post_url: Full URL of the LinkedIn post
            
        Returns:
            Dictionary containing extracted post data
        """
        logger.info(f"Extracting data from: {post_url}")
        
        # Initialize the result dictionary
        post_data = {
            "url": post_url,
            "extracted_at": datetime.now().isoformat(),
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
            # Load the post URL
            logger.info("Loading LinkedIn post page...")
            self.driver.get(post_url)
            
            # Wait for page to fully load
            self._wait_for_page_load()
            
            # Check if login is required
            if "authwall" in self.driver.current_url or "login" in self.driver.current_url:
                error_msg = "LinkedIn requires authentication. Please log in manually."
                logger.error(error_msg)
                post_data["extraction_status"] = "failed"
                post_data["errors"].append(error_msg)
                
                # Wait for manual login (60 seconds)
                logger.info("Waiting 60 seconds for manual login...")
                time.sleep(60)
                
                # Try to navigate back to the post
                self.driver.get(post_url)
                self._wait_for_page_load()
            
            # Extract post text content
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
            
            # Extract author information
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
            
            # Try to find the social counts bar
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
                
                # Shares/Reposts
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
            
            # Log extraction summary
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
        """
        Save extracted data to a JSON file.
        
        Args:
            data: Dictionary containing the extracted data
            output_path: Path where JSON file should be saved
        """
        try:
            # Ensure the directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON with pretty formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved successfully to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")
            raise
    
    def scrape_post(self, post_url: str, output_path: str = "data/post_data.json") -> Dict[str, Any]:
        """
        Main method to scrape a LinkedIn post and save the results.
        
        Args:
            post_url: Full URL of the LinkedIn post
            output_path: Path where JSON file should be saved
            
        Returns:
            Dictionary containing the extracted post data
        """
        try:
            # Set up the WebDriver
            self._setup_driver()
            
            # Extract the post data
            post_data = self.extract_post_data(post_url)
            
            # Save to JSON
            self.save_to_json(post_data, output_path)
            
            return post_data
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            # Always close the browser
            self.close()
    
    def close(self) -> None:
        """
        Clean up and close the browser.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


def main():
    """
    Main function to demonstrate usage of the scraper.
    """
    # LinkedIn post URL to scrape
    post_url = "https://www.linkedin.com/posts/klarna_klarnas-climate-resilience-program-activity-7346877091532959746-748v/"
    
    # Output path for the JSON data
    output_path = "data/json/post_data.json"
    
    # Create scraper instance
    scraper = LinkedInPostScraper(headless=False)
    
    try:
        # Scrape the post
        logger.info("Starting LinkedIn post scraper...")
        post_data = scraper.scrape_post(post_url, output_path)
        
        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
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
