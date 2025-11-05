"""
LinkedIn Post Analysis - Main Pipeline Orchestrator

This script orchestrates the complete analysis workflow:
1. Extract LinkedIn post data from URL
2. Analyze post text features
3. Perform sentiment analysis
4. Predict engagement scores
5. Score audience relevance (if audience data provided)
6. Generate CSV reports

Usage: python scripts/main.py [LinkedIn_Post_URL]

Example:
    python scripts/main.py https://www.linkedin.com/posts/klarna_activity-7348677091536605184-Br-h

Author: Mohamed Landolsi
Date: November 5, 2025
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import all analysis modules
try:
    from linkedin_scraper_simple import LinkedInPostScraper
    from post_analyzer import extract_post_features
    from sentiment_analyzer import analyze_sentiment
    from engagement_predictor import predict_engagement_score
    from icp_analyzer import define_icp, calculate_audience_relevance_score
    from export_to_csv import generate_analysis_outputs
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please ensure all required modules are in the scripts/ directory")
    sys.exit(1)


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print the pipeline header."""
    print("\n" + "="*70)
    print(f"{Colors.HEADER}{Colors.BOLD}📊 LINKEDIN POST ANALYSIS PIPELINE{Colors.ENDC}")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def print_step(step_number: int, step_name: str):
    """Print a step header."""
    print(f"\n{Colors.CYAN}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}[STEP {step_number}] {step_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print_error(f"Failed to save {file_path}: {e}")
        return False


def step1_extract_post(post_url: str, use_sample: bool = False) -> Optional[Dict[str, Any]]:
    """
    Step 1: Extract LinkedIn post data.
    
    Args:
        post_url: LinkedIn post URL
        use_sample: If True, load from sample file instead of scraping
        
    Returns:
        Dictionary with post data or None if failed
    """
    print_step(1, "EXTRACT LINKEDIN POST DATA")
    
    # Option to use existing sample data
    sample_file = 'data/json/post_data_sample.json'
    if use_sample and Path(sample_file).exists():
        print_info(f"Loading existing post data from {sample_file}")
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                post_data = json.load(f)
            print_success("Post data loaded from sample file")
            print_info(f"  • Author: {post_data.get('author', 'Unknown')}")
            print_info(f"  • Text length: {len(post_data.get('post_text', ''))} characters")
            print_info(f"  • Likes: {post_data.get('likes', 0)}")
            print_info(f"  • Comments: {post_data.get('comments', 0)}")
            print_info(f"  • Shares: {post_data.get('shares', 0)}")
            return post_data
        except Exception as e:
            print_error(f"Failed to load sample data: {e}")
            # Fall through to scraping
    
    try:
        print_info(f"Target URL: {post_url}")
        print_info("Initializing LinkedIn scraper...")
        
        scraper = LinkedInPostScraper()
        print_success("Scraper initialized")
        
        print_info("Extracting post data (this may take 60+ seconds for login)...")
        post_data = scraper.extract_post_data(post_url)
        
        if not post_data or post_data.get('extraction_status') == 'failed':
            print_error("Scraping failed - attempting to load sample data...")
            
            if Path(sample_file).exists():
                try:
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        post_data = json.load(f)
                    print_success("Loaded sample data as fallback")
                    return post_data
                except Exception as e:
                    print_error(f"Failed to load sample data: {e}")
            
            return None
        
        # Validate extraction
        if post_data.get('extraction_status') != 'success':
            print_warning(f"Extraction status: {post_data.get('extraction_status')}")
        
        print_success("Post data extracted successfully")
        print_info(f"  • Author: {post_data.get('author', 'Unknown')}")
        print_info(f"  • Text length: {len(post_data.get('post_text', ''))} characters")
        print_info(f"  • Likes: {post_data.get('likes', 0)}")
        print_info(f"  • Comments: {post_data.get('comments', 0)}")
        print_info(f"  • Shares: {post_data.get('shares', 0)}")
        
        # Save post data
        if save_json(post_data, 'data/json/post_data.json'):
            print_success("Saved to data/json/post_data.json")
        
        return post_data
        
    except Exception as e:
        print_error(f"Step 1 failed: {e}")
        
        # Try to load sample data as last resort
        if Path(sample_file).exists():
            print_info("Attempting to load sample data as fallback...")
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    post_data = json.load(f)
                print_success("Loaded sample data")
                return post_data
            except Exception as load_error:
                print_error(f"Failed to load sample data: {load_error}")
        
        return None


def step2_analyze_features(post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Step 2: Analyze post text features.
    
    Args:
        post_data: Post data from step 1
        
    Returns:
        Dictionary with text features or None if failed
    """
    print_step(2, "ANALYZE POST TEXT FEATURES")
    
    try:
        post_text = post_data.get('post_text', '')
        
        if not post_text:
            print_warning("No post text found")
            return {}
        
        print_info(f"Analyzing post text ({len(post_text)} characters)...")
        features = extract_post_features(post_text)
        
        print_success("Text features extracted")
        print_info(f"  • Word count: {features.get('word_count', 0)}")
        print_info(f"  • Hashtags: {features.get('hashtag_count', 0)}")
        print_info(f"  • Mentions: {features.get('mention_count', 0)}")
        print_info(f"  • Emojis: {features.get('emoji_count', 0)}")
        print_info(f"  • URLs: {features.get('url_count', 0)}")
        print_info(f"  • Has CTA: {'Yes' if features.get('has_call_to_action') else 'No'}")
        
        return features
        
    except Exception as e:
        print_error(f"Step 2 failed: {e}")
        return None


def step3_sentiment_analysis(post_text: str) -> Optional[Dict[str, Any]]:
    """
    Step 3: Perform sentiment analysis.
    
    Args:
        post_text: Post text content
        
    Returns:
        Dictionary with sentiment scores or None if failed
    """
    print_step(3, "SENTIMENT ANALYSIS")
    
    try:
        if not post_text:
            print_warning("No post text for sentiment analysis")
            return {}
        
        print_info("Running VADER sentiment analysis...")
        sentiment = analyze_sentiment(post_text)
        
        print_success("Sentiment analysis complete")
        print_info(f"  • Sentiment: {sentiment.get('sentiment_label', 'N/A')} ({sentiment.get('intensity', 'N/A')})")
        print_info(f"  • Compound score: {sentiment.get('compound_score', 0):.3f}")
        print_info(f"  • Positive: {sentiment.get('positive_score', 0):.1%}")
        print_info(f"  • Negative: {sentiment.get('negative_score', 0):.1%}")
        print_info(f"  • Confidence: {sentiment.get('confidence_level', 'N/A')}")
        
        return sentiment
        
    except Exception as e:
        print_error(f"Step 3 failed: {e}")
        return None


def step4_engagement_prediction(post_data: Dict[str, Any], features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Step 4: Predict engagement score.
    
    Args:
        post_data: Post data with current metrics
        features: Text features including sentiment
        
    Returns:
        Dictionary with engagement prediction or None if failed
    """
    print_step(4, "ENGAGEMENT PREDICTION")
    
    try:
        likes = post_data.get('likes', 0) or 0
        comments = post_data.get('comments', 0) or 0
        shares = post_data.get('shares', 0) or 0
        
        print_info(f"Predicting engagement score...")
        print_info(f"  • Current engagement: {likes + comments + shares} total")
        
        # Get sentiment from features
        sentiment = features.get('sentiment', {})
        
        prediction = predict_engagement_score(
            post_data=post_data,
            sentiment_data=sentiment,
            features_data=features
        )
        
        print_success("Engagement prediction complete")
        print_info(f"  • Predicted score: {prediction.get('engagement_score', 0):.1f}/100")
        print_info(f"  • Performance: {prediction.get('prediction_label', 'N/A')}")
        print_info(f"  • Percentile: {prediction.get('percentile', 'N/A')}")
        print_info(f"  • Confidence: {prediction.get('confidence_level', 'N/A')}")
        
        return prediction
        
    except Exception as e:
        print_error(f"Step 4 failed: {e}")
        return None


def step5_audience_analysis(sample_audience: Optional[List[Dict[str, Any]]] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Step 5: Score audience relevance (ICP matching).
    
    Args:
        sample_audience: List of audience member profiles (optional)
        
    Returns:
        List of scored audience members or None if failed
    """
    print_step(5, "AUDIENCE ICP SCORING")
    
    try:
        if not sample_audience:
            print_warning("No audience data provided - using sample profiles")
            
            # Create sample audience for demonstration
            sample_audience = [
                {
                    'name': 'Sarah Johnson',
                    'job_title': 'VP Marketing',
                    'seniority': 'VP',
                    'industry': 'B2B SaaS',
                    'company_size': 300,
                    'company_name': 'GrowthTech Inc',
                    'location': 'San Francisco, CA',
                    'linkedin_followers': 7500,
                    'profile_signals': ['content_creator', 'premium_user']
                },
                {
                    'name': 'Michael Chen',
                    'job_title': 'Marketing Manager',
                    'seniority': 'Manager',
                    'industry': 'Technology',
                    'company_size': 1200,
                    'company_name': 'TechCorp',
                    'location': 'Austin, TX',
                    'linkedin_followers': 1500,
                    'profile_signals': []
                }
            ]
        
        print_info(f"Scoring {len(sample_audience)} audience members...")
        
        # Define ICP
        icp = define_icp()
        print_info(f"  • ICP defined: {len(icp.target_roles)} roles, {len(icp.target_industries)} industries")
        
        # Score each audience member
        scored_audience = []
        hot_leads = 0
        warm_leads = 0
        
        for profile in sample_audience:
            score = calculate_audience_relevance_score(profile, icp)
            scored_audience.append({
                'profile': profile,
                'relevance': score
            })
            
            priority = score.get('lead_priority', 'Cold')
            if priority == 'Hot':
                hot_leads += 1
            elif priority == 'Warm':
                warm_leads += 1
        
        print_success("Audience scoring complete")
        print_info(f"  • Hot leads: {hot_leads}")
        print_info(f"  • Warm leads: {warm_leads}")
        print_info(f"  • Cold leads: {len(sample_audience) - hot_leads - warm_leads}")
        
        avg_score = sum(m['relevance']['relevance_score'] for m in scored_audience) / len(scored_audience)
        print_info(f"  • Average relevance: {avg_score:.1f}/100")
        
        return scored_audience
        
    except Exception as e:
        print_error(f"Step 5 failed: {e}")
        return None


def step6_generate_outputs(post_data: Dict[str, Any], analysis_data: Dict[str, Any], 
                          audience_data: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Step 6: Generate CSV outputs.
    
    Args:
        post_data: Post data from step 1
        analysis_data: Complete analysis results
        audience_data: Scored audience members
        
    Returns:
        True if successful, False otherwise
    """
    print_step(6, "GENERATE CSV OUTPUTS")
    
    try:
        # Save complete analysis to JSON first
        print_info("Saving complete analysis to JSON...")
        if save_json(analysis_data, 'data/json/post_analysis.json'):
            print_success("Saved to data/json/post_analysis.json")
        
        # Generate CSV outputs
        print_info("Generating CSV reports...")
        
        results = generate_analysis_outputs(
            post_data_path='data/json/post_data.json',
            analysis_data_path='data/json/post_analysis.json',
            output_dir='data/csv',
            audience_data=audience_data
        )
        
        print_success("CSV reports generated")
        print_info(f"  • Post analysis: {results.get('post_analysis_csv')}")
        
        if results.get('audience_ranking_csv'):
            print_info(f"  • Audience ranking: {results.get('audience_ranking_csv')}")
        
        return True
        
    except Exception as e:
        print_error(f"Step 6 failed: {e}")
        return False


def print_summary(start_time: float, success: bool, post_data: Optional[Dict[str, Any]] = None,
                 analysis_data: Optional[Dict[str, Any]] = None):
    """Print final summary."""
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}PIPELINE SUMMARY{Colors.ENDC}")
    print("="*70)
    
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ANALYSIS COMPLETE{Colors.ENDC}")
        print(f"\n⏱️  Execution time: {elapsed_time:.1f} seconds")
        
        if post_data:
            print(f"\n📊 Post Statistics:")
            print(f"  • Author: {post_data.get('author', 'Unknown')}")
            print(f"  • Total engagement: {(post_data.get('likes', 0) or 0) + (post_data.get('comments', 0) or 0) + (post_data.get('shares', 0) or 0)}")
        
        if analysis_data:
            sentiment = analysis_data.get('text_features', {}).get('sentiment', {})
            prediction = analysis_data.get('engagement_prediction', {})
            
            if sentiment:
                print(f"  • Sentiment: {sentiment.get('sentiment_label', 'N/A')} ({sentiment.get('compound_score', 0):.3f})")
            
            if prediction:
                print(f"  • Predicted score: {prediction.get('engagement_score', 0):.1f}/100")
                print(f"  • Performance: {prediction.get('prediction_label', 'N/A')}")
        
        print(f"\n📁 Output Files:")
        print(f"  • data/json/post_data.json")
        print(f"  • data/json/post_analysis.json")
        print(f"  • data/csv/post_analysis.csv")
        print(f"  • data/csv/audience_ranking.csv")
        
        print(f"\n💡 Next Steps:")
        print(f"  • View dashboard: streamlit run scripts/dashboard.py")
        print(f"  • Check CSV reports in data/csv/")
        
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ ANALYSIS FAILED{Colors.ENDC}")
        print(f"\n⏱️  Execution time: {elapsed_time:.1f} seconds")
        print(f"\n💡 Troubleshooting:")
        print(f"  • Check error messages above")
        print(f"  • Ensure you're logged into LinkedIn in Brave browser")
        print(f"  • Verify the post URL is correct and accessible")
        print(f"  • Run individual scripts to isolate the issue")
    
    print("="*70 + "\n")


def main(post_url: Optional[str] = None, audience_data: Optional[List[Dict[str, Any]]] = None, 
         use_sample: bool = True):
    """
    Main pipeline orchestrator.
    
    Args:
        post_url: LinkedIn post URL (uses sample if not provided)
        audience_data: List of audience profiles to score (uses sample if not provided)
        use_sample: If True, use existing sample data instead of scraping (default: True)
    """
    start_time = time.time()
    print_header()
    
    # Use sample URL if none provided
    if not post_url:
        post_url = "https://www.linkedin.com/posts/klarna_activity-7348677091536605184-Br-h"
        print_warning(f"No URL provided, using sample post: {post_url}")
    
    if use_sample:
        print_info("Using sample data mode (add --scrape flag to scrape fresh data)")
    
    success = True
    post_data = None
    analysis_data = {}
    
    try:
        # Step 1: Extract post data
        post_data = step1_extract_post(post_url, use_sample=use_sample)
        if not post_data:
            success = False
            print_error("Cannot proceed without post data")
            print_summary(start_time, success)
            return
        
        # Step 2: Analyze features
        features = step2_analyze_features(post_data)
        if features is None:
            success = False
            print_warning("Feature analysis failed, continuing with limited data...")
            features = {}
        
        # Step 3: Sentiment analysis
        post_text = post_data.get('post_text', '')
        sentiment = step3_sentiment_analysis(post_text)
        if sentiment is None:
            print_warning("Sentiment analysis failed, continuing...")
            sentiment = {}
        
        # Add sentiment to features
        if features is not None:
            features['sentiment'] = sentiment
        
        # Step 4: Engagement prediction
        prediction = step4_engagement_prediction(post_data, features or {})
        if prediction is None:
            print_warning("Engagement prediction failed, continuing...")
            prediction = {}
        
        # Build complete analysis data
        analysis_data = {
            'scraped_data': post_data,
            'text_features': features or {},
            'engagement_prediction': prediction or {},
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Step 5: Audience analysis
        scored_audience = step5_audience_analysis(audience_data)
        if scored_audience is None:
            print_warning("Audience analysis failed, continuing without audience data...")
            scored_audience = None
        
        # Step 6: Generate outputs
        output_success = step6_generate_outputs(post_data, analysis_data, scored_audience)
        if not output_success:
            print_warning("Output generation had issues, but core analysis completed")
        
    except KeyboardInterrupt:
        print_error("\n\nPipeline interrupted by user")
        success = False
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        success = False
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_summary(start_time, success, post_data, analysis_data)


if __name__ == "__main__":
    # Get post URL from command line argument if provided
    post_url = None
    use_sample = True
    
    # Parse command line arguments
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--scrape':
            use_sample = False
        elif arg.startswith('http'):
            post_url = arg
    
    # Run the pipeline
    main(post_url, use_sample=use_sample)
