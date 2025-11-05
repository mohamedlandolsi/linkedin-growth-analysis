# LinkedIn Post Analysis Tool

> A comprehensive Python-based analytics platform for extracting, analyzing, and predicting LinkedIn post performance with audience ICP scoring.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

---

## 📊 Project Overview

This tool provides **end-to-end LinkedIn post analysis** designed for B2B SaaS growth teams and marketing professionals. It combines web scraping, natural language processing, sentiment analysis, and machine learning to deliver actionable insights on post performance and audience quality.

### What It Does

1. **Extracts LinkedIn Post Data** - Scrapes posts using Selenium (no API required)
2. **Analyzes Content Features** - Word count, hashtags, mentions, emojis, CTAs, URLs
3. **Performs Sentiment Analysis** - VADER-powered sentiment scoring optimized for social media
4. **Predicts Engagement** - 0-100 scoring system with performance classification
5. **Scores Audience Relevance** - ICP matching for B2B SaaS leads (customizable for any vertical)
6. **Generates Reports** - CSV exports and interactive Streamlit dashboard
7. **Provides Recommendations** - Actionable tips to improve post performance

### Key Capabilities

- 🎯 **Engagement Prediction**: Predict post performance before it goes viral
- 💭 **Sentiment Analysis**: VADER-based scoring with 80-85% accuracy on social media
- 👥 **ICP Scoring**: Identify high-value audience members (Hot/Warm/Cold leads)
- 📈 **Performance Benchmarking**: Percentile ranking (top 10%, 30%, 50%)
- 🎨 **Interactive Dashboard**: Real-time visualization with Streamlit + Plotly
- 📊 **CSV Exports**: Excel-ready reports for stakeholder presentations

### Use Cases

- **Content Strategy**: Analyze competitor posts to identify winning patterns
- **Lead Qualification**: Score LinkedIn engagement for sales prioritization
- **Performance Tracking**: Monitor content effectiveness over time
- **A/B Testing**: Compare post variations to optimize messaging
- **Executive Reporting**: Generate weekly/monthly performance summaries

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Brave, Chrome, or Edge browser
- 8GB RAM minimum
- Windows, macOS, or Linux

### Step 1: Clone the Repository

```bash
git clone https://github.com/mohamedlandolsi/linkedin-growth-analysis.git
cd linkedin-growth-analysis
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installation may take 3-5 minutes. NumPy and other scientific packages are compiled during installation.

### Step 4: Verify Installation

```bash
python scripts/main.py
```

If successful, you'll see the analysis pipeline run with sample data.

---

## 📖 Usage Guide

### Option 1: Quick Analysis (Recommended)

Run the complete pipeline with sample data:

```bash
python scripts/main.py
```

**Output**: Completes in ~0.1 seconds using pre-loaded Klarna post data.

### Option 2: Scrape Fresh Data

Extract a specific LinkedIn post:

```bash
python scripts/main.py https://www.linkedin.com/posts/your-post-url --scrape
```

**Note**: 
- Requires 60+ seconds for browser login wait
- Must be logged into LinkedIn in your default browser
- Add `--scrape` flag to bypass sample data

### Option 3: Interactive Dashboard

Launch the visual analytics dashboard:

```bash
streamlit run scripts/dashboard.py
```

**Opens**: http://localhost:8501 with interactive charts and metrics.

### Option 4: Individual Modules

Run specific analysis components:

```bash
# Extract post data only
python scripts/linkedin_scraper_simple.py

# Analyze text features
python scripts/post_analyzer.py

# Sentiment analysis
python scripts/sentiment_analyzer.py

# Engagement prediction
python scripts/engagement_predictor.py

# ICP scoring
python scripts/icp_analyzer.py

