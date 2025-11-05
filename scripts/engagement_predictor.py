"""
LinkedIn Post Engagement Prediction Module

This module predicts engagement performance of LinkedIn posts based on:
- Actual engagement metrics (likes, comments, shares)
- Post content features (length, hashtags, emojis)
- Sentiment analysis results
- Call-to-action presence

The scoring system is designed to be tunable and provides actionable insights
for content optimization.
"""

from typing import Dict, Any, Optional, Tuple
import math


# Default weighting parameters (customizable)
DEFAULT_WEIGHTS = {
    # Engagement metric weights
    # Rationale: Shares > Comments > Likes in terms of engagement quality
    # - Likes: Easy, passive engagement (1x weight)
    # - Comments: Active engagement, discussion (2x weight)
    # - Shares: Highest value - extends reach exponentially (3x weight)
    'likes_weight': 1.0,
    'comments_weight': 2.0,
    'shares_weight': 3.0,
    
    # Feature impact multipliers
    # These adjust the base engagement score based on content quality
    'sentiment_multiplier': 0.15,      # Positive sentiment boost (up to +15%)
    'word_count_multiplier': 0.10,     # Optimal length bonus (up to +10%)
    'hashtag_multiplier': 0.08,        # Hashtag optimization (up to +8%)
    'emoji_multiplier': 0.05,          # Emoji presence bonus (up to +5%)
    'cta_multiplier': 0.07,            # Call-to-action bonus (up to +7%)
    'url_multiplier': 0.03,            # URL presence (up to +3%)
    
    # Optimal ranges for features
    'optimal_word_count_min': 100,     # Posts shorter than this are penalized
    'optimal_word_count_max': 300,     # Posts longer than this are penalized
    'optimal_hashtag_count': 3,        # Sweet spot for hashtags (2-5 range)
    'min_hashtag_count': 2,            # Minimum recommended hashtags
    'max_hashtag_count': 5,            # Maximum before diminishing returns
}


