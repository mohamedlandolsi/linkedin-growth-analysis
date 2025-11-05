"""
LinkedIn Post Analysis Dashboard

A lightweight Streamlit dashboard for visualizing LinkedIn post performance,
sentiment analysis, engagement predictions, and audience ICP scoring.

Run with: streamlit run scripts/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="LinkedIn Post Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
        background-color: #f5f7fa;
    }
    
    /* Metric boxes - make them stand out */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    /* Post text box - clear white background */
    .post-text {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #0073b1;
        margin: 15px 0;
        font-size: 16px;
        line-height: 1.8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #1a1a1a;
    }
    
    /* Section headers - LinkedIn blue */
    .section-header {
        color: #0073b1;
        font-weight: 700;
        font-size: 28px;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 3px solid #0073b1;
        padding-bottom: 10px;
    }
    
    /* Card backgrounds */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Make dividers more visible */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #0073b1 0%, #00a0dc 100%);
        margin: 30px 0;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 2px solid #0073b1;
        border-radius: 8px;
    }
    
    /* Header styling */
    h1 {
        color: #0073b1 !important;
        font-weight: 700 !important;
    }
    
    h2 {
        color: #0073b1 !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #00a0dc !important;
        font-weight: 600 !important;
    }
    
    /* Make markdown text more visible */
    .stMarkdown {
        color: #1a1a1a;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_post_data():
    """Load post data from JSON file."""
    try:
        with open('data/json/post_data_sample.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Post data file not found. Please run the scraper first.")
        return None


@st.cache_data
def load_analysis_data():
    """Load complete analysis results from JSON file."""
    try:
        with open('data/json/post_analysis.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("Analysis file not found. Using post data only.")
        return None


@st.cache_data
def load_audience_data():
    """Load audience ranking from CSV file."""
    try:
        df = pd.read_csv('data/csv/audience_ranking.csv', encoding='utf-8-sig')
        # Remove summary row
        df = df[df['audience_id'] != '=== SUMMARY STATISTICS ===']
        
        # Convert numeric columns to proper types
        numeric_cols = ['relevance_score', 'company_size', 'linkedin_followers',
                       'role_score', 'seniority_score', 'industry_score', 
                       'company_size_score', 'bonus_score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.info("Audience ranking CSV not found. Audience section will be hidden.")
        return None


def create_sentiment_gauge(sentiment_score):
    """Create a gauge chart for sentiment score."""
    # Normalize sentiment score from -1 to 1 range to 0 to 100
    normalized_score = (sentiment_score + 1) * 50
    
    # Determine color based on sentiment
    if sentiment_score >= 0.5:
        color = "#28a745"  # Strong green
        label = "Very Positive"
    elif sentiment_score >= 0.05:
        color = "#7cb342"  # Light green
        label = "Positive"
    elif sentiment_score >= -0.05:
        color = "#9e9e9e"  # Gray
        label = "Neutral"
    elif sentiment_score >= -0.5:
        color = "#ff9800"  # Orange
        label = "Negative"
    else:
        color = "#dc3545"  # Red
        label = "Very Negative"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=normalized_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<b>{label}</b><br><span style='font-size:0.8em; color:#1a1a1a;'>Compound Score: {sentiment_score:.3f}</span>",
            'font': {'size': 18, 'color': '#0073b1'}
        },
        delta={'reference': 50, 'increasing': {'color': '#28a745'}, 'decreasing': {'color': '#dc3545'}},
        number={'font': {'size': 40, 'color': color, 'weight': 'bold'}},
        gauge={
            'axis': {
                'range': [None, 100],
                'tickwidth': 2,
                'tickcolor': "#0073b1",
                'tickfont': {'size': 12, 'color': '#1a1a1a'}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#f8f9fa",
            'borderwidth': 3,
            'bordercolor': "#0073b1",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(220, 53, 69, 0.3)'},   # Red zone
                {'range': [25, 45], 'color': 'rgba(255, 152, 0, 0.3)'},  # Orange zone
                {'range': [45, 55], 'color': 'rgba(158, 158, 158, 0.3)'}, # Gray zone
                {'range': [55, 75], 'color': 'rgba(124, 179, 66, 0.3)'},  # Light green
                {'range': [75, 100], 'color': 'rgba(40, 167, 69, 0.3)'}   # Strong green
            ],
            'threshold': {
                'line': {'color': "#dc3545", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={'color': "#1a1a1a", 'family': "Arial"},
        height=300,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig


def create_sentiment_breakdown_chart(pos, neu, neg):
    """Create a bar chart for sentiment component breakdown."""
    fig = go.Figure(data=[
        go.Bar(
            x=['Positive', 'Neutral', 'Negative'],
            y=[pos * 100, neu * 100, neg * 100],
            marker_color=['#28a745', '#6c757d', '#dc3545'],
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=2,
            text=[f'{pos*100:.1f}%', f'{neu*100:.1f}%', f'{neg*100:.1f}%'],
            textposition='outside',
            textfont=dict(size=14, color='#1a1a1a', family='Arial', weight='bold')
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Sentiment Component Breakdown",
            'font': {'size': 18, 'color': '#0073b1', 'family': 'Arial', 'weight': 'bold'}
        },
        yaxis_title="Percentage",
        xaxis_title="",
        showlegend=False,
        height=350,
        yaxis={'range': [0, max(pos, neu, neg) * 110], 'gridcolor': '#e0e0e0'},
        xaxis={'tickfont': {'size': 12, 'color': '#1a1a1a'}},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font={'color': '#1a1a1a'}
    )
    
    return fig


def create_engagement_comparison_chart(current, predicted, max_score=100):
    """Create a bar chart comparing current vs predicted engagement."""
    fig = go.Figure(data=[
        go.Bar(
            x=['Current Engagement', 'Predicted Score'],
            y=[current, predicted],
            marker_color=['#0073b1', '#00a0dc'],
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=2,
            text=[f'{current:.1f}', f'{predicted:.1f}/100'],
            textposition='outside',
            textfont=dict(size=14, color='#1a1a1a', family='Arial', weight='bold')
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Engagement: Current vs Predicted Performance",
            'font': {'size': 18, 'color': '#0073b1', 'family': 'Arial', 'weight': 'bold'}
        },
        yaxis_title="Score",
        xaxis_title="",
        showlegend=False,
        height=350,
        yaxis={'range': [0, max_score * 1.1], 'gridcolor': '#e0e0e0'},
        xaxis={'tickfont': {'size': 12, 'color': '#1a1a1a'}},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font={'color': '#1a1a1a'}
    )
    
    return fig


def create_score_breakdown_chart(base_score, quality_bonus, max_base=60, max_bonus=40):
    """Create a stacked bar chart showing score breakdown."""
    fig = go.Figure(data=[
        go.Bar(
            name='Base Score',
            x=['Engagement Score'],
            y=[base_score],
            marker_color='#0073b1',
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=2,
            text=f'{base_score:.1f}/{max_base}',
            textposition='inside',
            textfont=dict(size=14, color='#ffffff', family='Arial', weight='bold')
        ),
        go.Bar(
            name='Quality Bonus',
            x=['Engagement Score'],
            y=[quality_bonus],
            marker_color='#00a0dc',
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=2,
            text=f'{quality_bonus:.1f}/{max_bonus}',
            textposition='inside',
            textfont=dict(size=14, color='#ffffff', family='Arial', weight='bold')
        )
    ])
    
    fig.update_layout(
        barmode='stack',
        title={
            'text': "Score Breakdown: Base + Quality Bonus",
            'font': {'size': 18, 'color': '#0073b1', 'family': 'Arial', 'weight': 'bold'}
        },
        yaxis_title="Points",
        xaxis_title="",
        showlegend=True,
        height=300,
        yaxis={'range': [0, 100], 'gridcolor': '#e0e0e0'},
        xaxis={'tickfont': {'size': 12, 'color': '#1a1a1a'}},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font={'color': '#1a1a1a'},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#0073b1',
            borderwidth=2
        )
    )
    
    return fig


def create_audience_relevance_chart(df_top_10):
    """Create a horizontal bar chart for top 10 audience members."""
    
    # Create color array based on scores
    colors = df_top_10['relevance_score'].apply(
        lambda x: '#28a745' if x >= 80 else '#ffc107' if x >= 40 else '#dc3545'
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_top_10['relevance_score'],
            y=df_top_10['profile_name'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.3)', width=2)
            ),
            text=df_top_10['relevance_score'].apply(lambda x: f'{x:.0f}'),
            textposition='outside',
            textfont=dict(size=14, color='#1a1a1a', family='Arial', weight='bold'),
            hovertemplate='<b>%{y}</b><br>' +
                         'Score: %{x:.0f}/100<br>' +
                         '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Top 10 Most Relevant Audience Members",
            'font': {'size': 18, 'color': '#0073b1', 'family': 'Arial', 'weight': 'bold'}
        },
        xaxis_title="Relevance Score",
        yaxis_title="",
        showlegend=False,
        height=400,
        xaxis={'range': [0, 105], 'gridcolor': '#e0e0e0'},
        yaxis={'autorange': 'reversed', 'tickfont': {'size': 12, 'color': '#1a1a1a'}},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font={'color': '#1a1a1a'}
    )
    
    return fig


def display_header():
    """Display dashboard header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 LinkedIn Post Analysis Dashboard")
        st.markdown("**Comprehensive analysis of post performance, sentiment, and audience relevance**")
    
    with col2:
        st.markdown(f"<div style='text-align: right; padding-top: 20px;'>"
                   f"<small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>",
                   unsafe_allow_html=True)


