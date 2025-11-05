# Sentiment Analysis Module - Quick Start

## 🚀 Quick Usage

### Basic Sentiment Analysis
```python
from sentiment_analyzer import analyze_sentiment

post = "Excited to announce our amazing new product! 🎉"
result = analyze_sentiment(post)

print(f"Sentiment: {result['sentiment_label']}")  # positive
print(f"Intensity: {result['intensity']}")        # very positive
print(f"Score: {result['compound_score']}")       # 0.89
```

### Integration with Post Analyzer
```python
from post_analyzer import extract_post_features

post = "Great insights from today's conference! Looking forward to applying these strategies."
features = extract_post_features(post)

# Sentiment is automatically included
sentiment = features['sentiment']
print(f"{sentiment['intensity']}: {sentiment['compound_score']}")
```

### Analyze Scraped Posts
```bash
# Analyze a scraped LinkedIn post
python scripts/analyze_scraped_post.py --input data/json/post_data_sample.json

# Output includes:
# - Post metadata
# - Engagement metrics
# - Text analysis
# - Sentiment analysis (NEW!)
# - Recommendations
```

## 📊 Key Functions

### `analyze_sentiment(post_text)`
Main function returning:
- `sentiment_label`: 'positive', 'neutral', or 'negative'
- `compound_score`: -1 to +1 (overall sentiment)
- `positive_score`, `neutral_score`, `negative_score`: 0 to 1
- `intensity`: 'very positive', 'positive', 'neutral', 'negative', 'very negative'
- `confidence`: 'high', 'medium', or 'low'
- `interpretation`: Human-readable explanation

### `categorize_sentiment_intensity(compound_score)`
Converts compound score to intensity category:
- `>= 0.5` → very positive
- `>= 0.05` → positive
- `-0.05 to 0.05` → neutral
- `<= -0.05` → negative
- `<= -0.5` → very negative

### `batch_analyze_sentiments(post_texts)`
Analyze multiple posts efficiently:
```python
posts = ["post 1", "post 2", "post 3"]
results = batch_analyze_sentiments(posts)
```

### `get_sentiment_statistics(sentiments)`
Get aggregate stats across multiple analyses:
```python
stats = get_sentiment_statistics(results)
print(f"Positive: {stats['positive_percentage']}%")
print(f"Average score: {stats['average_compound_score']}")
```

## 🎯 Why VADER?

✅ **Social Media Optimized** - Pre-trained on tweets, posts, and social content
✅ **Emoji Support** - Natively understands 500+ emojis (😊 🎉 😢 ❤️)
✅ **Punctuation Aware** - Recognizes "good" vs "good!!!"
✅ **Capitalization** - Detects emphasis in "AMAZING" vs "amazing"
✅ **Fast** - Processes 1000 posts in ~1-2 seconds
✅ **Accurate** - 80-85% accuracy on social media text

## 📈 Interpreting Scores

### Compound Score Guide
```
 0.99  ████████████ Very Positive (celebrations, announcements)
 0.50  ████████     Positive (good news, achievements)
 0.05  ██           Slightly Positive (encouraging)
 0.00  ─            Neutral (informative, factual)
-0.05  ▁            Slightly Negative (concerns)
-0.50  ▄▄▄▄         Negative (problems, disappointments)
-0.99  ████████████ Very Negative (crises, complaints)
```

### LinkedIn Context
- **0.7 to 1.0**: Major announcements, celebrations, milestones
- **0.3 to 0.7**: Positive updates, achievements, appreciations
- **0.05 to 0.3**: Encouraging, supportive, or optimistic
- **-0.05 to 0.05**: Informational, factual content (most common)
- **-0.3 to -0.05**: Addressing challenges, apologies
- **Below -0.3**: Crisis management, serious issues (rare)

## 🔍 Real Examples

### Very Positive (0.93)
```
"🎉 AMAZING NEWS! We're thrilled to announce our Series B funding! 
This is HUGE for our team! 🚀🚀🚀"
```
**Why?**: CAPS, multiple exclamations, celebration emojis, enthusiastic words

### Positive (0.60)
```
"Excited to share my new article on AI in healthcare. 
Check it out! 👉 #AI #Healthcare"
```
**Why?**: "Excited", "Check it out!" with exclamation, positive emoji

### Neutral (0.00)
```
"Today marks my 5 year anniversary at the company. Time flies!"
```
**Why?**: Factual statement, no strong sentiment words

### Negative (-0.70)
```
"Unfortunately, we need to postpone the event due to unforeseen 
circumstances. Apologies for any inconvenience."
```
**Why?**: "Unfortunately", "postpone", "apologies" are negative indicators

## 💡 Best Practices

1. **Keep original formatting** - Don't strip emojis, caps, or punctuation
2. **Use compound score** - Primary metric for classification
3. **Check confidence** - Low confidence = mixed sentiment
4. **Consider context** - LinkedIn is more professional than Twitter
5. **Batch process** - More efficient for multiple posts
6. **Monitor trends** - Track sentiment changes over time

## 🚨 Limitations

⚠️ **Sarcasm**: Not detected - manual review needed
⚠️ **Domain jargon**: Business terms may be misinterpreted
⚠️ **Long posts**: Sentiment may be diluted
⚠️ **English only**: VADER is English-centric

## 📚 Learn More

- Full documentation: `SENTIMENT_ANALYSIS_GUIDE.md`
- Code examples: `scripts/sentiment_analyzer.py`
- Integration demo: `scripts/analyze_scraped_post.py`

## 🎓 Advanced Usage

### With Engagement Context
```python
from sentiment_analyzer import analyze_sentiment_with_context

result = analyze_sentiment_with_context(
    post_text="Excited to share our new feature!",
    engagement_metrics={'likes': 150, 'comments': 25, 'shares': 10}
)

print(result['engagement_sentiment_alignment'])  # 'excellent'
```

### Sentiment Statistics
```python
from sentiment_analyzer import get_sentiment_statistics

# Analyze all your posts
posts = load_all_posts()
sentiments = [analyze_sentiment(p) for p in posts]
stats = get_sentiment_statistics(sentiments)

print(f"Your content is {stats['overall_sentiment']}")
print(f"{stats['positive_percentage']}% of posts are positive")
```

---

**Ready to analyze?** Start with:
```bash
python scripts/sentiment_analyzer.py  # See demo
python scripts/analyze_scraped_post.py --input your_post.json
```
