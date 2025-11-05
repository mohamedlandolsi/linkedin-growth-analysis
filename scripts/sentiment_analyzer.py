"""
LinkedIn Post Sentiment Analyzer

This module provides sentiment analysis specifically optimized for LinkedIn and
social media content using VADER (Valence Aware Dictionary and sEntiment Reasoner).

WHY VADER FOR SOCIAL MEDIA?
============================
VADER is superior to TextBlob for social media sentiment analysis because:

1. **Social Media Optimized**: Pre-trained on social media text with slang, emoticons, 
   and modern internet language patterns.

2. **Emoji & Emoticon Aware**: Natively understands emojis (😊, 🎉) and emoticons (:), :(, :D)
   without additional preprocessing.

3. **Punctuation Sensitivity**: Recognizes that "good!!!" is more positive than "good"
   - exclamation marks amplify sentiment intensity.

4. **Capitalization Detection**: "AMAZING" is scored more intensely than "amazing"
   - important for social media emphasis.

5. **Degree Modifiers**: Handles intensifiers ("very good") and negations ("not bad")
   with contextual understanding.

6. **Slang & Acronyms**: Includes modern slang (lit, sucks, meh) and acronyms (LOL, OMG).

7. **No Training Required**: Rule-based lexicon approach means no training data needed
   and consistent results across domains.

8. **Speed**: Extremely fast - processes text in milliseconds, ideal for batch analysis.

TextBlob vs VADER Comparison:
------------------------------
| Feature              | VADER          | TextBlob      |
|---------------------|----------------|---------------|
| Social Media Focus  | ✅ Optimized   | ❌ General    |
| Emoji Support       | ✅ Native      | ❌ Limited    |
| Punctuation Impact  | ✅ Yes         | ❌ No         |
| Speed               | ✅ Very Fast   | ⚠️ Slower     |
| Accuracy (Social)   | ✅ ~80-85%     | ⚠️ ~70-75%    |

BEST PRACTICES FOR SOCIAL MEDIA SENTIMENT ANALYSIS:
===================================================
1. **Keep Original Text**: Don't over-normalize - VADER needs caps, punctuation, emojis
2. **Context Matters**: Professional posts may have different sentiment than casual ones
3. **Hashtag Handling**: VADER treats #happy similar to "happy"
4. **Multiple Scores**: Use compound score for overall, but check individual scores for nuance
5. **Threshold Tuning**: Default thresholds work well, but can be adjusted for your use case
6. **Sarcasm Limitation**: No sentiment analyzer handles sarcasm perfectly - manual review needed
7. **Domain Adaptation**: LinkedIn is more professional than Twitter - interpret accordingly
"""

from typing import Dict, Tuple, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialize VADER analyzer (singleton pattern for performance)
_vader_analyzer = None


def get_vader_analyzer() -> SentimentIntensityAnalyzer:
    """
    Get or create VADER sentiment analyzer instance (singleton).
    
    Returns:
        SentimentIntensityAnalyzer: VADER analyzer instance
    """
    global _vader_analyzer
    if _vader_analyzer is None:
        _vader_analyzer = SentimentIntensityAnalyzer()
    return _vader_analyzer


