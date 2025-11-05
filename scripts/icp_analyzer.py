"""
LinkedIn Audience ICP (Ideal Customer Profile) Analyzer

This module helps analyze LinkedIn post audience members to determine their relevance
to Wavess - a B2B SaaS GTM (Go-To-Market) platform for LinkedIn growth.

Use cases:
- Identify high-value audience members from post engagement
- Score leads based on ICP fit
- Prioritize outreach based on relevance scores
- Track audience quality over time
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ICP:
    """
    Ideal Customer Profile definition for Wavess.
    
    Wavess is a B2B SaaS platform for LinkedIn growth, targeting professionals
    who need to scale their LinkedIn presence for business development,
    brand building, and demand generation.
    """
    
    # Target job titles/roles (40 points max)
    target_roles: List[str] = field(default_factory=lambda: [
        # Marketing Roles
        'Marketing Manager', 'Marketing Director', 'VP Marketing', 'CMO',
        'Head of Marketing', 'Digital Marketing Manager', 'Content Marketing Manager',
        'Demand Generation Manager', 'Growth Marketing Manager', 'Brand Manager',
        
        # Growth Roles
        'Growth Manager', 'Growth Director', 'VP Growth', 'Head of Growth',
        'Business Development Manager', 'Business Development Director',
        
        # Product/GTM Roles
        'Product Marketing Manager', 'GTM Manager', 'GTM Director',
        'Revenue Operations Manager', 'Sales Operations Manager',
        
        # Executive Roles
        'CEO', 'Founder', 'Co-Founder', 'Chief Growth Officer', 'CRO',
        
        # Sales Roles (relevant for social selling)
        'Sales Manager', 'Sales Director', 'VP Sales', 'Account Executive',
        'Head of Sales', 'Sales Development Manager',
        
        # Other relevant roles
        'Community Manager', 'Social Media Manager', 'Social Media Director',
        'Content Director', 'Content Strategist', 'Strategy Manager'
    ])
    
    # Role categories for partial matching
    role_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        'marketing': ['marketing', 'brand', 'demand gen', 'demand generation', 'content'],
        'growth': ['growth', 'acquisition', 'expansion', 'scale'],
        'sales': ['sales', 'business development', 'bd', 'revenue', 'account executive', 'ae'],
        'product': ['product', 'gtm', 'go-to-market'],
        'executive': ['ceo', 'founder', 'chief', 'president', 'owner', 'coo', 'cro', 'cmo'],
        'social': ['social media', 'community', 'engagement', 'linkedin'],
        'operations': ['operations', 'ops', 'revops', 'revenue operations']
    })
    
    # Seniority levels (20 points max)
    seniority_levels: Dict[str, int] = field(default_factory=lambda: {
        'C-Level': 20,       # CEO, CMO, CRO, etc.
        'VP': 18,            # VP Marketing, VP Sales, etc.
        'Director': 16,      # Director-level roles
        'Head of': 16,       # Head of Marketing, Head of Growth, etc.
        'Senior Manager': 14, # Senior Manager roles
        'Manager': 12,       # Manager-level roles
        'Lead': 10,          # Team Lead, Product Lead, etc.
        'Senior': 8,         # Senior IC roles (Senior Marketing Specialist, etc.)
        'Specialist': 6,     # Individual contributor specialists
        'Coordinator': 4,    # Entry-level roles
        'Associate': 4,      # Junior roles
        'Intern': 2          # Internships
    })
    
    # Target industries (25 points max)
    target_industries: List[str] = field(default_factory=lambda: [
        # Primary targets
        'SaaS', 'Software', 'Technology', 'B2B SaaS', 'Enterprise Software',
        
        # Tech/Digital
        'Information Technology', 'Cloud Computing', 'Artificial Intelligence',
        'Machine Learning', 'Data Analytics', 'Cybersecurity',
        
        # Business Services
        'Marketing Services', 'Marketing Technology', 'MarTech',
        'Business Intelligence', 'Consulting',
        
        # Fintech/Modern Industries
        'Fintech', 'Financial Technology', 'Digital Payments',
        
        # Startups/Scale-ups
        'Startup', 'Scale-up', 'Venture Capital', 'Tech Startup',
        
        # E-commerce/Digital
        'E-commerce', 'Digital Commerce', 'Retail Technology'
    ])
    
    # Company size range (15 points max)
    # Optimal: 50-5000 employees (sweet spot for SaaS adoption)
    company_size_ranges: Dict[str, tuple] = field(default_factory=lambda: {
        'optimal': (50, 5000),      # Best fit - 15 points
        'good': (20, 10000),        # Good fit - 10 points
        'acceptable': (10, 50000),  # Acceptable - 5 points
    })
    
    # Geographic regions (informational, not scored)
    target_regions: List[str] = field(default_factory=lambda: [
        'North America', 'United States', 'Canada',
        'Europe', 'United Kingdom', 'Germany', 'France', 'Netherlands',
        'Asia Pacific', 'Australia', 'Singapore',
        'Global', 'Remote'
    ])
    
    # Bonus signals (additional points up to 20)
    bonus_signals: Dict[str, int] = field(default_factory=lambda: {
        'linkedin_influencer': 10,      # Has significant LinkedIn following
        'frequent_engagement': 5,        # Actively engages with content
        'content_creator': 8,            # Creates LinkedIn content regularly
        'premium_user': 5,               # Has LinkedIn Premium/Sales Nav
        'verified': 5,                   # Verified LinkedIn profile
        'active_in_target_groups': 6,   # Active in marketing/growth communities
        'event_speaker': 7,              # Speaks at industry events
        'thought_leader': 10             # Recognized industry expert
    })


def define_icp(custom_config: Optional[Dict[str, Any]] = None) -> ICP:
    """
    Define the Ideal Customer Profile for Wavess.
    
    Returns a default ICP optimized for a B2B SaaS LinkedIn growth tool,
    or a customized ICP if configuration is provided.
    
    Args:
        custom_config (Dict[str, Any], optional): Custom ICP configuration
            to override defaults. Can specify:
            - target_roles: List[str]
            - target_industries: List[str]
            - company_size_ranges: Dict[str, tuple]
            - seniority_levels: Dict[str, int]
            - bonus_signals: Dict[str, int]
    
    Returns:
        ICP: Configured Ideal Customer Profile
        
    Example:
        >>> icp = define_icp()
        >>> print(f"Targeting {len(icp.target_roles)} role types")
        >>> print(f"Across {len(icp.target_industries)} industries")
    """
    
    # Start with default ICP
    icp = ICP()
    
    # Apply custom configuration if provided
    if custom_config:
        if 'target_roles' in custom_config:
            icp.target_roles = custom_config['target_roles']
        if 'target_industries' in custom_config:
            icp.target_industries = custom_config['target_industries']
        if 'company_size_ranges' in custom_config:
            icp.company_size_ranges = custom_config['company_size_ranges']
        if 'seniority_levels' in custom_config:
            icp.seniority_levels = custom_config['seniority_levels']
        if 'bonus_signals' in custom_config:
            icp.bonus_signals = custom_config['bonus_signals']
    
    return icp


def calculate_audience_relevance_score(
    audience_member_profile: Dict[str, Any],
    icp: ICP
) -> Dict[str, Any]:
    """
    Calculate relevance score for an audience member based on ICP fit.
    
    SCORING BREAKDOWN:
    ==================
    - Role Match: 0-40 points
      * Exact title match: 40 points
      * Keyword match: 20-35 points based on relevance
      * No match: 0 points
      
    - Seniority Match: 0-20 points
      * Based on seniority_levels in ICP
      * Higher seniority = higher score
      
    - Industry Match: 0-25 points
      * Exact industry match: 25 points
      * Partial/related match: 15 points
      * No match: 0 points
      
    - Company Size Fit: 0-15 points
      * Optimal range (50-5000): 15 points
      * Good range (20-10000): 10 points
      * Acceptable range: 5 points
      * Outside ranges: 0 points
      
    - Bonus Signals: 0-20 points
      * LinkedIn influencer: +10 points
      * Content creator: +8 points
      * Event speaker: +7 points
      * Active engagement: +5 points
      * (capped at 20 total)
    
    TOTAL: 0-100 points + up to 20 bonus (max 120, normalized to 100)
    
    Args:
        audience_member_profile (Dict[str, Any]): Profile data structure:
            {
                'job_title': str,                    # Current job title
                'seniority': str,                    # Seniority level
                'industry': str,                     # Industry/sector
                'company_size': int,                 # Number of employees
                'location': str,                     # Geographic location
                'linkedin_followers': int,           # LinkedIn connection/follower count
                'engagement_history': Dict,          # Engagement metrics
                'profile_signals': List[str],        # Bonus signals present
                'company_name': str,                 # Company name (optional)
                'years_in_role': int,               # Tenure (optional)
                'education': str                    # Education background (optional)
            }
            
        icp (ICP): Ideal Customer Profile definition
        
    Returns:
        Dict[str, Any]: Relevance analysis containing:
            - relevance_score: int (0-100)
            - relevance_label: str ('High', 'Medium', 'Low', 'Not Relevant')
            - score_breakdown: Dict with component scores
            - match_details: Dict with matching criteria
            - recommendations: List of insights/actions
            - lead_priority: str ('Hot', 'Warm', 'Cold')
    
    Example:
        >>> profile = {
        ...     'job_title': 'VP Marketing',
        ...     'seniority': 'VP',
        ...     'industry': 'B2B SaaS',
        ...     'company_size': 250,
        ...     'location': 'San Francisco',
        ...     'linkedin_followers': 5000,
        ...     'profile_signals': ['content_creator', 'premium_user']
        ... }
        >>> icp = define_icp()
        >>> result = calculate_audience_relevance_score(profile, icp)
        >>> print(f"Score: {result['relevance_score']}/100 - {result['relevance_label']}")
    """
    
    # Initialize scoring components
    role_score = 0
    seniority_score = 0
    industry_score = 0
    company_size_score = 0
    bonus_score = 0
    
    # Track matching details
    match_details = {
        'role_match_type': 'none',
        'role_matched': None,
        'seniority_detected': None,
        'industry_matched': None,
        'company_size_category': None,
        'bonus_signals_found': []
    }
    
    # STEP 1: Calculate Role Score (0-40 points)
    # ===========================================
    job_title = audience_member_profile.get('job_title', '').lower()
    
    # Check for exact title match
    exact_match = False
    for target_role in icp.target_roles:
        if target_role.lower() == job_title or target_role.lower() in job_title:
            role_score = 40
            exact_match = True
            match_details['role_match_type'] = 'exact'
            match_details['role_matched'] = target_role
            break
    
    # If no exact match, check for keyword matches
    if not exact_match:
        keyword_matches = []
        for category, keywords in icp.role_keywords.items():
            for keyword in keywords:
                if keyword in job_title:
                    keyword_matches.append((category, keyword))
        
        if keyword_matches:
            # Score based on keyword relevance
            # Executive/Growth/Marketing keywords = higher scores
            top_category = keyword_matches[0][0]
            
            if top_category in ['executive', 'growth', 'marketing']:
                role_score = 35
                match_details['role_match_type'] = 'high_keyword'
            elif top_category in ['sales', 'product', 'social']:
                role_score = 25
                match_details['role_match_type'] = 'medium_keyword'
            elif top_category in ['operations']:
                role_score = 20
                match_details['role_match_type'] = 'low_keyword'
            
            match_details['role_matched'] = f"{top_category} ({keyword_matches[0][1]})"
    
    # STEP 2: Calculate Seniority Score (0-20 points)
    # ===============================================
    seniority = audience_member_profile.get('seniority', '')
    
    # Try to find seniority level
    for level, points in icp.seniority_levels.items():
        if level.lower() in seniority.lower() or level.lower() in job_title:
            seniority_score = points
            match_details['seniority_detected'] = level
            break
    
    # STEP 3: Calculate Industry Score (0-25 points)
    # ==============================================
    industry = audience_member_profile.get('industry', '').lower()
    
    # Check for exact industry match
    for target_industry in icp.target_industries:
        if target_industry.lower() in industry or industry in target_industry.lower():
            industry_score = 25
            match_details['industry_matched'] = target_industry
            break
    
    # If no exact match, check for partial/related matches
    if industry_score == 0:
        tech_keywords = ['tech', 'software', 'digital', 'cloud', 'internet', 'startup']
        business_keywords = ['business', 'services', 'consulting', 'agency']
        
        if any(keyword in industry for keyword in tech_keywords):
            industry_score = 15
            match_details['industry_matched'] = 'Tech-related'
        elif any(keyword in industry for keyword in business_keywords):
            industry_score = 10
            match_details['industry_matched'] = 'Business-related'
    
    # STEP 4: Calculate Company Size Score (0-15 points)
    # ==================================================
    company_size = audience_member_profile.get('company_size', 0)
    
    if company_size > 0:
        # Check optimal range (50-5000 employees)
        if icp.company_size_ranges['optimal'][0] <= company_size <= icp.company_size_ranges['optimal'][1]:
            company_size_score = 15
            match_details['company_size_category'] = 'Optimal'
        # Check good range (20-10000 employees)
        elif icp.company_size_ranges['good'][0] <= company_size <= icp.company_size_ranges['good'][1]:
            company_size_score = 10
            match_details['company_size_category'] = 'Good'
        # Check acceptable range (10-50000 employees)
        elif icp.company_size_ranges['acceptable'][0] <= company_size <= icp.company_size_ranges['acceptable'][1]:
            company_size_score = 5
            match_details['company_size_category'] = 'Acceptable'
        else:
            match_details['company_size_category'] = 'Outside target range'
    
    # STEP 5: Calculate Bonus Signals (0-20 points, capped)
    # =====================================================
    profile_signals = audience_member_profile.get('profile_signals', [])
    linkedin_followers = audience_member_profile.get('linkedin_followers', 0)
    engagement_history = audience_member_profile.get('engagement_history', {})
    
    # Check for LinkedIn influencer status (5000+ followers)
    if linkedin_followers >= 5000:
        bonus_score += icp.bonus_signals.get('linkedin_influencer', 10)
        match_details['bonus_signals_found'].append('LinkedIn Influencer (5K+ followers)')
    
    # Check for frequent engagement
    if engagement_history:
        posts_engaged = engagement_history.get('posts_engaged_last_30_days', 0)
        if posts_engaged >= 10:
            bonus_score += icp.bonus_signals.get('frequent_engagement', 5)
            match_details['bonus_signals_found'].append(f'Frequent Engagement ({posts_engaged} posts)')
    
    # Check for other signals
    for signal in profile_signals:
        if signal in icp.bonus_signals:
            bonus_score += icp.bonus_signals[signal]
            match_details['bonus_signals_found'].append(signal.replace('_', ' ').title())
    
    # Cap bonus score at 20 points
    bonus_score = min(20, bonus_score)
    
    # STEP 6: Calculate Final Score
    # =============================
    base_score = role_score + seniority_score + industry_score + company_size_score
    total_score = base_score + bonus_score
    
    # Normalize to 0-100 scale (since max is 120 with bonuses)
    final_score = min(100, int(total_score))
    
    # STEP 7: Determine Relevance Label and Priority
    # ==============================================
    if final_score >= 80:
        relevance_label = 'High'
        lead_priority = 'Hot'
    elif final_score >= 60:
        relevance_label = 'Medium-High'
        lead_priority = 'Warm'
    elif final_score >= 40:
        relevance_label = 'Medium'
        lead_priority = 'Warm'
    elif final_score >= 20:
        relevance_label = 'Low'
        lead_priority = 'Cold'
    else:
        relevance_label = 'Not Relevant'
        lead_priority = 'Cold'
    
    # STEP 8: Generate Recommendations
    # =================================
    recommendations = _generate_recommendations(
        final_score, match_details, audience_member_profile
    )
    
    # Compile results
    return {
        'relevance_score': final_score,
        'relevance_label': relevance_label,
        'lead_priority': lead_priority,
        'score_breakdown': {
            'role_score': role_score,
            'role_max': 40,
            'seniority_score': seniority_score,
            'seniority_max': 20,
            'industry_score': industry_score,
            'industry_max': 25,
            'company_size_score': company_size_score,
            'company_size_max': 15,
            'bonus_score': bonus_score,
            'bonus_max': 20,
            'base_score': base_score,
            'total_score': total_score
        },
        'match_details': match_details,
        'recommendations': recommendations
    }


def _generate_recommendations(
    score: int,
    match_details: Dict[str, Any],
    profile: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations based on relevance score."""
    
    recommendations = []
    
    # Overall assessment
    if score >= 80:
        recommendations.append("🔥 High-priority lead! Strong ICP match across all dimensions.")
        recommendations.append("💼 Recommend immediate personalized outreach.")
    elif score >= 60:
        recommendations.append("✅ Good ICP fit. Worth engaging with tailored messaging.")
    elif score >= 40:
        recommendations.append("💡 Moderate fit. Consider nurture campaign or content engagement.")
    else:
        recommendations.append("⚠️ Low ICP fit. Deprioritize unless specific indicators suggest otherwise.")
    
    # Role-specific recommendations
    if match_details['role_match_type'] == 'none':
        recommendations.append("❌ Role mismatch: Not in target function. May not have budget/authority.")
    elif match_details['role_match_type'] in ['low_keyword', 'medium_keyword']:
        recommendations.append("⚠️ Partial role match: Verify decision-making authority before outreach.")
    
    # Seniority recommendations
    if match_details['seniority_detected'] in ['C-Level', 'VP', 'Director', 'Head of']:
        recommendations.append("👔 Senior decision-maker: Strong buying authority. Focus on ROI/strategic value.")
    elif match_details['seniority_detected'] in ['Manager', 'Senior Manager']:
        recommendations.append("👤 Manager level: Likely influencer. May need buy-in from leadership.")
    
    # Company size recommendations
    if match_details['company_size_category'] == 'Optimal':
        recommendations.append("🎯 Ideal company size: Perfect fit for SaaS adoption and growth needs.")
    elif match_details['company_size_category'] == 'Outside target range':
        company_size = profile.get('company_size', 0)
        if company_size < 50:
            recommendations.append("🏢 Small company: May have budget constraints. Emphasize ROI and efficiency.")
        elif company_size > 10000:
            recommendations.append("🏢 Large enterprise: May have complex approval processes. Focus on scale benefits.")
    
    # Bonus signal recommendations
    if 'LinkedIn Influencer' in str(match_details.get('bonus_signals_found', [])):
        recommendations.append("⭐ LinkedIn influencer: High engagement potential. Could become advocate/champion.")
    
    if 'content_creator' in profile.get('profile_signals', []):
        recommendations.append("📝 Content creator: Active on LinkedIn. Potential for partnership/case study.")
    
    return recommendations