def display_post_details(post_data, analysis_data):
    """Display post details section."""
    st.markdown("<h2 class='section-header'>📝 Post Details</h2>", unsafe_allow_html=True)
    
    # Post text
    post_text = post_data.get('post_text', 'No text available')
    st.markdown(f"<div class='post-text'>{post_text}</div>", unsafe_allow_html=True)
    
    # Author and metadata
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        author = post_data.get('author', 'Unknown')
        if '\n' in author:
            author = author.split('\n')[0]  # Get first line only
        st.metric("👤 Author", author)
    
    with col2:
        extracted_at = post_data.get('extracted_at', 'Unknown')
        if extracted_at and extracted_at != 'Unknown':
            extracted_date = extracted_at.split('T')[0]
            st.metric("📅 Extracted", extracted_date)
        else:
            st.metric("📅 Extracted", "Unknown")
    
    with col3:
        browser = post_data.get('browser_used', 'Unknown')
        st.metric("🌐 Browser", browser)
    
    with col4:
        status = post_data.get('extraction_status', 'unknown')
        status_icon = "✅" if status == "success" else "⚠️"
        st.metric("📊 Status", f"{status_icon} {status.title()}")
    
    # Engagement metrics
    st.markdown("<h3 style='margin-top: 20px;'>💬 Current Engagement</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    likes = post_data.get('likes') or 0
    comments = post_data.get('comments') or 0
    shares = post_data.get('shares') or 0
    total = likes + comments + shares
    
    with col1:
        st.metric("👍 Likes", f"{likes:,}")
    
    with col2:
        st.metric("💬 Comments", f"{comments:,}")
    
    with col3:
        st.metric("🔄 Shares", f"{shares:,}")
    
    with col4:
        st.metric("📈 Total Engagement", f"{total:,}")


def display_post_features(analysis_data):
    """Display post features section."""
    st.markdown("<h2 class='section-header'>🔍 Post Features</h2>", unsafe_allow_html=True)
    
    features = analysis_data.get('text_features', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        word_count = features.get('word_count', 0)
        st.metric("📝 Word Count", f"{word_count:,}")
    
    with col2:
        char_count = features.get('character_count', 0)
        st.metric("🔤 Characters", f"{char_count:,}")
    
    with col3:
        hashtag_count = features.get('hashtag_count', 0)
        st.metric("#️⃣ Hashtags", hashtag_count)
    
    with col4:
        emoji_count = features.get('emoji_count', 0)
        st.metric("😊 Emojis", emoji_count)
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mention_count = features.get('mention_count', 0)
        st.metric("@ Mentions", mention_count)
    
    with col2:
        url_count = features.get('url_count', 0)
        st.metric("🔗 URLs", url_count)
    
    with col3:
        has_cta = features.get('has_call_to_action', False)
        cta_icon = "✅" if has_cta else "❌"
        st.metric("📢 Has CTA", f"{cta_icon} {'Yes' if has_cta else 'No'}")
    
    with col4:
        question_count = features.get('question_count', 0)
        st.metric("❓ Questions", question_count)
    
    # Show lists if available
    if features.get('hashtags') and len(features['hashtags']) > 0:
        st.markdown("**Hashtags:**")
        st.write(", ".join(features['hashtags']))
    
    if features.get('mentions') and len(features['mentions']) > 0:
        st.markdown("**Mentions:**")
        st.write(", ".join(features['mentions']))
    
    if features.get('urls') and len(features['urls']) > 0:
        st.markdown("**URLs:**")
        for url in features['urls']:
            st.write(f"- {url}")


def display_sentiment_analysis(analysis_data):
    """Display sentiment analysis section."""
    st.markdown("<h2 class='section-header'>💭 Sentiment Analysis</h2>", unsafe_allow_html=True)
    
    features = analysis_data.get('text_features', {})
    sentiment = features.get('sentiment', {})
    
    if not sentiment:
        st.warning("Sentiment analysis data not available.")
        return
    
    # Top row metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_label = sentiment.get('sentiment_label', 'N/A').title()
        intensity = sentiment.get('intensity', 'N/A')
        st.metric("📊 Sentiment", f"{sentiment_label} ({intensity})")
    
    with col2:
        compound_score = sentiment.get('compound_score', 0)
        st.metric("🎯 Compound Score", f"{compound_score:.3f}")
    
    with col3:
        confidence = sentiment.get('confidence_level', 'N/A').title()
        st.metric("✅ Confidence", confidence)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge chart
        compound_score = sentiment.get('compound_score', 0)
        fig_gauge = create_sentiment_gauge(compound_score)
        st.plotly_chart(fig_gauge, width='stretch')
    
    with col2:
        # Breakdown bar chart
        pos = sentiment.get('positive_score', 0)
        neu = sentiment.get('neutral_score', 0)
        neg = sentiment.get('negative_score', 0)
        fig_breakdown = create_sentiment_breakdown_chart(pos, neu, neg)
        st.plotly_chart(fig_breakdown, width='stretch')


def display_engagement_prediction(analysis_data, post_data):
    """Display engagement prediction section."""
    st.markdown("<h2 class='section-header'>🎯 Engagement Prediction</h2>", unsafe_allow_html=True)
    
    prediction = analysis_data.get('engagement_prediction', {})
    
    if not prediction:
        st.warning("Engagement prediction data not available.")
        return
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        eng_score = prediction.get('engagement_score', 0)
        st.metric("🎯 Predicted Score", f"{eng_score:.1f}/100")
    
    with col2:
        performance = prediction.get('prediction_label', 'N/A')
        st.metric("📊 Performance", performance)
    
    with col3:
        percentile = prediction.get('percentile', 'N/A')
        st.metric("📈 Percentile", percentile)
    
    with col4:
        confidence = prediction.get('confidence_level', 'N/A').title()
        st.metric("✅ Confidence", confidence)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Current engagement vs predicted
        likes = post_data.get('likes') or 0
        comments = post_data.get('comments') or 0
        shares = post_data.get('shares') or 0
        current_total = likes + comments + shares
        
        # Normalize current engagement to 0-100 scale for comparison
        # Using simple normalization (this is just for visualization)
        current_normalized = min(100, current_total / 5)  # Rough normalization
        
        predicted_score = prediction.get('engagement_score', 0)
        fig_comparison = create_engagement_comparison_chart(current_normalized, predicted_score)
        st.plotly_chart(fig_comparison, width='stretch')
    
    with col2:
        # Score breakdown
        base_score = prediction.get('base_score', 0)
        quality_bonus = prediction.get('quality_bonus', 0)
        fig_breakdown = create_score_breakdown_chart(base_score, quality_bonus)
        st.plotly_chart(fig_breakdown, width='stretch')
    
    # Recommendations
    recommendations = prediction.get('recommendations', [])
    if recommendations:
        st.markdown("**📌 Recommendations:**")
        for rec in recommendations[:3]:  # Show top 3
            # Clean emoji from recommendations
            rec_clean = rec.replace('🔥', '').replace('✅', '').replace('💡', '').replace('⚠️', '').strip()
            st.write(f"• {rec_clean}")


def display_audience_fit(audience_df):
    """Display audience fit section."""
    st.markdown("<h2 class='section-header'>👥 Audience ICP Fit</h2>", unsafe_allow_html=True)
    
    if audience_df is None or audience_df.empty:
        st.info("Audience ranking data not available. Run the ICP analyzer with audience data to see this section.")
        return
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_audience = len(audience_df)
        st.metric("👥 Total Audience", total_audience)
    
    with col2:
        avg_score = audience_df['relevance_score'].mean()
        st.metric("📊 Avg Relevance", f"{avg_score:.1f}/100")
    
    with col3:
        hot_leads = (audience_df['lead_priority'] == 'Hot').sum()
        st.metric("🔥 Hot Leads", hot_leads)
    
    with col4:
        warm_leads = (audience_df['lead_priority'] == 'Warm').sum()
        st.metric("⚡ Warm Leads", warm_leads)
    
    # Top 10 chart
    df_top_10 = audience_df.nlargest(10, 'relevance_score')
    fig_audience = create_audience_relevance_chart(df_top_10)
    st.plotly_chart(fig_audience, width='stretch')
    
    # Detailed table for top 10
    st.markdown("**📋 Top 10 Audience Members - Detailed View**")
    
    display_df = df_top_10[[
        'profile_name', 'job_title', 'company', 'industry',
        'relevance_score', 'lead_priority', 'icp_match_reason'
    ]].copy()
    
    # Format for display
    display_df.columns = ['Name', 'Job Title', 'Company', 'Industry', 'Score', 'Priority', 'Match Reason']
    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.0f}/100")
    
    # Color code by priority using newer API
    def color_priority(val):
        if val == 'Hot':
            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif val == 'Warm':
            return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
        else:
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    
    styled_df = display_df.style.map(color_priority, subset=['Priority'])
    st.dataframe(styled_df, width='stretch', height=400)


def main():
    """Main dashboard function."""
    
    # Display header
    display_header()
    
    # Load data
    post_data = load_post_data()
    analysis_data = load_analysis_data()
    audience_df = load_audience_data()
    
    if post_data is None:
        st.error("❌ Unable to load post data. Please ensure data files exist.")
        st.stop()
    
    # Use analysis data if available, otherwise fall back to post data
    if analysis_data is None:
        analysis_data = {'scraped_data': post_data, 'text_features': {}, 'engagement_prediction': {}}
    
    # Add divider
    st.markdown("---")
    
    # Display sections
    display_post_details(post_data, analysis_data)
    
    st.markdown("---")
    
    # Two column layout for features and sentiment
    col1, col2 = st.columns(2)
    
    with col1:
        display_post_features(analysis_data)
    
    with col2:
        display_sentiment_analysis(analysis_data)
    
    st.markdown("---")
    
    display_engagement_prediction(analysis_data, post_data)
    
    st.markdown("---")
    
    display_audience_fit(audience_df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; padding: 20px;'>"
        "<small>LinkedIn Growth Analysis Tool | Built with Streamlit & Plotly</small>"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
