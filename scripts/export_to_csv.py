"""
Analysis Output Generator

This module generates CSV exports of LinkedIn post analysis results,
including post performance metrics and audience ICP scoring.

Outputs:
- data/csv/post_analysis.csv: Post-level metrics and predictions
- data/csv/audience_ranking.csv: Audience member ICP scores and recommendations
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def generate_analysis_outputs(
    post_data_path: str = "data/json/post_data.json",
    analysis_data_path: str = "data/json/post_analysis.json",
    output_dir: str = "data/csv",
    audience_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, str]:
    """
    Generate CSV exports of all LinkedIn post analysis results.
    
    This function consolidates post data, text features, sentiment analysis,
    and engagement predictions into clean, sorted CSV files suitable for
    Excel, reporting tools, or further analysis.
    
    Args:
        post_data_path (str): Path to scraped post data JSON
        analysis_data_path (str): Path to complete analysis results JSON
        output_dir (str): Directory to save CSV files
        audience_data (List[Dict], optional): List of scored audience members
            from ICP analyzer. Each dict should contain profile data and
            relevance scores.
            
    Returns:
        Dict[str, str]: Dictionary with paths to generated files:
            - 'post_analysis_csv': Path to post analysis CSV
            - 'audience_ranking_csv': Path to audience ranking CSV (if data provided)
            - 'summary': Summary statistics string
            
    Example:
        >>> results = generate_analysis_outputs()
        >>> print(f"Post analysis saved to: {results['post_analysis_csv']}")
        >>> print(results['summary'])
    """
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load data files
    post_data = _load_json_file(post_data_path)
    analysis_data = _load_json_file(analysis_data_path)
    
    # Generate post analysis CSV
    post_csv_path = _generate_post_analysis_csv(
        post_data, analysis_data, output_dir
    )
    
    # Generate audience ranking CSV if data provided
    audience_csv_path = None
    if audience_data:
        audience_csv_path = _generate_audience_ranking_csv(
            audience_data, output_dir
        )
    
    # Generate summary statistics
    summary = _generate_summary_statistics(post_data, analysis_data, audience_data)
    
    return {
        'post_analysis_csv': post_csv_path,
        'audience_ranking_csv': audience_csv_path,
        'summary': summary
    }


def _load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found - {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {file_path}")
        return {}


def _generate_post_analysis_csv(
    post_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    output_dir: str
) -> str:
    """
    Generate post_analysis.csv with comprehensive post metrics.
    
    CSV Structure:
    - Summary row at top with aggregate statistics
    - Data rows with individual post metrics
    - Sorted by predicted engagement score (descending)
    """
    
    # Extract data from nested structure
    scraped = analysis_data.get('scraped_data', post_data)
    features = analysis_data.get('text_features', {})
    sentiment = features.get('sentiment', {})
    prediction = analysis_data.get('engagement_prediction', {})
    
    # Create post record
    post_records = []
    
    # Generate unique post ID from URL or timestamp
    post_url = scraped.get('url', '')
    post_id = _extract_post_id(post_url) or scraped.get('extracted_at', 'unknown')[:10]
    
    # Get post text (truncate to 100 chars for CSV)
    post_text = scraped.get('post_text', '')
    post_text_short = (post_text[:100] + '...') if len(post_text) > 100 else post_text
    post_text_short = post_text_short.replace('\n', ' ').replace('\r', ' ')  # Remove line breaks
    
    # Compile post record
    record = {
        'post_id': post_id,
        'post_text': post_text_short,
        'extracted_at': scraped.get('extracted_at', ''),
        'author': scraped.get('author', 'Unknown'),
        'browser_used': scraped.get('browser_used', ''),
        
        # Text features
        'word_count': features.get('word_count', 0),
        'character_count': features.get('character_count', 0),
        'hashtag_count': features.get('hashtag_count', 0),
        'emoji_count': features.get('emoji_count', 0),
        'url_count': features.get('url_count', 0),
        'has_cta': 'Yes' if features.get('has_call_to_action') else 'No',
        
        # Sentiment analysis
        'sentiment_label': sentiment.get('sentiment_label', 'N/A').title(),
        'sentiment_score': sentiment.get('compound_score', 0.0),
        'sentiment_intensity': sentiment.get('intensity', 'N/A'),
        'sentiment_positive_pct': f"{sentiment.get('positive_score', 0) * 100:.1f}%",
        'sentiment_negative_pct': f"{sentiment.get('negative_score', 0) * 100:.1f}%",
        
        # Current engagement metrics
        'current_likes': scraped.get('likes') or 0,
        'current_comments': scraped.get('comments') or 0,
        'current_shares': scraped.get('shares') or 0,
        'total_engagement': (scraped.get('likes') or 0) + 
                           (scraped.get('comments') or 0) + 
                           (scraped.get('shares') or 0),
        
        # Engagement prediction
        'predicted_engagement_score': prediction.get('engagement_score', 0),
        'performance_label': prediction.get('prediction_label', 'N/A'),
        'prediction_confidence': prediction.get('confidence_level', 'N/A').title(),
        'percentile_rank': prediction.get('percentile', 'N/A'),
        
        # Score breakdown
        'base_score': prediction.get('base_score', 0),
        'quality_bonus': prediction.get('quality_bonus', 0),
        
        # Status
        'extraction_status': scraped.get('extraction_status', 'unknown')
    }
    
    post_records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(post_records)
    
    # Sort by predicted engagement score (descending)
    if 'predicted_engagement_score' in df.columns:
        df = df.sort_values('predicted_engagement_score', ascending=False)
    
    # Calculate summary statistics
    summary_row = {
        'post_id': '=== SUMMARY STATISTICS ===',
        'post_text': f"Total Posts: {len(df)}",
        'extracted_at': f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        'author': '',
        'browser_used': '',
        
        'word_count': f"Avg: {df['word_count'].mean():.0f}" if not df.empty else '',
        'character_count': f"Avg: {df['character_count'].mean():.0f}" if not df.empty else '',
        'hashtag_count': f"Avg: {df['hashtag_count'].mean():.1f}" if not df.empty else '',
        'emoji_count': f"Avg: {df['emoji_count'].mean():.1f}" if not df.empty else '',
        'url_count': f"Total: {df['url_count'].sum():.0f}" if not df.empty else '',
        'has_cta': f"{(df['has_cta'] == 'Yes').sum()} posts" if not df.empty else '',
        
        'sentiment_label': f"Positive: {(df['sentiment_label'] == 'Positive').sum()}" if not df.empty else '',
        'sentiment_score': f"Avg: {df['sentiment_score'].mean():.2f}" if not df.empty else '',
        'sentiment_intensity': '',
        'sentiment_positive_pct': '',
        'sentiment_negative_pct': '',
        
        'current_likes': f"Total: {df['current_likes'].sum():.0f}" if not df.empty else '',
        'current_comments': f"Total: {df['current_comments'].sum():.0f}" if not df.empty else '',
        'current_shares': f"Total: {df['current_shares'].sum():.0f}" if not df.empty else '',
        'total_engagement': f"Total: {df['total_engagement'].sum():.0f}" if not df.empty else '',
        
        'predicted_engagement_score': f"Avg: {df['predicted_engagement_score'].mean():.1f}" if not df.empty else '',
        'performance_label': f"High: {(df['performance_label'] == 'High Performer').sum()}" if not df.empty else '',
        'prediction_confidence': '',
        'percentile_rank': '',
        'base_score': '',
        'quality_bonus': '',
        'extraction_status': ''
    }
    
    # Add summary row at top
    summary_df = pd.DataFrame([summary_row])
    df_with_summary = pd.concat([summary_df, df], ignore_index=True)
    
    # Save to CSV
    output_path = Path(output_dir) / 'post_analysis.csv'
    df_with_summary.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Post analysis CSV saved: {output_path}")
    print(f"   • {len(df)} post(s) analyzed")
    print(f"   • Average engagement score: {df['predicted_engagement_score'].mean():.1f}/100" if not df.empty else "")
    
    return str(output_path)


def _generate_audience_ranking_csv(
    audience_data: List[Dict[str, Any]],
    output_dir: str
) -> str:
    """
    Generate audience_ranking.csv with ICP scoring results.
    
    CSV Structure:
    - Summary row at top with aggregate statistics
    - Data rows with individual audience member scores
    - Sorted by relevance score (descending)
    """
    
    # Extract audience records
    audience_records = []
    
    for idx, member in enumerate(audience_data, 1):
        # Get profile data
        profile = member.get('profile', {})
        relevance = member.get('relevance', {})
        match_details = relevance.get('match_details', {})
        
        # Generate unique ID
        audience_id = f"AUD-{idx:04d}"
        
        # Get profile name (construct from available data)
        profile_name = profile.get('name', 'Unknown')
        if profile_name == 'Unknown':
            # Try to construct from job title and company
            job = profile.get('job_title', '')
            company = profile.get('company_name', '')
            if job and company:
                profile_name = f"{job} @ {company}"
        
        # Get ICP match reason (why they scored high/low)
        match_reason = _format_match_reason(match_details, relevance.get('score_breakdown', {}))
        
        # Get top recommendation
        recommendations = relevance.get('recommendations', [])
        top_recommendation = recommendations[0] if recommendations else 'No specific recommendations'
        # Clean emoji and formatting from recommendation
        top_recommendation = top_recommendation.replace('🔥', '').replace('✅', '').replace('💡', '').replace('⚠️', '').strip()
        
        # Compile record
        record = {
            'audience_id': audience_id,
            'profile_name': profile_name,
            'job_title': profile.get('job_title', 'Unknown'),
            'seniority': profile.get('seniority', 'Unknown'),
            'company': profile.get('company_name', 'Unknown'),
            'company_size': profile.get('company_size', 0),
            'industry': profile.get('industry', 'Unknown'),
            'location': profile.get('location', 'Unknown'),
            'linkedin_followers': profile.get('linkedin_followers', 0),
            
            # ICP Scoring
            'relevance_score': relevance.get('relevance_score', 0),
            'relevance_label': relevance.get('relevance_label', 'Unknown'),
            'lead_priority': relevance.get('lead_priority', 'Cold'),
            'confidence': relevance.get('confidence_level', 'low').title(),
            
            # Score breakdown
            'role_score': relevance.get('score_breakdown', {}).get('role_score', 0),
            'seniority_score': relevance.get('score_breakdown', {}).get('seniority_score', 0),
            'industry_score': relevance.get('score_breakdown', {}).get('industry_score', 0),
            'company_size_score': relevance.get('score_breakdown', {}).get('company_size_score', 0),
            'bonus_score': relevance.get('score_breakdown', {}).get('bonus_score', 0),
            
            # Match details
            'icp_match_reason': match_reason,
            'role_match_type': match_details.get('role_match_type', 'none'),
            'company_size_category': match_details.get('company_size_category', 'Unknown'),
            
            # Recommendations
            'recommendation': top_recommendation,
            'total_recommendations': len(recommendations)
        }
        
        audience_records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(audience_records)
    
    # Sort by relevance score (descending)
    df = df.sort_values('relevance_score', ascending=False)
    
    # Calculate summary statistics
    summary_row = {
        'audience_id': '=== SUMMARY STATISTICS ===',
        'profile_name': f"Total Audience: {len(df)}",
        'job_title': f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        'seniority': '',
        'company': '',
        'company_size': '',
        'industry': '',
        'location': '',
        'linkedin_followers': f"Avg: {df['linkedin_followers'].mean():.0f}" if not df.empty else '',
        
        'relevance_score': f"Avg: {df['relevance_score'].mean():.1f}" if not df.empty else '',
        'relevance_label': f"High: {(df['relevance_label'] == 'High').sum()}" if not df.empty else '',
        'lead_priority': f"Hot: {(df['lead_priority'] == 'Hot').sum()}" if not df.empty else '',
        'confidence': '',
        
        'role_score': f"Avg: {df['role_score'].mean():.1f}" if not df.empty else '',
        'seniority_score': f"Avg: {df['seniority_score'].mean():.1f}" if not df.empty else '',
        'industry_score': f"Avg: {df['industry_score'].mean():.1f}" if not df.empty else '',
        'company_size_score': f"Avg: {df['company_size_score'].mean():.1f}" if not df.empty else '',
        'bonus_score': f"Avg: {df['bonus_score'].mean():.1f}" if not df.empty else '',
        
        'icp_match_reason': '',
        'role_match_type': '',
        'company_size_category': '',
        'recommendation': '',
        'total_recommendations': ''
    }
    
    # Add summary row at top
    summary_df = pd.DataFrame([summary_row])
    df_with_summary = pd.concat([summary_df, df], ignore_index=True)
    
    # Save to CSV
    output_path = Path(output_dir) / 'audience_ranking.csv'
    df_with_summary.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Audience ranking CSV saved: {output_path}")
    print(f"   • {len(df)} audience member(s) scored")
    print(f"   • Average relevance score: {df['relevance_score'].mean():.1f}/100" if not df.empty else "")
    print(f"   • Hot leads: {(df['lead_priority'] == 'Hot').sum()}" if not df.empty else "")
    
    return str(output_path)


def _extract_post_id(url: str) -> Optional[str]:
    """Extract post ID from LinkedIn URL."""
    if not url:
        return None
    
    # LinkedIn post URLs typically end with activity-{POST_ID}
    try:
        if 'activity-' in url:
            parts = url.split('activity-')
            if len(parts) > 1:
                post_id = parts[1].split('-')[0]  # Get first part after activity-
                return f"POST-{post_id[:12]}"  # Truncate to reasonable length
    except Exception:
        pass
    
    return None


def _format_match_reason(match_details: Dict[str, Any], score_breakdown: Dict[str, Any]) -> str:
    """Format a concise ICP match reason string."""
    
    reasons = []
    
    # Role match
    role_match = match_details.get('role_match_type', 'none')
    if role_match == 'exact':
        reasons.append(f"Exact role match ({match_details.get('role_matched', 'N/A')})")
    elif role_match in ['high_keyword', 'medium_keyword']:
        reasons.append(f"Role keyword match ({match_details.get('role_matched', 'N/A')})")
    else:
        reasons.append("Role mismatch")
    
    # Seniority
    seniority = match_details.get('seniority_detected')
    if seniority:
        reasons.append(f"{seniority} level")
    
    # Industry
    industry = match_details.get('industry_matched')
    if industry and industry != 'Unknown':
        reasons.append(f"{industry} industry")
    
    # Company size
    size_cat = match_details.get('company_size_category')
    if size_cat and size_cat != 'Unknown':
        reasons.append(f"{size_cat} company size")
    
    # Bonus signals
    bonus_signals = match_details.get('bonus_signals_found', [])
    if bonus_signals:
        reasons.append(f"+{len(bonus_signals)} bonus signals")
    
    return "; ".join(reasons) if reasons else "No strong ICP match"


def _generate_summary_statistics(
    post_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    audience_data: Optional[List[Dict[str, Any]]]
) -> str:
    """Generate a text summary of all analysis results."""
    
    scraped = analysis_data.get('scraped_data', post_data)
    features = analysis_data.get('text_features', {})
    sentiment = features.get('sentiment', {})
    prediction = analysis_data.get('engagement_prediction', {})
    
    summary_lines = [
        "="*70,
        "LINKEDIN POST ANALYSIS - SUMMARY STATISTICS",
        "="*70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "POST PERFORMANCE:",
        f"  • Current Engagement: {(scraped.get('likes') or 0) + (scraped.get('comments') or 0) + (scraped.get('shares') or 0)} total",
        f"    - Likes: {scraped.get('likes') or 0}",
        f"    - Comments: {scraped.get('comments') or 0}",
        f"    - Shares: {scraped.get('shares') or 0}",
        f"  • Predicted Score: {prediction.get('engagement_score', 0)}/100",
        f"  • Performance Label: {prediction.get('prediction_label', 'N/A')}",
        f"  • Percentile: {prediction.get('percentile', 'N/A')}",
        "",
        "CONTENT ANALYSIS:",
        f"  • Word Count: {features.get('word_count', 0)}",
        f"  • Hashtags: {features.get('hashtag_count', 0)}",
        f"  • Emojis: {features.get('emoji_count', 0)}",
        f"  • URLs: {features.get('url_count', 0)}",
        f"  • Has CTA: {'Yes' if features.get('has_call_to_action') else 'No'}",
        "",
        "SENTIMENT:",
        f"  • Label: {sentiment.get('sentiment_label', 'N/A').title()}",
        f"  • Intensity: {sentiment.get('intensity', 'N/A')}",
        f"  • Compound Score: {sentiment.get('compound_score', 0):.3f}",
        f"  • Positive: {sentiment.get('positive_score', 0):.1%}",
        f"  • Negative: {sentiment.get('negative_score', 0):.1%}",
    ]
    
    # Add audience statistics if available
    if audience_data:
        hot_leads = sum(1 for m in audience_data if m.get('relevance', {}).get('lead_priority') == 'Hot')
        warm_leads = sum(1 for m in audience_data if m.get('relevance', {}).get('lead_priority') == 'Warm')
        avg_score = sum(m.get('relevance', {}).get('relevance_score', 0) for m in audience_data) / len(audience_data)
        
        summary_lines.extend([
            "",
            "AUDIENCE ANALYSIS:",
            f"  • Total Audience Members: {len(audience_data)}",
            f"  • Average Relevance Score: {avg_score:.1f}/100",
            f"  • Hot Leads: {hot_leads}",
            f"  • Warm Leads: {warm_leads}",
            f"  • Cold Leads: {len(audience_data) - hot_leads - warm_leads}",
        ])
    
    summary_lines.extend([
        "",
        "="*70
    ])
    
    return "\n".join(summary_lines)


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("CSV EXPORT GENERATOR - DEMONSTRATION")
    print("="*70)
    
    # Generate post analysis CSV
    print("\n📊 Generating CSV exports...")
    
    # Example: Generate without audience data
    results = generate_analysis_outputs(
        post_data_path="data/json/post_data_sample.json",
        analysis_data_path="data/json/post_analysis.json"
    )
    
    print("\n📁 FILES GENERATED:")
    print(f"  • Post Analysis: {results['post_analysis_csv']}")
    if results['audience_ranking_csv']:
        print(f"  • Audience Ranking: {results['audience_ranking_csv']}")
    
    print("\n" + results['summary'])
    
    # Example with sample audience data
    print("\n\n" + "="*70)
    print("GENERATING WITH SAMPLE AUDIENCE DATA")
    print("="*70)
    
    # Import ICP analyzer for sample data
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        from icp_analyzer import define_icp, calculate_audience_relevance_score
        
        # Create sample audience
        sample_profiles = [
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
        
        # Score audience
        icp = define_icp()
        scored_audience = []
        for profile in sample_profiles:
            score = calculate_audience_relevance_score(profile, icp)
            scored_audience.append({
                'profile': profile,
                'relevance': score
            })
        
        # Generate CSVs with audience data
        results = generate_analysis_outputs(
            post_data_path="data/json/post_data_sample.json",
            analysis_data_path="data/json/post_analysis.json",
            audience_data=scored_audience
        )
        
        print("\n✅ DEMONSTRATION COMPLETE!")
        print("="*70)
        
    except ImportError:
        print("\n⚠️ ICP analyzer not available - skipping audience demo")