def batch_score_audience(
    audience_members: List[Dict[str, Any]],
    icp: ICP
) -> List[Dict[str, Any]]:
    """
    Score multiple audience members efficiently.
    
    Args:
        audience_members: List of audience member profiles
        icp: Ideal Customer Profile
        
    Returns:
        List of scored profiles with relevance data, sorted by score (high to low)
    """
    
    results = []
    for member in audience_members:
        score_result = calculate_audience_relevance_score(member, icp)
        results.append({
            'profile': member,
            'relevance': score_result
        })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x['relevance']['relevance_score'], reverse=True)
    
    return results


def get_audience_summary_stats(scored_audience: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for scored audience.
    
    Args:
        scored_audience: List of scored audience members from batch_score_audience()
        
    Returns:
        Dict with summary statistics
    """
    
    if not scored_audience:
        return {}
    
    scores = [member['relevance']['relevance_score'] for member in scored_audience]
    priorities = [member['relevance']['lead_priority'] for member in scored_audience]
    
    return {
        'total_audience': len(scored_audience),
        'average_relevance_score': round(sum(scores) / len(scores), 2),
        'high_relevance_count': sum(1 for s in scores if s >= 80),
        'medium_relevance_count': sum(1 for s in scores if 40 <= s < 80),
        'low_relevance_count': sum(1 for s in scores if s < 40),
        'hot_leads': sum(1 for p in priorities if p == 'Hot'),
        'warm_leads': sum(1 for p in priorities if p == 'Warm'),
        'cold_leads': sum(1 for p in priorities if p == 'Cold'),
        'top_score': max(scores),
        'lowest_score': min(scores),
        'audience_quality': 'Excellent' if sum(scores) / len(scores) >= 70 else
                          'Good' if sum(scores) / len(scores) >= 50 else
                          'Fair' if sum(scores) / len(scores) >= 30 else 'Poor'
    }


# Example usage and demonstration
if __name__ == "__main__":
    print("="*80)
    print("LINKEDIN AUDIENCE ICP ANALYZER - WAVESS")
    print("="*80)
    
    # Define ICP
    icp = define_icp()
    print(f"\n📋 ICP DEFINED:")
    print(f"   • Target Roles: {len(icp.target_roles)} role types")
    print(f"   • Target Industries: {len(icp.target_industries)} industries")
    print(f"   • Company Size: {icp.company_size_ranges['optimal'][0]}-{icp.company_size_ranges['optimal'][1]} employees (optimal)")
    
    # Example profiles
    print("\n\n" + "="*80)
    print("EXAMPLE AUDIENCE MEMBER PROFILES")
    print("="*80)
    
    # High-fit profile
    profile_high = {
        'job_title': 'VP Marketing',
        'seniority': 'VP',
        'industry': 'B2B SaaS',
        'company_size': 250,
        'location': 'San Francisco, CA',
        'linkedin_followers': 8000,
        'engagement_history': {
            'posts_engaged_last_30_days': 15,
            'comments_made': 8,
            'shares': 5
        },
        'profile_signals': ['content_creator', 'premium_user'],
        'company_name': 'TechCorp',
        'years_in_role': 2
    }
    
    print("\n🎯 PROFILE 1: High-Fit Lead")
    print("-"*80)
    print(f"Job Title: {profile_high['job_title']}")
    print(f"Industry: {profile_high['industry']}")
    print(f"Company Size: {profile_high['company_size']} employees")
    print(f"LinkedIn Followers: {profile_high['linkedin_followers']:,}")
    
    result_high = calculate_audience_relevance_score(profile_high, icp)
    print(f"\n📊 RELEVANCE SCORE: {result_high['relevance_score']}/100")
    print(f"Label: {result_high['relevance_label']}")
    print(f"Priority: {result_high['lead_priority']}")
    print(f"\nScore Breakdown:")
    print(f"  • Role: {result_high['score_breakdown']['role_score']}/40")
    print(f"  • Seniority: {result_high['score_breakdown']['seniority_score']}/20")
    print(f"  • Industry: {result_high['score_breakdown']['industry_score']}/25")
    print(f"  • Company Size: {result_high['score_breakdown']['company_size_score']}/15")
    print(f"  • Bonus Signals: {result_high['score_breakdown']['bonus_score']}/20")
    print(f"\nTop Recommendations:")
    for rec in result_high['recommendations'][:3]:
        print(f"  {rec}")
    
    # Medium-fit profile
    profile_medium = {
        'job_title': 'Marketing Manager',
        'seniority': 'Manager',
        'industry': 'Technology',
        'company_size': 1500,
        'location': 'New York, NY',
        'linkedin_followers': 2000,
        'engagement_history': {
            'posts_engaged_last_30_days': 5
        },
        'profile_signals': [],
        'company_name': 'MidTech Solutions'
    }
    
    print("\n\n📊 PROFILE 2: Medium-Fit Lead")
    print("-"*80)
    print(f"Job Title: {profile_medium['job_title']}")
    print(f"Industry: {profile_medium['industry']}")
    print(f"Company Size: {profile_medium['company_size']} employees")
    
    result_medium = calculate_audience_relevance_score(profile_medium, icp)
    print(f"\n📊 RELEVANCE SCORE: {result_medium['relevance_score']}/100")
    print(f"Label: {result_medium['relevance_label']}")
    print(f"Priority: {result_medium['lead_priority']}")
    
    # Low-fit profile
    profile_low = {
        'job_title': 'Software Engineer',
        'seniority': 'Senior',
        'industry': 'Healthcare',
        'company_size': 50000,
        'location': 'Boston, MA',
        'linkedin_followers': 500,
        'engagement_history': {},
        'profile_signals': [],
        'company_name': 'HealthCare Mega Corp'
    }
    
    print("\n\n⚠️ PROFILE 3: Low-Fit Lead")
    print("-"*80)
    print(f"Job Title: {profile_low['job_title']}")
    print(f"Industry: {profile_low['industry']}")
    print(f"Company Size: {profile_low['company_size']:,} employees")
    
    result_low = calculate_audience_relevance_score(profile_low, icp)
    print(f"\n📊 RELEVANCE SCORE: {result_low['relevance_score']}/100")
    print(f"Label: {result_low['relevance_label']}")
    print(f"Priority: {result_low['lead_priority']}")
    
    # Batch scoring demo
    print("\n\n" + "="*80)
    print("BATCH SCORING DEMONSTRATION")
    print("="*80)
    
    audience = [profile_high, profile_medium, profile_low]
    scored = batch_score_audience(audience, icp)
    stats = get_audience_summary_stats(scored)
    
    print(f"\nAudience Quality Summary:")
    print(f"  • Total Audience: {stats['total_audience']}")
    print(f"  • Average Score: {stats['average_relevance_score']}/100")
    print(f"  • Quality Rating: {stats['audience_quality']}")
    print(f"  • Hot Leads: {stats['hot_leads']}")
    print(f"  • Warm Leads: {stats['warm_leads']}")
    print(f"  • Cold Leads: {stats['cold_leads']}")
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print("="*80)