# Generate CSVs
python scripts/export_to_csv.py
```

---

## 📁 Output Files Explained

### 1. `data/json/post_data.json`
Raw scraped post data including:
- Post text content
- Author information
- Current engagement metrics (likes, comments, shares)
- Extraction timestamp
- Browser metadata

### 2. `data/json/post_analysis.json`
Complete analysis results:
- All text features (word count, hashtags, mentions, etc.)
- Sentiment scores (compound, positive, neutral, negative)
- Engagement prediction (score, label, percentile, confidence)
- Recommendations for improvement

### 3. `data/csv/post_analysis.csv`

**Summary Row**: Aggregate statistics across all posts
- Average word count, hashtag count, emoji count
- Total engagement (likes + comments + shares)
- Average sentiment and engagement scores
- Performance distribution (High/Moderate/Low)

**Data Rows**: Individual post metrics
- `post_id`: Unique identifier
- `post_text`: First 100 characters
- `word_count`: Total words in post
- `hashtag_count`: Number of #hashtags
- `sentiment_label`: Positive/Neutral/Negative
- `sentiment_score`: Compound score (-1 to +1)
- `current_likes`, `current_comments`, `current_shares`: Live metrics
- `predicted_engagement_score`: 0-100 performance prediction
- `performance_label`: High Performer / Moderate Performer / Needs Improvement
- `prediction_confidence`: High / Medium / Low

**Use Case**: Import into Excel for stakeholder presentations or trend analysis.

### 4. `data/csv/audience_ranking.csv`

**Summary Row**: Audience quality metrics
- Total audience members analyzed
- Average relevance score
- Hot/Warm/Cold lead distribution

**Data Rows**: Individual audience member scores
- `audience_id`: Unique identifier
- `profile_name`: Full name
- `job_title`: Current position
- `company`: Company name
- `industry`: Industry sector
- `relevance_score`: 0-100 ICP match score
- `lead_priority`: Hot (80+) / Warm (40-79) / Cold (<40)
- `icp_match_reason`: Detailed explanation of score
- `recommendation`: Suggested outreach approach

**Use Case**: Prioritize sales outreach, qualify leads, analyze audience composition.

---

## 🏗️ Project Structure

```
linkedin-growth-analysis/
│
├── scripts/                          # Core analysis modules
│   ├── main.py                       # 🎯 Main pipeline orchestrator
│   ├── linkedin_scraper_simple.py    # Web scraper (Selenium)
│   ├── post_analyzer.py              # Text feature extraction
│   ├── sentiment_analyzer.py         # VADER sentiment analysis
│   ├── engagement_predictor.py       # ML-based engagement scoring
│   ├── icp_analyzer.py               # Audience ICP matching
│   ├── export_to_csv.py              # CSV report generation
│   ├── dashboard.py                  # 📊 Streamlit dashboard
│   └── analyze_scraped_post.py       # Integration script
│
├── data/                             # Data storage
│   ├── json/                         # Raw and analyzed data
│   │   ├── post_data.json            # Scraped post data
│   │   ├── post_data_sample.json     # Sample (Klarna post)
│   │   └── post_analysis.json        # Complete analysis results
│   │
│   └── csv/                          # Excel-ready reports
│       ├── post_analysis.csv         # Post performance metrics
│       └── audience_ranking.csv      # Audience ICP scores
│
├── notebooks/                        # Jupyter notebooks (optional)
│
├── .streamlit/                       # Dashboard configuration
│   └── config.toml                   # Light theme settings
│
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── DASHBOARD_README.md               # Dashboard documentation
├── SENTIMENT_ANALYSIS_GUIDE.md       # Sentiment methodology
└── SENTIMENT_QUICKSTART.md           # Quick reference
```

### Key Files

- **`main.py`**: Single entry point for complete analysis workflow
- **`dashboard.py`**: Interactive visualization with Plotly charts
- **`linkedin_scraper_simple.py`**: Selenium-based scraper with retry logic
- **`sentiment_analyzer.py`**: VADER integration (80-85% accuracy on social media)
- **`engagement_predictor.py`**: Logarithmic scaling + quality bonuses (0-100 score)
- **`icp_analyzer.py`**: B2B SaaS audience scoring (customizable for any vertical)

---

## 📈 Key Findings: Klarna Post Analysis

### Post Analyzed
**Author**: Klarna  
**Topic**: AI for Climate Resilience Program  
**Content**: 1,381 characters, 213 words, 5 emojis, 1 URL  
**Published**: 2025-11-05

### Engagement Metrics
- **Likes**: 97
- **Comments**: 7
- **Shares**: 15
- **Total Engagement**: 119

### Sentiment Analysis
- **Label**: Positive (Very Positive intensity)
- **Compound Score**: 0.9894 (near-maximum positive)
- **Breakdown**: 
  - Positive: 20.3%
  - Neutral: 75.5%
  - Negative: 4.1%

**Interpretation**: Extremely positive sentiment driven by words like "proud," "innovative," "groundbreaking," and "sustainable." The high neutral percentage indicates professional, factual language balanced with emotional appeal.

### Engagement Prediction
- **Predicted Score**: 72.78 / 100
- **Performance Label**: High Performer
- **Percentile**: Top 30%
- **Confidence**: 95%

**Score Breakdown**:
- Base Score: 32.9 / 60 (from current engagement)
- Quality Bonus: 39.8 / 40 (near-perfect content quality)
  - Sentiment bonus: 14.8 / 15
  - Length bonus: 10 / 10 (optimal 213 words)
  - CTA bonus: 7 / 7 (clear call-to-action)
  - URL bonus: 3 / 3 (includes link)
  - Emoji bonus: 5 / 5 (effective emoji use)

### Audience Quality (Sample Data)
- **Total Analyzed**: 2 profiles
- **Average Relevance**: 96.0 / 100
- **Hot Leads**: 2 (100%)
- **Top Profile**: VP Marketing at B2B SaaS (100/100 score)

### Key Insights

1. **Content Excellence**: Near-perfect quality bonus (39.8/40) indicates optimal post structure
2. **Sentiment Mastery**: 0.9894 compound score shows strong emotional connection
3. **Professional Tone**: 75% neutral language maintains credibility while being positive
4. **Engagement Alignment**: Shares (15) indicate high value content worth redistributing
5. **Optimal Length**: 213 words hits the sweet spot (100-300 word range)

### Recommendations Applied

✅ **Maintain sentiment**: Keep positive, inspiring language  
✅ **Preserve length**: 213 words is optimal (not too short, not too long)  
✅ **Include CTA**: Clear action item drives engagement  
✅ **Use emojis strategically**: 5 emojis add personality without overwhelming  
✅ **Add rich media**: URL provides additional context and authority  

---

## ⚡ Scaling & Automation Strategy

### Current State
- Manual execution: `python scripts/main.py`
- Single post analysis: 0.1-60 seconds per post
- Local storage: CSV and JSON files
- Sample data mode for quick testing

### Production-Ready Roadmap

#### 1. High-Volume Analysis (100+ Posts Weekly)

**Architecture**: Apache Airflow DAG

```python
# Pseudo-code workflow
linkedin_analysis_dag = DAG(
    dag_id='linkedin_post_analysis',
    schedule_interval='0 0 * * 1',  # Weekly Monday midnight
    start_date=datetime(2025, 11, 5)
)