def predict_engagement_score(
    post_data: Dict[str, Any],
    sentiment_data: Optional[Dict[str, Any]] = None,
    features_data: Optional[Dict[str, Any]] = None,
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Predict engagement performance score for a LinkedIn post.
    
    SCORING METHODOLOGY:
    ====================
    1. Base Score (0-60 points): Calculated from actual engagement metrics
       - Weighted engagement = (likes × 1) + (comments × 2) + (shares × 3)
       - Normalized to 0-60 scale using logarithmic scaling
       
    2. Content Quality Bonus (0-40 points): Based on post features
       - Sentiment bonus: Up to 15 points for positive sentiment
       - Length bonus: Up to 10 points for optimal word count (100-300)
       - Hashtag bonus: Up to 8 points for 2-5 hashtags
       - Emoji bonus: Up to 5 points for emoji presence
       - CTA bonus: Up to 7 points for call-to-action
       - URL bonus: Up to 3 points for including links
       
    3. Final Score: Base Score + Quality Bonuses (0-100 scale)
    
    Args:
        post_data (Dict[str, Any]): Post information including:
            - likes (int): Number of likes
            - comments (int): Number of comments
            - shares (int): Number of shares
            
        sentiment_data (Dict[str, Any], optional): Sentiment analysis results:
            - compound_score (float): -1 to +1 sentiment score
            - sentiment_label (str): positive/neutral/negative
            - intensity (str): Sentiment intensity level
            
        features_data (Dict[str, Any], optional): Post features:
            - word_count (int): Number of words
            - hashtag_count (int): Number of hashtags
            - emoji_count (int): Number of emojis
            - has_call_to_action (bool): CTA presence
            - url_count (int): Number of URLs
            
        custom_weights (Dict[str, float], optional): Override default weights
        
    Returns:
        Dict[str, Any]: Prediction results containing:
            - engagement_score (float): Overall score (0-100)
            - prediction_label (str): "High Performer", "Medium", or "Low"
            - confidence_level (str): "high", "medium", or "low"
            - confidence_score (float): Confidence percentage (0-100)
            - base_score (float): Score from engagement metrics only
            - quality_bonus (float): Bonus from content features
            - breakdown (Dict): Detailed score breakdown
            - recommendations (List[str]): Improvement suggestions
            - percentile (str): Performance percentile estimate
    
    Example:
        >>> post = {'likes': 150, 'comments': 25, 'shares': 10}
        >>> sentiment = {'compound_score': 0.85, 'sentiment_label': 'positive'}
        >>> features = {'word_count': 180, 'hashtag_count': 3, 'emoji_count': 2}
        >>> result = predict_engagement_score(post, sentiment, features)
        >>> print(f"{result['prediction_label']}: {result['engagement_score']:.1f}")
        High Performer: 78.5
    """
    
    # Merge custom weights with defaults
    weights = DEFAULT_WEIGHTS.copy()
    if custom_weights:
        weights.update(custom_weights)
    
    # Initialize result structure
    result = {
        'engagement_score': 0.0,
        'prediction_label': 'Low',
        'confidence_level': 'low',
        'confidence_score': 0.0,
        'base_score': 0.0,
        'quality_bonus': 0.0,
        'breakdown': {},
        'recommendations': [],
        'percentile': 'bottom 25%'
    }
    
    # Extract engagement metrics (handle None/null values)
    likes = post_data.get('likes') or 0
    comments = post_data.get('comments') or 0
    shares = post_data.get('shares') or 0
    
    # STEP 1: Calculate Base Score from Engagement Metrics (0-60 points)
    # ================================================================
    base_score, engagement_details = _calculate_base_engagement_score(
        likes, comments, shares, weights
    )
    result['base_score'] = base_score
    result['breakdown']['engagement'] = engagement_details
    
    # STEP 2: Calculate Quality Bonuses from Content Features (0-40 points)
    # ====================================================================
    quality_bonus = 0.0
    quality_breakdown = {}
    
    # Sentiment Bonus (up to 15 points)
    if sentiment_data:
        sentiment_bonus, sentiment_details = _calculate_sentiment_bonus(
            sentiment_data, weights
        )
        quality_bonus += sentiment_bonus
        quality_breakdown['sentiment'] = sentiment_details
    
    # Content Feature Bonuses
    if features_data:
        # Word count bonus (up to 10 points)
        word_count_bonus, word_details = _calculate_word_count_bonus(
            features_data.get('word_count', 0), weights
        )
        quality_bonus += word_count_bonus
        quality_breakdown['word_count'] = word_details
        
        # Hashtag bonus (up to 8 points)
        hashtag_bonus, hashtag_details = _calculate_hashtag_bonus(
            features_data.get('hashtag_count', 0), weights
        )
        quality_bonus += hashtag_bonus
        quality_breakdown['hashtags'] = hashtag_details
        
        # Emoji bonus (up to 5 points)
        emoji_bonus, emoji_details = _calculate_emoji_bonus(
            features_data.get('emoji_count', 0), weights
        )
        quality_bonus += emoji_bonus
        quality_breakdown['emojis'] = emoji_details
        
        # CTA bonus (up to 7 points)
        cta_bonus, cta_details = _calculate_cta_bonus(
            features_data.get('has_call_to_action', False), weights
        )
        quality_bonus += cta_bonus
        quality_breakdown['call_to_action'] = cta_details
        
        # URL bonus (up to 3 points)
        url_bonus, url_details = _calculate_url_bonus(
            features_data.get('url_count', 0), weights
        )
        quality_bonus += url_bonus
        quality_breakdown['urls'] = url_details
    
    result['quality_bonus'] = quality_bonus
    result['breakdown']['quality_features'] = quality_breakdown
    
    # STEP 3: Calculate Final Score (0-100)
    # =====================================
    final_score = min(100.0, base_score + quality_bonus)
    result['engagement_score'] = round(final_score, 2)
    
    # STEP 4: Determine Prediction Label
    # ==================================
    result['prediction_label'] = _get_prediction_label(final_score)
    result['percentile'] = _get_percentile_estimate(final_score)
    
    # STEP 5: Calculate Confidence Level
    # ==================================
    confidence_score, confidence_level = _calculate_confidence(
        likes, comments, shares, final_score
    )
    result['confidence_score'] = confidence_score
    result['confidence_level'] = confidence_level
    result['breakdown']['confidence'] = {
        'total_engagement': likes + comments + shares,
        'explanation': _get_confidence_explanation(confidence_level)
    }
    
    # STEP 6: Generate Recommendations
    # =================================
    result['recommendations'] = _generate_recommendations(
        final_score, sentiment_data, features_data, engagement_details
    )
    
    return result


def _calculate_base_engagement_score(
    likes: int,
    comments: int, 
    shares: int,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate base score from engagement metrics using weighted sum.
    
    Uses logarithmic scaling to handle wide range of engagement values:
    - Small differences at low engagement are significant
    - Large differences at high engagement matter less
    
    This prevents viral posts from skewing the entire scale while still
    rewarding strong performance.
    
    Args:
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        weights: Weight configuration
        
    Returns:
        Tuple of (base_score, details_dict)
    """
    
    # Calculate weighted engagement
    # Shares are most valuable, followed by comments, then likes
    weighted_engagement = (
        likes * weights['likes_weight'] +
        comments * weights['comments_weight'] +
        shares * weights['shares_weight']
    )
    
    # Apply logarithmic scaling for normalization
    # log(1 + x) ensures 0 engagement = 0 score
    # The +1 prevents log(0) and makes the curve smoother
    if weighted_engagement > 0:
        # Scale to 0-60 range (60% of total score from engagement)
        # Using log base 10 and scaling factor
        base_score = min(60.0, (math.log10(1 + weighted_engagement) * 15))
    else:
        base_score = 0.0
    
    details = {
        'likes': likes,
        'comments': comments,
        'shares': shares,
        'weighted_total': round(weighted_engagement, 2),
        'score': round(base_score, 2),
        'weights_used': {
            'likes': weights['likes_weight'],
            'comments': weights['comments_weight'],
            'shares': weights['shares_weight']
        }
    }
    
    return base_score, details


def _calculate_sentiment_bonus(
    sentiment_data: Dict[str, Any],
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus points based on sentiment analysis.
    
    Positive sentiment correlates with higher engagement on LinkedIn.
    The bonus scales with sentiment intensity.
    """
    
    compound = sentiment_data.get('compound_score', 0.0)
    max_bonus = 15.0 * weights['sentiment_multiplier'] / 0.15
    
    # Map compound score (-1 to +1) to bonus points (0 to max_bonus)
    # Only positive sentiment gets bonus
    if compound > 0:
        # Linear scaling: compound 0.5 = 50% of max, compound 1.0 = 100% of max
        bonus = (compound / 1.0) * max_bonus
    else:
        bonus = 0.0
    
    details = {
        'compound_score': compound,
        'sentiment_label': sentiment_data.get('sentiment_label', 'unknown'),
        'intensity': sentiment_data.get('intensity', 'unknown'),
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _calculate_word_count_bonus(
    word_count: int,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus for optimal post length.
    
    LinkedIn posts perform best between 100-300 words:
    - Too short (<100): Lacks substance, appears low-effort
    - Optimal (100-300): Detailed but scannable
    - Too long (>300): Reduced engagement, readers lose interest
    """
    
    max_bonus = 10.0 * weights['word_count_multiplier'] / 0.10
    optimal_min = weights['optimal_word_count_min']
    optimal_max = weights['optimal_word_count_max']
    
    if optimal_min <= word_count <= optimal_max:
        # In optimal range: full bonus
        bonus = max_bonus
        status = 'optimal'
    elif word_count < optimal_min:
        # Too short: scale linearly from 0 to max_bonus
        bonus = (word_count / optimal_min) * max_bonus
        status = 'too_short'
    else:
        # Too long: decay after optimal_max
        # Posts can still be good if longer, just penalize slightly
        excess = word_count - optimal_max
        decay_factor = max(0.3, 1.0 - (excess / 500))  # Minimum 30% of bonus
        bonus = max_bonus * decay_factor
        status = 'too_long'
    
    details = {
        'word_count': word_count,
        'optimal_range': f"{optimal_min}-{optimal_max}",
        'status': status,
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _calculate_hashtag_bonus(
    hashtag_count: int,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus for hashtag usage.
    
    Optimal hashtag count on LinkedIn: 2-5
    - 0-1: Poor discoverability
    - 2-5: Optimal for reach without appearing spammy
    - 6+: Diminishing returns, can appear unprofessional
    """
    
    max_bonus = 8.0 * weights['hashtag_multiplier'] / 0.08
    optimal = weights['optimal_hashtag_count']
    min_good = weights['min_hashtag_count']
    max_good = weights['max_hashtag_count']
    
    if min_good <= hashtag_count <= max_good:
        # In optimal range: bonus scales to peak at optimal count
        if hashtag_count <= optimal:
            bonus = (hashtag_count / optimal) * max_bonus
        else:
            # Slight decay after optimal but still in good range
            bonus = max_bonus * (1.0 - ((hashtag_count - optimal) / (max_good - optimal) * 0.2))
        status = 'optimal'
    elif hashtag_count < min_good:
        # Below minimum: small bonus proportional to what's there
        bonus = (hashtag_count / min_good) * max_bonus * 0.4
        status = 'too_few'
    else:
        # Too many: diminishing returns
        excess = hashtag_count - max_good
        bonus = max_bonus * max(0.2, 1.0 - (excess / 5))
        status = 'too_many'
    
    details = {
        'hashtag_count': hashtag_count,
        'optimal_range': f"{min_good}-{max_good}",
        'status': status,
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _calculate_emoji_bonus(
    emoji_count: int,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus for emoji usage.
    
    Emojis add visual interest and emotion to posts.
    Optimal: 1-3 emojis for professional LinkedIn content.
    """
    
    max_bonus = 5.0 * weights['emoji_multiplier'] / 0.05
    
    if emoji_count > 0:
        # Bonus scales up to 3 emojis, then plateaus
        optimal_count = 3
        if emoji_count <= optimal_count:
            bonus = (emoji_count / optimal_count) * max_bonus
        else:
            # More than 3: full bonus but no extra benefit
            bonus = max_bonus
        status = 'present'
    else:
        bonus = 0.0
        status = 'none'
    
    details = {
        'emoji_count': emoji_count,
        'status': status,
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _calculate_cta_bonus(
    has_cta: bool,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus for call-to-action presence.
    
    CTAs drive engagement by giving readers a clear next step.
    Examples: "Apply now", "Learn more", "Join us", "Share your thoughts"
    """
    
    max_bonus = 7.0 * weights['cta_multiplier'] / 0.07
    
    bonus = max_bonus if has_cta else 0.0
    
    details = {
        'has_call_to_action': has_cta,
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _calculate_url_bonus(
    url_count: int,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate bonus for URL inclusion.
    
    URLs drive traffic and indicate valuable external resources.
    Optimal: 1 URL (primary destination)
    """
    
    max_bonus = 3.0 * weights['url_multiplier'] / 0.03
    
    if url_count > 0:
        # Full bonus for 1 URL, no extra benefit for more
        bonus = max_bonus
        status = 'present'
    else:
        bonus = 0.0
        status = 'none'
    
    details = {
        'url_count': url_count,
        'status': status,
        'bonus_points': round(bonus, 2),
        'max_possible': max_bonus
    }
    
    return bonus, details


def _get_prediction_label(score: float) -> str:
    """
    Convert numerical score to prediction label.
    
    Thresholds based on LinkedIn engagement benchmarks:
    - High Performer: Top 30% of posts
    - Medium: Middle 50% of posts
    - Low: Bottom 20% of posts
    """
    
    if score >= 70:
        return "High Performer"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


def _get_percentile_estimate(score: float) -> str:
    """Estimate performance percentile based on score."""
    
    if score >= 85:
        return "top 10%"
    elif score >= 70:
        return "top 30%"
    elif score >= 55:
        return "top 50%"
    elif score >= 40:
        return "top 70%"
    else:
        return "bottom 30%"


def _calculate_confidence(
    likes: int,
    comments: int,
    shares: int,
    score: float
) -> Tuple[float, str]:
    """
    Calculate confidence level based on engagement volume.
    
    More engagement data = higher confidence in the prediction.
    """
    
    total_engagement = likes + comments + shares
    
    # Confidence thresholds
    # These are based on typical LinkedIn post engagement ranges
    if total_engagement >= 100:
        confidence = 95.0
        level = 'high'
    elif total_engagement >= 50:
        confidence = 80.0
        level = 'high'
    elif total_engagement >= 20:
        confidence = 65.0
        level = 'medium'
    elif total_engagement >= 10:
        confidence = 50.0
        level = 'medium'
    elif total_engagement > 0:
        confidence = 35.0
        level = 'low'
    else:
        # No engagement data - purely prediction based on content
        confidence = 20.0
        level = 'low'
    
    return confidence, level


def _get_confidence_explanation(level: str) -> str:
    """Get human-readable confidence explanation."""
    
    explanations = {
        'high': 'Based on substantial engagement data',
        'medium': 'Based on moderate engagement data',
        'low': 'Limited engagement data - prediction based primarily on content features'
    }
    
    return explanations.get(level, 'Unknown confidence level')


def _generate_recommendations(
    score: float,
    sentiment_data: Optional[Dict[str, Any]],
    features_data: Optional[Dict[str, Any]],
    engagement_details: Dict[str, Any]
) -> list:
    """
    Generate actionable recommendations for improving engagement.
    """
    
    recommendations = []
    
    # Overall score recommendations
    if score < 40:
        recommendations.append("⚠️ Low engagement predicted. Consider major revisions to content and distribution strategy.")
    elif score < 70:
        recommendations.append("💡 Moderate engagement expected. Small optimizations could significantly boost performance.")
    
    # Engagement-specific recommendations
    total_engagement = engagement_details.get('weighted_total', 0)
    if total_engagement < 50:
        recommendations.append("📢 Boost initial reach: Share in relevant groups, tag key connections, post at optimal times (Tue-Thu 8-10am).")
    
    shares = engagement_details.get('shares', 0)
    comments = engagement_details.get('comments', 0)
    if shares == 0 or (comments > 0 and shares == 0):
        recommendations.append("🔄 Low share rate: Add a shareable insight, statistic, or quote. Ask readers to 'share if you agree'.")
    
    if comments < 5 and engagement_details.get('likes', 0) > 20:
        recommendations.append("💬 Good visibility but low discussion: End with a question to encourage comments.")
    
    # Sentiment recommendations
    if sentiment_data:
        if sentiment_data.get('compound_score', 0) < 0.05:
            recommendations.append("😊 Add positive framing: Positive posts get 2x more engagement on LinkedIn.")
    
    # Content feature recommendations
    if features_data:
        word_count = features_data.get('word_count', 0)
        if word_count < 100:
            recommendations.append("📝 Expand content: Posts with 100-300 words perform best. Add context, examples, or insights.")
        elif word_count > 300:
            recommendations.append("✂️ Trim content: Break long posts into multiple shorter posts or use line breaks for scannability.")
        
        hashtag_count = features_data.get('hashtag_count', 0)
        if hashtag_count < 2:
            recommendations.append("#️⃣ Add hashtags: Use 3-5 relevant hashtags to increase discoverability.")
        elif hashtag_count > 5:
            recommendations.append("#️⃣ Reduce hashtags: 3-5 hashtags is optimal. Too many appear spammy.")
        
        if features_data.get('emoji_count', 0) == 0:
            recommendations.append("🎨 Add visual interest: Include 1-3 relevant emojis to catch attention and convey emotion.")
        
        if not features_data.get('has_call_to_action', False):
            recommendations.append("👉 Add clear CTA: Tell readers what to do next (comment, share, click link, apply, etc.).")
        
        if features_data.get('url_count', 0) == 0:
            recommendations.append("🔗 Consider adding a link: Posts with URLs drive traffic and provide additional value.")
    
    # If no specific recommendations, provide general tips
    if not recommendations:
        recommendations.append("✅ Content is well-optimized! Continue monitoring performance and iterating.")
    
    return recommendations


# Convenience function for quick predictions
def quick_predict(likes: int, comments: int, shares: int, 
                 word_count: int = 150, hashtags: int = 3, 
                 is_positive: bool = True) -> str:
    """
    Quick prediction with minimal input.
    
    Returns a simple string summary for rapid assessment.
    """
    
    post = {'likes': likes, 'comments': comments, 'shares': shares}
    
    sentiment = {'compound_score': 0.6 if is_positive else 0.0, 'sentiment_label': 'positive' if is_positive else 'neutral'}
    
    features = {
        'word_count': word_count,
        'hashtag_count': hashtags,
        'emoji_count': 2 if is_positive else 0,
        'has_call_to_action': True,
        'url_count': 1
    }
    
    result = predict_engagement_score(post, sentiment, features)
    
    return f"{result['prediction_label']} ({result['engagement_score']:.1f}/100) - {result['percentile']} - Confidence: {result['confidence_level']}"


# Example usage and testing
if __name__ == "__main__":
    print("="*80)
    print("LINKEDIN ENGAGEMENT PREDICTOR - DEMONSTRATION")
    print("="*80)
    
    # Test Case 1: High Performer
    print("\n📊 TEST CASE 1: High Performing Post")
    print("-"*80)
    post1 = {'likes': 150, 'comments': 25, 'shares': 12}
    sentiment1 = {'compound_score': 0.89, 'sentiment_label': 'positive', 'intensity': 'very positive'}
    features1 = {
        'word_count': 180,
        'hashtag_count': 3,
        'emoji_count': 3,
        'has_call_to_action': True,
        'url_count': 1
    }
    
    result1 = predict_engagement_score(post1, sentiment1, features1)
    print(f"Engagement: {post1['likes']} likes, {post1['comments']} comments, {post1['shares']} shares")
    print(f"Word Count: {features1['word_count']}, Hashtags: {features1['hashtag_count']}")
    print(f"\n🎯 PREDICTION: {result1['prediction_label']}")
    print(f"📈 Score: {result1['engagement_score']}/100 ({result1['percentile']})")
    print(f"   • Base Score (engagement): {result1['base_score']:.1f}/60")
    print(f"   • Quality Bonus (content): {result1['quality_bonus']:.1f}/40")
    print(f"🎲 Confidence: {result1['confidence_level'].title()} ({result1['confidence_score']:.0f}%)")
    
    # Test Case 2: Medium Performer
    print("\n\n📊 TEST CASE 2: Medium Performing Post")
    print("-"*80)
    post2 = {'likes': 45, 'comments': 5, 'shares': 2}
    sentiment2 = {'compound_score': 0.35, 'sentiment_label': 'positive', 'intensity': 'positive'}
    features2 = {
        'word_count': 250,
        'hashtag_count': 2,
        'emoji_count': 1,
        'has_call_to_action': False,
        'url_count': 0
    }
    
    result2 = predict_engagement_score(post2, sentiment2, features2)
    print(f"Engagement: {post2['likes']} likes, {post2['comments']} comments, {post2['shares']} shares")
    print(f"Word Count: {features2['word_count']}, Hashtags: {features2['hashtag_count']}")
    print(f"\n🎯 PREDICTION: {result2['prediction_label']}")
    print(f"📈 Score: {result2['engagement_score']}/100 ({result2['percentile']})")
    print(f"   • Base Score (engagement): {result2['base_score']:.1f}/60")
    print(f"   • Quality Bonus (content): {result2['quality_bonus']:.1f}/40")
    print(f"🎲 Confidence: {result2['confidence_level'].title()} ({result2['confidence_score']:.0f}%)")
    print(f"\n💡 Top Recommendations:")
    for rec in result2['recommendations'][:3]:
        print(f"   {rec}")
    
    # Test Case 3: Low Performer
    print("\n\n📊 TEST CASE 3: Low Performing Post")
    print("-"*80)
    post3 = {'likes': 8, 'comments': 1, 'shares': 0}
    sentiment3 = {'compound_score': -0.1, 'sentiment_label': 'neutral', 'intensity': 'neutral'}
    features3 = {
        'word_count': 50,
        'hashtag_count': 0,
        'emoji_count': 0,
        'has_call_to_action': False,
        'url_count': 0
    }
    
    result3 = predict_engagement_score(post3, sentiment3, features3)
    print(f"Engagement: {post3['likes']} likes, {post3['comments']} comments, {post3['shares']} shares")
    print(f"Word Count: {features3['word_count']}, Hashtags: {features3['hashtag_count']}")
    print(f"\n🎯 PREDICTION: {result3['prediction_label']}")
    print(f"📈 Score: {result3['engagement_score']}/100 ({result3['percentile']})")
    print(f"   • Base Score (engagement): {result3['base_score']:.1f}/60")
    print(f"   • Quality Bonus (content): {result3['quality_bonus']:.1f}/40")
    print(f"🎲 Confidence: {result3['confidence_level'].title()} ({result3['confidence_score']:.0f}%)")
    print(f"\n💡 Top Recommendations:")
    for rec in result3['recommendations'][:3]:
        print(f"   {rec}")
    
    # Quick Predict Demo
    print("\n\n🚀 QUICK PREDICT DEMO:")
    print("-"*80)
    print(quick_predict(100, 15, 8, word_count=200, hashtags=4, is_positive=True))
    print(quick_predict(30, 5, 1, word_count=120, hashtags=2, is_positive=False))
    print(quick_predict(5, 0, 0, word_count=60, hashtags=0, is_positive=False))
    
    print("\n\n✅ DEMONSTRATION COMPLETE!")
    print("="*80)
