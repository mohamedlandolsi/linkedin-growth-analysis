"""
Integration Example: Scrape and Analyze LinkedIn Posts

This script demonstrates how to combine the LinkedIn scraper with the post analyzer
to extract post data and perform comprehensive text analysis.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from post_analyzer import extract_post_features, analyze_engagement_signals


def load_scraped_post(json_path: str = "data/json/post_data.json") -> Dict[str, Any]:
    """
    Load scraped post data from JSON file.
    
    Args:
        json_path (str): Path to the JSON file containing scraped data
        
    Returns:
        Dict[str, Any]: Scraped post data
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_scraped_post(json_path: str = "data/json/post_data.json") -> Dict[str, Any]:
    """
    Load and analyze a scraped LinkedIn post.
    
    Args:
        json_path (str): Path to the JSON file containing scraped data
        
    Returns:
        Dict[str, Any]: Combined scraped data and analysis results
    """
    # Load scraped data
    post_data = load_scraped_post(json_path)
    
    # Extract post text
    post_text = post_data.get('post_text', '')
    
    if not post_text:
        print("⚠️ Warning: No post text found in scraped data")
        return {
            'scraped_data': post_data,
            'text_features': {},
            'engagement_analysis': {}
        }
    
    # Analyze post features
    features = extract_post_features(post_text)
    
    # Analyze engagement signals
    engagement = analyze_engagement_signals(features)
    
    # Combine all data
    result = {
        'scraped_data': post_data,
        'text_features': features,
        'engagement_analysis': engagement
    }
    
    return result


def print_analysis_report(analysis: Dict[str, Any]) -> None:
    """
    Print a formatted analysis report.
    
    Args:
        analysis (Dict[str, Any]): Analysis results from analyze_scraped_post()
    """
    scraped = analysis['scraped_data']
    features = analysis['text_features']
    engagement = analysis['engagement_analysis']
    
    print("\n" + "="*80)
    print("LINKEDIN POST ANALYSIS REPORT")
    print("="*80)
    
    # Post metadata
    print("\n📄 POST METADATA:")
    print("-"*80)
    print(f"URL: {scraped.get('url', 'N/A')}")
    print(f"Author: {scraped.get('author', 'N/A')}")
    print(f"Browser Used: {scraped.get('browser_used', 'N/A')}")
    print(f"Extracted At: {scraped.get('extracted_at', 'N/A')}")
    
    # Engagement metrics
    print("\n📊 ENGAGEMENT METRICS:")
    print("-"*80)
    print(f"Likes: {scraped.get('likes', 0):,}")
    print(f"Comments: {scraped.get('comments', 0):,}")
    print(f"Shares: {scraped.get('shares', 0):,}")
    
    total_engagement = (scraped.get('likes', 0) or 0) + \
                      (scraped.get('comments', 0) or 0) + \
                      (scraped.get('shares', 0) or 0)
    print(f"Total Engagement: {total_engagement:,}")
    
    # Text features
    print("\n📝 TEXT ANALYSIS:")
    print("-"*80)
    print(f"Word Count: {features['word_count']}")
    print(f"Character Count: {features['character_count']}")
    print(f"Average Word Length: {features['average_word_length']}")
    print(f"Unique Words: {features['unique_words']}")
    print(f"Sentences: {features['sentence_count']}")
    print(f"Lines: {features['line_count']}")
    
    # Content elements
    print("\n🏷️ CONTENT ELEMENTS:")
    print("-"*80)
    print(f"Hashtags ({features['hashtag_count']}): {', '.join(features['hashtags']) if features['hashtags'] else 'None'}")
    print(f"Mentions ({features['mention_count']}): {', '.join(features['mentions']) if features['mentions'] else 'None'}")
    print(f"URLs ({features['url_count']}): {features['url_count']} found")
    print(f"Emojis ({features['emoji_count']}): {' '.join(features['emojis']) if features['emojis'] else 'None'}")
    print(f"Call-to-Action: {'✅ Yes' if features['has_call_to_action'] else '❌ No'}")
    if features['call_to_action_phrases']:
        print(f"  CTA Phrases: {', '.join(features['call_to_action_phrases'])}")
    
    # Engagement analysis
    print("\n🎯 ENGAGEMENT ANALYSIS:")
    print("-"*80)
    print(f"Engagement Score: {engagement['engagement_score']}/100")
    print(f"Readability: {engagement['readability_score']}")
    print(f"Strong Hook: {'✅ Yes' if engagement['has_strong_hook'] else '❌ No'}")
    
    if engagement['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(engagement['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Post preview
    print("\n📖 POST PREVIEW:")
    print("-"*80)
    preview = scraped.get('post_text', 'N/A')
    if len(preview) > 200:
        preview = preview[:200] + "..."
    print(preview)
    
    print("\n" + "="*80)


def save_analysis(analysis: Dict[str, Any], output_path: str = "data/json/post_analysis.json") -> None:
    """
    Save analysis results to JSON file.
    
    Args:
        analysis (Dict[str, Any]): Analysis results
        output_path (str): Path to save the JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Analysis saved to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze a scraped LinkedIn post")
    parser.add_argument(
        "--input",
        default="data/json/post_data.json",
        help="Path to scraped post JSON file"
    )
    parser.add_argument(
        "--output",
        default="data/json/post_analysis.json",
        help="Path to save analysis results"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )
    
    args = parser.parse_args()
    
    try:
        print("🔍 Analyzing scraped LinkedIn post...")
        
        # Perform analysis
        analysis = analyze_scraped_post(args.input)
        
        # Print report
        print_analysis_report(analysis)
        
        # Save results
        if not args.no_save:
            save_analysis(analysis, args.output)
        
        print("\n✅ Analysis complete!")
        
    except FileNotFoundError:
        print(f"\n❌ Error: File not found - {args.input}")
        print("Please run the scraper first to generate post data.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