def analyze_sentiment(post_text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of LinkedIn post text using VADER.
    
    VADER returns four sentiment scores:
    - positive: Proportion of text that is positive (0.0 to 1.0)
    - neutral: Proportion of text that is neutral (0.0 to 1.0)
    - negative: Proportion of text that is negative (0.0 to 1.0)
    - compound: Overall sentiment score normalized between -1 (most negative) and +1 (most positive)
    
    The compound score is the most useful single metric:
    - >= 0.05: Positive sentiment
    - > -0.05 and < 0.05: Neutral sentiment
    - <= -0.05: Negative sentiment
    
    Args:
        post_text (str): The LinkedIn post text to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing:
            - sentiment_label (str): 'positive', 'neutral', or 'negative'
            - compound_score (float): Overall sentiment score (-1 to +1)
            - positive_score (float): Positive proportion (0 to 1)
            - neutral_score (float): Neutral proportion (0 to 1)
            - negative_score (float): Negative proportion (0 to 1)
            - intensity (str): Sentiment intensity category
            - confidence (str): Confidence level based on score magnitude
    
    Example:
        >>> text = "Amazing opportunity! 🚀 So excited to share this!"
        >>> result = analyze_sentiment(text)
        >>> print(result['sentiment_label'])
        'positive'
        >>> print(result['intensity'])
        'very positive'
    """
    
    if not post_text or not isinstance(post_text, str):
        return _empty_sentiment()
    
    # Get VADER analyzer
    analyzer = get_vader_analyzer()
    
    # Perform sentiment analysis
    # VADER automatically handles:
    # - Emojis: 😊 🎉 😢 ❤️ etc.
    # - Exclamation marks: "Great!" vs "Great!!!"
    # - Capitalization: "LOVE" vs "love"
    # - Repeated letters: "loooove" is recognized as emphasis
    # - Hashtags: #happy is treated like "happy"
    # - Degree modifiers: "very good", "really bad"
    # - Negations: "not good", "don't like"
    scores = analyzer.polarity_scores(post_text)
    
    # Extract individual scores
    compound = scores['compound']
    positive = scores['pos']
    neutral = scores['neu']
    negative = scores['neg']
    
    # Determine sentiment label using standard VADER thresholds
    if compound >= 0.05:
        sentiment_label = 'positive'
    elif compound <= -0.05:
        sentiment_label = 'negative'
    else:
        sentiment_label = 'neutral'
    
    # Determine intensity category
    intensity = categorize_sentiment_intensity(compound)
    
    # Determine confidence level
    confidence = _calculate_confidence(compound, positive, neutral, negative)
    
    return {
        'sentiment_label': sentiment_label,
        'compound_score': round(compound, 4),
        'positive_score': round(positive, 4),
        'neutral_score': round(neutral, 4),
        'negative_score': round(negative, 4),
        'intensity': intensity,
        'confidence': confidence,
        'interpretation': _get_interpretation(sentiment_label, intensity, compound)
    }


def categorize_sentiment_intensity(compound_score: float) -> str:
    """
    Categorize sentiment intensity based on compound score.
    
    Intensity Thresholds (based on VADER best practices):
    - Very Positive: compound >= 0.5
    - Positive: 0.05 <= compound < 0.5
    - Neutral: -0.05 < compound < 0.05
    - Negative: -0.5 < compound <= -0.05
    - Very Negative: compound <= -0.5
    
    Args:
        compound_score (float): VADER compound score (-1 to +1)
        
    Returns:
        str: Intensity category
    
    Example:
        >>> categorize_sentiment_intensity(0.7)
        'very positive'
        >>> categorize_sentiment_intensity(-0.3)
        'negative'
    """
    
    if compound_score >= 0.5:
        return 'very positive'
    elif compound_score >= 0.05:
        return 'positive'
    elif compound_score > -0.05:
        return 'neutral'
    elif compound_score > -0.5:
        return 'negative'
    else:
        return 'very negative'


def analyze_sentiment_with_context(post_text: str, 
                                   engagement_metrics: Dict[str, int] = None) -> Dict[str, Any]:
    """
    Analyze sentiment with additional context from engagement metrics.
    
    This function combines sentiment analysis with engagement data to provide
    richer insights. High positive sentiment with low engagement might indicate
    the need for better distribution, while negative sentiment with high engagement
    could indicate controversial but engaging content.
    
    Args:
        post_text (str): The LinkedIn post text
        engagement_metrics (Dict[str, int], optional): Dictionary with 'likes', 'comments', 'shares'
        
    Returns:
        Dict[str, Any]: Sentiment analysis with engagement context
    """
    
    sentiment = analyze_sentiment(post_text)
    
    if engagement_metrics:
        total_engagement = sum(engagement_metrics.values())
        sentiment['total_engagement'] = total_engagement
        
        # Engagement-Sentiment alignment score
        # Positive posts should ideally have high engagement
        if sentiment['sentiment_label'] == 'positive' and total_engagement > 100:
            sentiment['engagement_sentiment_alignment'] = 'excellent'
        elif sentiment['sentiment_label'] == 'positive' and total_engagement > 50:
            sentiment['engagement_sentiment_alignment'] = 'good'
        elif sentiment['sentiment_label'] == 'negative' and total_engagement > 50:
            sentiment['engagement_sentiment_alignment'] = 'controversial'
        else:
            sentiment['engagement_sentiment_alignment'] = 'neutral'
    
    return sentiment


def batch_analyze_sentiments(post_texts: list) -> list:
    """
    Analyze sentiment for multiple posts efficiently.
    
    Args:
        post_texts (list): List of post text strings
        
    Returns:
        list: List of sentiment analysis dictionaries
    """
    return [analyze_sentiment(text) for text in post_texts]


def get_sentiment_statistics(sentiments: list) -> Dict[str, Any]:
    """
    Calculate statistics across multiple sentiment analyses.
    
    Args:
        sentiments (list): List of sentiment dictionaries from analyze_sentiment()
        
    Returns:
        Dict[str, Any]: Aggregate statistics
    """
    
    if not sentiments:
        return {}
    
    # Count by label
    positive_count = sum(1 for s in sentiments if s['sentiment_label'] == 'positive')
    neutral_count = sum(1 for s in sentiments if s['sentiment_label'] == 'neutral')
    negative_count = sum(1 for s in sentiments if s['sentiment_label'] == 'negative')
    
    total = len(sentiments)
    
    # Average scores
    avg_compound = sum(s['compound_score'] for s in sentiments) / total
    avg_positive = sum(s['positive_score'] for s in sentiments) / total
    avg_negative = sum(s['negative_score'] for s in sentiments) / total
    
    return {
        'total_posts': total,
        'positive_count': positive_count,
        'neutral_count': neutral_count,
        'negative_count': negative_count,
        'positive_percentage': round(positive_count / total * 100, 2),
        'neutral_percentage': round(neutral_count / total * 100, 2),
        'negative_percentage': round(negative_count / total * 100, 2),
        'average_compound_score': round(avg_compound, 4),
        'average_positive_score': round(avg_positive, 4),
        'average_negative_score': round(avg_negative, 4),
        'overall_sentiment': categorize_sentiment_intensity(avg_compound)
    }


def _calculate_confidence(compound: float, positive: float, 
                         neutral: float, negative: float) -> str:
    """
    Calculate confidence level based on score distribution.
    
    High confidence: Clear dominance of one sentiment (e.g., 80% positive, 10% neutral, 10% negative)
    Medium confidence: Moderate dominance (e.g., 60% positive, 30% neutral, 10% negative)
    Low confidence: Mixed sentiments (e.g., 40% positive, 30% neutral, 30% negative)
    
    Args:
        compound (float): Compound score
        positive (float): Positive proportion
        neutral (float): Neutral proportion
        negative (float): Negative proportion
        
    Returns:
        str: 'high', 'medium', or 'low'
    """
    
    # Strong compound score indicates high confidence
    if abs(compound) >= 0.5:
        return 'high'
    
    # Check if one sentiment clearly dominates
    max_score = max(positive, neutral, negative)
    
    if max_score >= 0.7:
        return 'high'
    elif max_score >= 0.5:
        return 'medium'
    else:
        return 'low'


def _get_interpretation(label: str, intensity: str, compound: float) -> str:
    """
    Get human-readable interpretation of sentiment.
    
    Args:
        label (str): Sentiment label
        intensity (str): Intensity category
        compound (float): Compound score
        
    Returns:
        str: Interpretation string
    """
    
    interpretations = {
        'very positive': f"Highly positive sentiment (score: {compound:.2f}) - Enthusiastic, excited, or celebratory tone",
        'positive': f"Positive sentiment (score: {compound:.2f}) - Optimistic, encouraging, or appreciative tone",
        'neutral': f"Neutral sentiment (score: {compound:.2f}) - Factual, informative, or balanced tone",
        'negative': f"Negative sentiment (score: {compound:.2f}) - Critical, disappointed, or concerned tone",
        'very negative': f"Highly negative sentiment (score: {compound:.2f}) - Strongly critical, angry, or distressed tone"
    }
    
    return interpretations.get(intensity, f"Sentiment: {label}")


def _empty_sentiment() -> Dict[str, Any]:
    """
    Return empty sentiment result for invalid input.
    
    Returns:
        Dict[str, Any]: Empty sentiment dictionary
    """
    return {
        'sentiment_label': 'neutral',
        'compound_score': 0.0,
        'positive_score': 0.0,
        'neutral_score': 1.0,
        'negative_score': 0.0,
        'intensity': 'neutral',
        'confidence': 'low',
        'interpretation': 'No text provided for analysis'
    }


# Example usage and demonstration
if __name__ == "__main__":
    print("="*80)
    print("LINKEDIN SENTIMENT ANALYZER - DEMONSTRATION")
    print("="*80)
    print("\n📚 WHY VADER FOR SOCIAL MEDIA?")
    print("-"*80)
    print("✅ Optimized for social media language, slang, and modern expressions")
    print("✅ Native emoji and emoticon support (😊, 🎉, :), :()")
    print("✅ Recognizes punctuation emphasis (good vs good!!!)")
    print("✅ Handles capitalization (amazing vs AMAZING)")
    print("✅ Understands degree modifiers (very good, really bad)")
    print("✅ Fast and efficient - no training required")
    print("✅ ~80-85% accuracy on social media text vs ~70-75% for TextBlob")
    
    # Test cases demonstrating VADER's capabilities
    test_posts = [
        {
            'text': "🎉 AMAZING NEWS! We're thrilled to announce our Series B funding! This is HUGE for our team! 🚀🚀🚀",
            'description': "Very positive with emojis, caps, and exclamations"
        },
        {
            'text': "Excited to share my new article on AI in healthcare. Check it out! 👉 #AI #Healthcare",
            'description': "Positive with hashtags and emoji"
        },
        {
            'text': "Interesting insights from today's conference. Looking forward to implementing some of these strategies.",
            'description': "Moderately positive, professional tone"
        },
        {
            'text': "Our quarterly report shows steady growth across all metrics. Revenue up 15%, customer satisfaction remains high.",
            'description': "Positive but neutral tone (factual)"
        },
        {
            'text': "Today marks my 5 year anniversary at the company. Time flies!",
            'description': "Neutral with slight positive"
        },
        {
            'text': "Unfortunately, we need to postpone the event due to unforeseen circumstances. Apologies for any inconvenience.",
            'description': "Negative but polite"
        },
        {
            'text': "This is NOT acceptable. Extremely disappointed with the service quality. Will not recommend. 😠",
            'description': "Very negative with negation and angry emoji"
        },
        {
            'text': "loooove this idea!!! So innovative and creative!!! 💡✨",
            'description': "Very positive with repeated letters and multiple exclamations"
        }
    ]
    
    print("\n\n📊 SENTIMENT ANALYSIS EXAMPLES:")
    print("="*80)
    
    results = []
    for i, post in enumerate(test_posts, 1):
        print(f"\n{i}. {post['description']}")
        print("-"*80)
        print(f"Text: \"{post['text']}\"")
        print()
        
        result = analyze_sentiment(post['text'])
        results.append(result)
        
        print(f"📊 Sentiment: {result['sentiment_label'].upper()} ({result['intensity']})")
        print(f"📈 Compound Score: {result['compound_score']} (range: -1 to +1)")
        print(f"   • Positive: {result['positive_score']:.1%}")
        print(f"   • Neutral:  {result['neutral_score']:.1%}")
        print(f"   • Negative: {result['negative_score']:.1%}")
        print(f"🎯 Confidence: {result['confidence']}")
        print(f"💭 {result['interpretation']}")
    
    # Show aggregate statistics
    print("\n\n📈 AGGREGATE STATISTICS:")
    print("="*80)
    stats = get_sentiment_statistics(results)
    print(f"Total Posts Analyzed: {stats['total_posts']}")
    print(f"Positive Posts: {stats['positive_count']} ({stats['positive_percentage']}%)")
    print(f"Neutral Posts: {stats['neutral_count']} ({stats['neutral_percentage']}%)")
    print(f"Negative Posts: {stats['negative_count']} ({stats['negative_percentage']}%)")
    print(f"\nAverage Compound Score: {stats['average_compound_score']}")
    print(f"Overall Sentiment: {stats['overall_sentiment']}")
    
    print("\n\n✅ DEMONSTRATION COMPLETE!")
    print("="*80)
