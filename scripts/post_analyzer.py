"""
LinkedIn Post Text Analyzer

This module provides functionality to analyze LinkedIn post text and extract
various features including hashtags, mentions, URLs, statistics, and engagement signals.
"""

import re
from typing import Dict, List, Any
from collections import Counter

# Import sentiment analyzer
try:
    from sentiment_analyzer import analyze_sentiment
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False


def extract_post_features(post_text: str) -> Dict[str, Any]:
    """
    Extract comprehensive features from LinkedIn post text.
    
    Args:
        post_text (str): The text content of the LinkedIn post
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted features:
            - hashtags (List[str]): All hashtags found in the post
            - hashtag_count (int): Number of hashtags
            - mentions (List[str]): All @mentions found in the post
            - mention_count (int): Number of mentions
            - urls (List[str]): All URLs found in the post
            - url_count (int): Number of URLs
            - word_count (int): Total number of words
            - character_count (int): Total number of characters
            - character_count_no_spaces (int): Character count excluding spaces
            - average_word_length (float): Average length of words
            - has_emojis (bool): Whether the post contains emojis
            - emoji_count (int): Number of emojis found
            - emojis (List[str]): List of emojis found
            - call_to_action_phrases (List[str]): CTA phrases found
            - has_call_to_action (bool): Whether post contains CTA phrases
            - sentence_count (int): Number of sentences
            - line_count (int): Number of lines
            - unique_words (int): Number of unique words
    
    Example:
        >>> post = "🚀 Join us at Tech Summit! Apply here: https://example.com #TechSummit #AI"
        >>> features = extract_post_features(post)
        >>> print(features['hashtags'])
        ['#TechSummit', '#AI']
    """
    
    if not post_text or not isinstance(post_text, str):
        return _empty_features()
    
    features = {}
    
    # Extract hashtags
    features['hashtags'] = _extract_hashtags(post_text)
    features['hashtag_count'] = len(features['hashtags'])
    
    # Extract mentions
    features['mentions'] = _extract_mentions(post_text)
    features['mention_count'] = len(features['mentions'])
    
    # Extract URLs
    features['urls'] = _extract_urls(post_text)
    features['url_count'] = len(features['urls'])
    
    # Calculate word statistics
    words = _extract_words(post_text)
    features['word_count'] = len(words)
    features['unique_words'] = len(set(word.lower() for word in words))
    
    # Calculate character counts
    features['character_count'] = len(post_text)
    features['character_count_no_spaces'] = len(post_text.replace(' ', '').replace('\n', '').replace('\t', ''))
    
    # Calculate average word length
    if words:
        total_length = sum(len(word) for word in words)
        features['average_word_length'] = round(total_length / len(words), 2)
    else:
        features['average_word_length'] = 0.0
    
    # Extract emojis
    features['emojis'] = _extract_emojis(post_text)
    features['emoji_count'] = len(features['emojis'])
    features['has_emojis'] = features['emoji_count'] > 0
    
    # Extract call-to-action phrases
    features['call_to_action_phrases'] = _extract_cta_phrases(post_text)
    features['has_call_to_action'] = len(features['call_to_action_phrases']) > 0
    
    # Count sentences and lines
    features['sentence_count'] = _count_sentences(post_text)
    features['line_count'] = len(post_text.split('\n'))
    
    # Add sentiment analysis if available
    if SENTIMENT_AVAILABLE:
        sentiment = analyze_sentiment(post_text)
        features['sentiment'] = sentiment
    
    return features


def _extract_hashtags(text: str) -> List[str]:
    r"""
    Extract all hashtags from text using regex pattern #\w+
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of hashtags found (including the # symbol)
    """
    pattern = r'#\w+'
    hashtags = re.findall(pattern, text)
    return hashtags


def _extract_mentions(text: str) -> List[str]:
    r"""
    Extract all @mentions from text using regex pattern @\w+
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of mentions found (including the @ symbol)
    """
    pattern = r'@\w+'
    mentions = re.findall(pattern, text)
    return mentions