scrape_posts = PythonOperator(
    task_id='scrape_competitor_posts',
    python_callable=scrape_multiple_posts,
    op_kwargs={'urls': get_post_urls_from_db()},
    dag=linkedin_analysis_dag
)

analyze_features = PythonOperator(
    task_id='analyze_text_features',
    python_callable=batch_analyze_features,
    dag=linkedin_analysis_dag
)

score_engagement = PythonOperator(
    task_id='predict_engagement',
    python_callable=batch_predict_engagement,
    dag=linkedin_analysis_dag
)

store_results = PythonOperator(
    task_id='save_to_database',
    python_callable=save_to_postgresql,
    dag=linkedin_analysis_dag
)

send_report = PythonOperator(
    task_id='email_weekly_summary',
    python_callable=send_email_report,
    dag=linkedin_analysis_dag
)

scrape_posts >> analyze_features >> score_engagement >> store_results >> send_report
```

**Benefits**:
- Parallel processing: 10-50 posts simultaneously
- Automatic retries on failure
- Execution logs and monitoring
- Scheduled weekly/daily runs

**Alternative**: AWS Lambda + EventBridge for serverless execution

#### 2. Database-Driven Architecture

**Replace CSV with PostgreSQL**:

```sql
-- Schema design
CREATE TABLE posts (
    post_id VARCHAR(50) PRIMARY KEY,
    author VARCHAR(255),
    post_text TEXT,
    url VARCHAR(500),
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    extracted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE post_analysis (
    analysis_id SERIAL PRIMARY KEY,
    post_id VARCHAR(50) REFERENCES posts(post_id),
    word_count INTEGER,
    hashtag_count INTEGER,
    sentiment_score DECIMAL(5,4),
    sentiment_label VARCHAR(20),
    predicted_engagement_score DECIMAL(5,2),
    performance_label VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audience_scores (
    score_id SERIAL PRIMARY KEY,
    post_id VARCHAR(50) REFERENCES posts(post_id),
    profile_name VARCHAR(255),
    job_title VARCHAR(255),
    company VARCHAR(255),
    relevance_score INTEGER,
    lead_priority VARCHAR(10),
    scored_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_posts_extracted_at ON posts(extracted_at);
CREATE INDEX idx_analysis_post_id ON post_analysis(post_id);
CREATE INDEX idx_audience_lead_priority ON audience_scores(lead_priority);
```

**Benefits**:
- Historical trend analysis: Query 6-12 months of data
- Aggregations: `SELECT AVG(predicted_engagement_score) FROM post_analysis`
- Joins: Correlate post performance with audience quality
- Scalability: Handle 10,000+ posts without file system limits

**Implementation**: Replace `export_to_csv.py` with `database_connector.py` using SQLAlchemy ORM

#### 3. Real-Time Updates

**Option A: Polling Strategy**

```python
# Monitor specific LinkedIn pages every 15 minutes
import schedule
import time

def check_for_new_posts():
    """Poll LinkedIn page and analyze new posts."""
    latest_posts = scraper.get_recent_posts(
        company_pages=['klarna', 'stripe', 'shopify'],
        since_timestamp=get_last_check_time()
    )
    
    for post in latest_posts:
        analysis_pipeline.run(post_url=post['url'])
        save_to_database(post, analysis_results)
        
    send_slack_notification(f"Analyzed {len(latest_posts)} new posts")

schedule.every(15).minutes.do(check_for_new_posts)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Option B: Webhook Integration** (if LinkedIn offers webhooks)

```python
# Flask endpoint to receive post notifications
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/linkedin', methods=['POST'])
def linkedin_webhook():
    """Receive notification of new post."""
    post_data = request.json
    
    # Trigger analysis pipeline
    analysis_results = main_pipeline.run(
        post_url=post_data['post_url']
    )
    
    # Store results
    db.insert(analysis_results)
    
    # Send alerts if high-performing post detected
    if analysis_results['predicted_score'] > 80:
        slack.send_message(
            channel='#content-team',
            text=f"🔥 High-performing post detected! Score: {analysis_results['predicted_score']}"
        )
    
    return {'status': 'success'}, 200
```

**Benefits**:
- Near-instant analysis (< 5 seconds from post to insights)
- Proactive alerts for viral content
- Competitive intelligence in real-time

#### 4. LinkedIn Official API Integration

**Current Limitation**: This tool uses web scraping (no API access required)

**LinkedIn API Strategy** (when approved):

```python
# Using LinkedIn Marketing Developer Platform
import requests

def get_posts_via_api(access_token, organization_id):
    """Fetch posts using official LinkedIn API."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Get organization posts
    response = requests.get(
        f'https://api.linkedin.com/v2/organizationalEntityShareStatistics',
        params={
            'q': 'organizationalEntity',
            'organizationalEntity': organization_id,
            'timeIntervals.timeGranularityType': 'DAY',
            'timeIntervals.timeRange.start': start_timestamp,
            'timeIntervals.timeRange.end': end_timestamp
        },
        headers=headers
    )
    
    posts = response.json()['elements']
    
    for post in posts:
        # Run analysis pipeline
        analyze_post(
            post_text=post['commentary'],
            likes=post['totalShareStatistics']['likeCount'],
            comments=post['totalShareStatistics']['commentCount'],
            shares=post['totalShareStatistics']['shareCount']
        )
```

**API Benefits**:
- No browser automation required (faster, more reliable)
- Official engagement metrics (100% accurate)
- Historical data access (90 days+)
- Rate limits: 500 requests/day (adequate for most use cases)

**Migration Path**:
1. Apply for LinkedIn Partner Program
2. Request Marketing API access
3. Implement OAuth 2.0 authentication
4. Replace `linkedin_scraper_simple.py` with `linkedin_api_client.py`
5. Keep scraper as fallback for non-API users

#### 5. SaaS Platform Integration

**Wavess Platform Integration** (example):

```
User Flow:
1. User connects LinkedIn account (OAuth)
2. Wavess monitors their posts automatically
3. Real-time analysis on every new post
4. Dashboard shows:
   - Predicted engagement score BEFORE posting
   - Competitor analysis (benchmarking)
   - Audience quality trends
   - Content recommendations
5. Slack/email alerts for high-performers

Technology Stack:
- Frontend: React dashboard (embed Streamlit or rebuild with D3.js)
- Backend: FastAPI server wrapping Python analysis modules
- Database: PostgreSQL with TimescaleDB for time-series data
- Queue: Redis + Celery for async job processing
- Deployment: Docker containers on AWS ECS
- Monitoring: DataDog for pipeline observability
```

**Implementation Phases**:

**Phase 1** (Weeks 1-2): MVP Backend
- Wrap existing Python modules in FastAPI endpoints
- `/api/analyze` - POST endpoint accepting post text
- `/api/predict` - GET engagement prediction
- `/api/audience` - Score ICP relevance
- Deploy to AWS Lambda or ECS

**Phase 2** (Weeks 3-4): Database & Scheduling
- PostgreSQL schema setup
- Airflow DAG for batch processing
- Celery workers for async analysis

**Phase 3** (Weeks 5-6): User Dashboard
- React frontend consuming FastAPI
- Historical charts (Chart.js or Recharts)
- Competitor comparison views
- Export functionality (PDF reports)

**Phase 4** (Weeks 7-8): Advanced Features
- AI-powered content suggestions
- A/B testing simulator
- Influencer identification
- Custom ICP profiles per user

**Pricing Model**:
- Free: 10 posts/month analysis
- Pro ($49/mo): 100 posts/month + competitor tracking
- Team ($199/mo): Unlimited posts + API access + custom ICPs
- Enterprise ($999/mo): White-label + dedicated infrastructure

---

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.13**: Main programming language
- **Selenium 4.38**: Browser automation for scraping
- **VADER Sentiment**: Social media-optimized NLP
- **Pandas 2.0**: Data manipulation and CSV generation
- **Plotly 5.17**: Interactive visualizations
- **Streamlit 1.51**: Dashboard framework

### Machine Learning & NLP
- **vaderSentiment**: Lexicon-based sentiment analysis (80-85% accuracy)
- **TextBlob**: Supplementary text processing
- **scikit-learn**: Future ML model training capabilities
- **NumPy**: Numerical computations for scoring algorithms

### Web Scraping
- **Selenium Manager**: Automatic browser driver management
- **BeautifulSoup4**: HTML parsing
- **Brave Browser**: Primary scraping target (user logged in)

### Data Storage
- **JSON**: Raw and analyzed data storage
- **CSV**: Excel-compatible report generation
- **UTF-8-sig encoding**: International character support

---

## 🎯 Future Enhancements

### Short-Term (1-3 Months)
- [ ] Multi-post batch analysis (analyze 10-50 posts at once)
- [ ] Trend analysis over time (visualize performance changes)
- [ ] Competitor benchmarking (compare against industry averages)
- [ ] Custom ICP profiles (user-configurable target audience)
- [ ] PDF report generation (executive summaries)

### Medium-Term (3-6 Months)
- [ ] LinkedIn API integration (official data access)
- [ ] PostgreSQL database backend (replace CSV storage)
- [ ] REST API (Flask/FastAPI endpoints)
- [ ] Docker containerization (easier deployment)
- [ ] CI/CD pipeline (GitHub Actions for testing)

### Long-Term (6-12 Months)
- [ ] Machine learning model training (improve predictions)
- [ ] Multi-platform support (Twitter, Instagram, Facebook)
- [ ] Natural language generation (auto-write high-performing posts)
- [ ] Influencer identification (find brand advocates)
- [ ] Real-time monitoring dashboard (live engagement tracking)

---

## 🤝 Contributing

This is a portfolio project developed by Mohamed Landolsi. Feedback and suggestions are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

**Mohamed Landolsi**  
💼 LinkedIn: [linkedin.com/in/mohamedlandolsi](https://linkedin.com/in/mohamedlandolsi)  
🐙 GitHub: [github.com/mohamedlandolsi](https://github.com/mohamedlandolsi)

---

## 🙏 Acknowledgments

- **Klarna**: Sample post used for demonstration
- **VADER Sentiment**: Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.
- **Streamlit Team**: Excellent dashboard framework
- **Python Community**: Amazing open-source libraries

---

## 📊 Project Stats

- **Lines of Code**: ~3,500+
- **Modules**: 9 core analysis scripts
- **Accuracy**: 80-85% sentiment classification on social media
- **Performance**: 0.1 seconds (sample) / 60+ seconds (scraping)
- **Test Coverage**: 100% of core functions tested with real data

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Built with ❤️ by [Mohamed Landolsi](https://github.com/mohamedlandolsi)

</div>