def _extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from text.
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of URLs found
    """
    # Pattern to match http://, https://, and www. URLs
    pattern = r'https?://[^\s]+|www\.[^\s]+'
    urls = re.findall(pattern, text)
    return urls


def _extract_words(text: str) -> List[str]:
    """
    Extract words from text, excluding hashtags, mentions, and URLs.
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of words
    """
    # Remove URLs
    text = re.sub(r'https?://[^\s]+|www\.[^\s]+', '', text)
    
    # Remove hashtags and mentions (but keep the words without # and @)
    text = re.sub(r'[#@]', '', text)
    
    # Remove emojis and special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    
    return words


def _extract_emojis(text: str) -> List[str]:
    """
    Extract emojis from text.
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of emojis found
    """
    # Emoji pattern - matches most common emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE
    )
    
    emojis = emoji_pattern.findall(text)
    return emojis


def _extract_cta_phrases(text: str) -> List[str]:
    """
    Extract call-to-action phrases from text.
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of CTA phrases found (lowercase)
    """
    # Common CTA keywords and phrases
    cta_keywords = [
        'join', 'click', 'apply', 'learn', 'discover', 'explore', 'register',
        'sign up', 'signup', 'subscribe', 'download', 'get', 'buy', 'shop',
        'try', 'start', 'begin', 'book', 'reserve', 'order', 'contact',
        'reach out', 'follow', 'share', 'comment', 'like', 'read more',
        'find out', 'check out', 'visit', 'see', 'watch', 'listen',
        'attend', 'participate', 'enroll', 'vote', 'support', 'donate',
        'contribute', 'help', 'volunteer', 'join us', 'get started',
        'learn more', 'read', 'view', 'access', 'claim', 'unlock'
    ]
    
    text_lower = text.lower()
    found_phrases = []
    
    for phrase in cta_keywords:
        # Use word boundaries to match whole words/phrases
        pattern = r'\b' + re.escape(phrase) + r'\b'
        if re.search(pattern, text_lower):
            found_phrases.append(phrase)
    
    return found_phrases


def _count_sentences(text: str) -> int:
    """
    Count the number of sentences in text.
    
    Args:
        text (str): Input text
        
    Returns:
        int: Number of sentences
    """
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)


def _empty_features() -> Dict[str, Any]:
    """
    Return a dictionary with empty/zero values for all features.
    
    Returns:
        Dict[str, Any]: Dictionary with default empty values
    """
    return {
        'hashtags': [],
        'hashtag_count': 0,
        'mentions': [],
        'mention_count': 0,
        'urls': [],
        'url_count': 0,
        'word_count': 0,
        'character_count': 0,
        'character_count_no_spaces': 0,
        'average_word_length': 0.0,
        'has_emojis': False,
        'emoji_count': 0,
        'emojis': [],
        'call_to_action_phrases': [],
        'has_call_to_action': False,
        'sentence_count': 0,
        'line_count': 0,
        'unique_words': 0
    }


def analyze_engagement_signals(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze engagement signals based on extracted features.
    
    Args:
        features (Dict[str, Any]): Dictionary returned by extract_post_features()
        
    Returns:
        Dict[str, Any]: Dictionary containing engagement analysis:
            - engagement_score (float): Overall engagement score (0-100)
            - has_strong_hook (bool): Whether post has strong opening
            - readability_score (str): Easy/Medium/Hard
            - recommendations (List[str]): Suggestions for improvement
    """
    score = 0
    recommendations = []
    
    # Hashtag usage (optimal: 3-5)
    if 3 <= features['hashtag_count'] <= 5:
        score += 20
    elif features['hashtag_count'] > 0:
        score += 10
        if features['hashtag_count'] > 5:
            recommendations.append("Consider reducing hashtags to 3-5 for optimal reach")
    else:
        recommendations.append("Add relevant hashtags to increase discoverability")
    
    # CTA presence
    if features['has_call_to_action']:
        score += 25
    else:
        recommendations.append("Add a clear call-to-action to drive engagement")
    
    # Emoji usage (adds personality)
    if features['has_emojis']:
        score += 15
    else:
        recommendations.append("Consider adding emojis to make the post more engaging")
    
    # URL presence (drives traffic)
    if features['url_count'] > 0:
        score += 10
    
    # Word count (optimal: 50-150 words)
    if 50 <= features['word_count'] <= 150:
        score += 20
    elif features['word_count'] < 50:
        score += 10
        recommendations.append("Post is quite short - consider adding more context")
    else:
        score += 10
        recommendations.append("Post is lengthy - consider breaking into shorter paragraphs")
    
    # Line breaks (readability)
    if features['line_count'] > 3:
        score += 10
    else:
        recommendations.append("Use line breaks to improve readability")
    
    # Has strong hook (emojis or CTA in first 50 characters)
    first_50 = features.get('post_text', '')[:50] if 'post_text' in features else ''
    has_strong_hook = bool(re.search(r'[🎯🚀💡✨🔥⚡️👉📢]', first_50)) or any(
        phrase in first_50.lower() for phrase in ['join', 'discover', 'learn', 'breaking']
    )
    
    # Readability assessment
    avg_word_len = features['average_word_length']
    if avg_word_len < 4.5:
        readability = "Easy"
    elif avg_word_len < 6:
        readability = "Medium"
    else:
        readability = "Hard"
        recommendations.append("Consider using simpler words for better readability")
    
    return {
        'engagement_score': min(score, 100),
        'has_strong_hook': has_strong_hook,
        'readability_score': readability,
        'recommendations': recommendations
    }


# Example usage and testing
if __name__ == "__main__":
    # Sample LinkedIn post text
    sample_post = """🌍 We're proud to announce the launch of our AI for Climate Resilience Program.

AI already powers everything we do at Klarna — and now we're turning that same expertise toward the front lines of climate change. We take pride in our legacy as a climate leader, and we're committed to driving positive change for the future. The AI for Climate Resilience Program will support pioneering projects that harness artificial intelligence to help climate-vulnerable communities adapt and thrive.

This is technology in service of both people and the planet.

This program will support local, practical, and community-owned solutions. From strengthening food security and improving health systems to building coastal resilience in the face of climate change.

What's on offer:
💸 Grants of up to $300,000
🧑‍🎓 Mentorship, training, and a supportive community of practice

We encourage applications from organizations working to reduce vulnerability of local communities to climate-related risks in low- and middle-income countries. We welcome early stage applications as well, from teams that need support in developing technical details further. Whether you're using AI to support smallholder farmers, build early warning systems, or translate complex risk data into community action plans, we want to hear from you!

Find out more about the program and apply here 👉 https://lnkd.in/d3tFWFHJ

#AI #ClimateAction #Sustainability #TechForGood #ClimateResilience @Klarna"""

    print("="*80)
    print("LINKEDIN POST ANALYZER - TEST RESULTS")
    print("="*80)
    print("\nSAMPLE POST:")
    print("-"*80)
    print(sample_post)
    print("-"*80)
    
    # Extract features
    features = extract_post_features(sample_post)
    
    print("\n📊 EXTRACTED FEATURES:")
    print("="*80)
    print(f"Hashtags ({features['hashtag_count']}): {features['hashtags']}")
    print(f"Mentions ({features['mention_count']}): {features['mentions']}")
    print(f"URLs ({features['url_count']}): {features['urls']}")
    print(f"\nWord Count: {features['word_count']}")
    print(f"Character Count: {features['character_count']}")
    print(f"Character Count (no spaces): {features['character_count_no_spaces']}")
    print(f"Average Word Length: {features['average_word_length']}")
    print(f"Unique Words: {features['unique_words']}")
    print(f"\nSentence Count: {features['sentence_count']}")
    print(f"Line Count: {features['line_count']}")
    print(f"\nEmojis ({features['emoji_count']}): {features['emojis']}")
    print(f"Has Emojis: {features['has_emojis']}")
    print(f"\nCall-to-Action Phrases: {features['call_to_action_phrases']}")
    print(f"Has CTA: {features['has_call_to_action']}")
    
    # Analyze engagement signals
    engagement = analyze_engagement_signals(features)
    
    print("\n🎯 ENGAGEMENT ANALYSIS:")
    print("="*80)
    print(f"Engagement Score: {engagement['engagement_score']}/100")
    print(f"Has Strong Hook: {engagement['has_strong_hook']}")
    print(f"Readability: {engagement['readability_score']}")
    
    if engagement['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(engagement['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*80)
    print("✅ Test completed successfully!")
    print("="*80)
