"""
Hook Pattern Analyzer - The Brain Lab
Uses Gemini AI to analyze YouTube Short titles and identify which hooks convert.
"""

import os
import json
import statistics
from typing import Optional
from google import genai
from google.genai import types

# Import our analytics modules
from modules.shorts_analytics import get_shorts_analytics
from modules.gumroad_tracker import get_sales_analytics, match_sales_to_shorts


# Known hook categories based on winning_hooks.py patterns
HOOK_CATEGORIES = {
    "BRAIN FACT": {
        "description": "Facts about brain function and intelligence",
        "keywords": ["brain", "mind", "neural", "cognitive", "intelligence"],
        "example": "BRAIN FACT: Overthinking is a sign of high intelligence"
    },
    "PSYCHOLOGY FACT": {
        "description": "Psychological insights and behavior patterns",
        "keywords": ["psychology", "behavior", "study", "research", "people"],
        "example": "PSYCHOLOGY FACT: Smart people apologize less"
    },
    "SOCIAL INTELLIGENCE": {
        "description": "Social dynamics and interpersonal insights",
        "keywords": ["social", "people", "relationship", "trust", "impression"],
        "example": "SOCIAL INTELLIGENCE: The way you treat a waiter reveals character"
    },
    "BODY LANGUAGE": {
        "description": "Non-verbal communication and signals",
        "keywords": ["body", "posture", "eyes", "gesture", "nonverbal"],
        "example": "Your posture speaks before you do"
    },
    "DARK PSYCHOLOGY": {
        "description": "Manipulation tactics and detection",
        "keywords": ["manipulation", "liar", "detect", "dark", "gaslighting"],
        "example": "Excessive flattery is a manipulation tactic"
    },
    "PERFORMANCE": {
        "description": "Cognitive performance and optimization",
        "keywords": ["focus", "productivity", "sleep", "energy", "clarity"],
        "example": "Cold showers increase mental clarity"
    },
    "OTHER": {
        "description": "Hooks that don't fit standard categories",
        "keywords": [],
        "example": "Generic or unique hooks"
    }
}


def categorize_hook_by_rules(title: str) -> str:
    """
    Categorizes a hook based on rule-based pattern matching.

    Args:
        title: YouTube Short title

    Returns:
        Category name string
    """
    title_upper = title.upper()

    # Check for explicit prefixes first
    if "BRAIN FACT:" in title_upper or title_upper.startswith("BRAIN FACT"):
        return "BRAIN FACT"
    elif "PSYCHOLOGY FACT:" in title_upper or "PSYCHOLOGY SAYS:" in title_upper:
        return "PSYCHOLOGY FACT"
    elif "SOCIAL INTELLIGENCE:" in title_upper:
        return "SOCIAL INTELLIGENCE"

    # Keyword matching for less explicit titles
    title_lower = title.lower()

    for category, info in HOOK_CATEGORIES.items():
        if category == "OTHER":
            continue
        keywords = info["keywords"]
        if any(keyword in title_lower for keyword in keywords):
            return category

    return "OTHER"


def get_gemini_client(api_key: Optional[str] = None):
    """
    Creates a Gemini AI client.

    Args:
        api_key: Gemini API key. If not provided, reads from environment.

    Returns:
        Gemini client or None if connection fails.
    """
    try:
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment")
            return None

        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error creating Gemini client: {e}")
        return None


def analyze_hooks_with_gemini(
    shorts_data: list,
    api_key: Optional[str] = None
) -> list:
    """
    Uses Gemini AI to analyze and categorize YouTube Short titles.

    Args:
        shorts_data: List of shorts with title, views, conversion data
        api_key: Gemini API key (optional, reads from env)

    Returns:
        List of shorts with AI-generated category and analysis
    """
    client = get_gemini_client(api_key)

    if not client:
        print("Warning: Gemini unavailable, falling back to rule-based categorization")
        # Fall back to rule-based categorization
        for short in shorts_data:
            short['category'] = categorize_hook_by_rules(short['title'])
            short['ai_analysis'] = None
        return shorts_data

    # Prepare titles for batch analysis
    titles = [s['title'] for s in shorts_data]

    prompt = f"""Analyze these YouTube Short titles and categorize each one.

TITLES:
{json.dumps(titles, indent=2)}

CATEGORIES (choose one for each):
- BRAIN FACT: Facts about brain function, intelligence, cognitive abilities
- PSYCHOLOGY FACT: Psychological insights, behavior patterns, studies
- SOCIAL INTELLIGENCE: Social dynamics, interpersonal skills, relationship insights
- BODY LANGUAGE: Non-verbal communication, gestures, posture
- DARK PSYCHOLOGY: Manipulation tactics, deception detection, psychological tactics
- PERFORMANCE: Cognitive optimization, focus, productivity tips
- OTHER: Doesn't fit above categories

For each title, return:
1. The category (from list above)
2. The hook type (what makes it compelling: curiosity, surprise, promise, fear, etc.)
3. The emotional trigger (what emotion it targets)

OUTPUT FORMAT (JSON array):
[
  {{
    "title": "exact title text",
    "category": "CATEGORY_NAME",
    "hook_type": "curiosity/surprise/promise/fear/identity/controversy",
    "emotional_trigger": "brief description of targeted emotion"
  }},
  ...
]

Return ONLY valid JSON, no explanations."""

    try:
        models_to_try = [
            "gemini-2.0-flash-exp",
            "gemini-flash-latest"
        ]

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        temperature=0.3
                    ),
                    contents=prompt
                )

                # Parse JSON response
                response_text = response.text.strip()

                # Handle potential markdown code blocks
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()

                analyses = json.loads(response_text)

                # Match analyses to shorts
                analysis_map = {a['title']: a for a in analyses}

                for short in shorts_data:
                    if short['title'] in analysis_map:
                        analysis = analysis_map[short['title']]
                        short['category'] = analysis.get('category', 'OTHER')
                        short['hook_type'] = analysis.get('hook_type', 'unknown')
                        short['emotional_trigger'] = analysis.get('emotional_trigger', '')
                        short['ai_analysis'] = True
                    else:
                        # Fallback for unmatched
                        short['category'] = categorize_hook_by_rules(short['title'])
                        short['hook_type'] = 'unknown'
                        short['emotional_trigger'] = ''
                        short['ai_analysis'] = False

                return shorts_data

            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue

        # All models failed, use rule-based
        print("All Gemini models failed, using rule-based categorization")
        for short in shorts_data:
            short['category'] = categorize_hook_by_rules(short['title'])
            short['ai_analysis'] = False
        return shorts_data

    except Exception as e:
        print(f"Gemini analysis failed: {e}")
        # Fallback to rule-based
        for short in shorts_data:
            short['category'] = categorize_hook_by_rules(short['title'])
            short['ai_analysis'] = False
        return shorts_data


def calculate_category_performance(shorts_with_categories: list) -> dict:
    """
    Calculates performance metrics for each hook category.

    Args:
        shorts_with_categories: List of shorts with category and conversion data

    Returns:
        Dictionary with category performance metrics
    """
    category_stats = {}

    for short in shorts_with_categories:
        category = short.get('category', 'OTHER')

        if category not in category_stats:
            category_stats[category] = {
                'shorts': [],
                'total_views': 0,
                'total_sales': 0,
                'total_revenue': 0,
                'conversion_rates': [],
                'rpms': []
            }

        stats = category_stats[category]
        stats['shorts'].append(short)
        stats['total_views'] += short.get('views', 0)
        stats['total_sales'] += short.get('sales', 0)
        stats['total_revenue'] += short.get('revenue', 0)

        if short.get('conversion_rate', 0) > 0:
            stats['conversion_rates'].append(short['conversion_rate'])
        if short.get('rpm', 0) > 0:
            stats['rpms'].append(short['rpm'])

    # Calculate aggregate metrics for each category
    results = {}

    for category, stats in category_stats.items():
        count = len(stats['shorts'])
        total_views = stats['total_views']
        total_sales = stats['total_sales']
        total_revenue = stats['total_revenue']

        results[category] = {
            'count': count,
            'total_views': total_views,
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'avg_views': round(total_views / count, 1) if count > 0 else 0,
            'conversion_rate': round(total_sales / total_views * 1000, 4) if total_views > 0 else 0,
            'rpm': round(total_revenue / total_views * 1000, 2) if total_views > 0 else 0,
            'avg_conversion_rate': round(statistics.mean(stats['conversion_rates']), 4) if stats['conversion_rates'] else 0,
            'avg_rpm': round(statistics.mean(stats['rpms']), 2) if stats['rpms'] else 0,
            'converting_shorts': len([s for s in stats['shorts'] if s.get('sales', 0) > 0]),
            'shorts': stats['shorts']  # Include for detailed analysis
        }

    return results


def correlate_hooks_with_conversions(
    channel_id: Optional[str] = None,
    youtube_api_key: Optional[str] = None,
    gumroad_token: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    product_id: Optional[str] = None,
    days: int = 30
) -> dict:
    """
    Main function to analyze hooks and correlate with conversion data.

    Args:
        channel_id: YouTube channel ID (or from env)
        youtube_api_key: YouTube API key (or from env)
        gumroad_token: Gumroad access token (or from env)
        gemini_api_key: Gemini API key (or from env)
        product_id: Optional Gumroad product ID filter
        days: Number of days to look back

    Returns:
        Dictionary with hook analysis and conversion correlations
    """
    # Fetch YouTube Shorts data
    youtube_result = get_shorts_analytics(
        channel_id=channel_id,
        api_key=youtube_api_key,
        days=days
    )

    if not youtube_result['success']:
        return {
            'success': False,
            'error': f"YouTube fetch failed: {youtube_result['error']}",
            'category_performance': {},
            'shorts_analyzed': []
        }

    # Fetch Gumroad sales data
    sales_result = get_sales_analytics(
        access_token=gumroad_token,
        product_id=product_id,
        days=days
    )

    shorts = youtube_result['shorts']

    # Match sales to shorts if sales data available
    if sales_result['success'] and sales_result['youtube_sales']:
        matched = match_sales_to_shorts(sales_result['youtube_sales'], shorts)
        matched_map = {m['video_id']: m for m in matched}

        # Add conversion data to shorts
        for short in shorts:
            video_id = short['video_id']
            if video_id in matched_map:
                short['sales'] = matched_map[video_id]['sale_count']
                short['revenue'] = matched_map[video_id]['total_revenue']
            else:
                short['sales'] = 0
                short['revenue'] = 0

            # Calculate conversion metrics
            views = short.get('views', 0)
            short['conversion_rate'] = round(short['sales'] / views * 1000, 4) if views > 0 else 0
            short['rpm'] = round(short['revenue'] / views * 1000, 2) if views > 0 else 0
    else:
        # No sales data, set zeros
        for short in shorts:
            short['sales'] = 0
            short['revenue'] = 0
            short['conversion_rate'] = 0
            short['rpm'] = 0

    # Analyze hooks with Gemini
    analyzed_shorts = analyze_hooks_with_gemini(shorts, gemini_api_key)

    # Calculate category performance
    category_performance = calculate_category_performance(analyzed_shorts)

    # Sort categories by conversion rate
    sorted_categories = sorted(
        category_performance.items(),
        key=lambda x: x[1]['conversion_rate'],
        reverse=True
    )

    # Generate insights
    insights = generate_hook_insights(category_performance, analyzed_shorts)

    return {
        'success': True,
        'error': None,
        'shorts_analyzed': analyzed_shorts,
        'category_performance': dict(sorted_categories),
        'total_shorts': len(analyzed_shorts),
        'insights': insights,
        'youtube_summary': youtube_result['summary'],
        'sales_success': sales_result['success']
    }


def generate_hook_insights(category_performance: dict, shorts: list) -> list:
    """
    Generates actionable insights from hook analysis.

    Args:
        category_performance: Category performance metrics
        shorts: Analyzed shorts list

    Returns:
        List of insight strings
    """
    insights = []

    # Find top performing category
    if category_performance:
        sorted_cats = sorted(
            category_performance.items(),
            key=lambda x: x[1]['conversion_rate'],
            reverse=True
        )

        top_cat = sorted_cats[0]
        if top_cat[1]['conversion_rate'] > 0:
            insights.append(
                f"Top converting category: {top_cat[0]} with {top_cat[1]['conversion_rate']:.4f} sales per 1K views"
            )

        # Find most used category
        most_used = max(category_performance.items(), key=lambda x: x[1]['count'])
        insights.append(
            f"Most used category: {most_used[0]} ({most_used[1]['count']} shorts, {most_used[1]['avg_views']:.0f} avg views)"
        )

        # Find underutilized high-performers
        for cat, perf in sorted_cats:
            if perf['count'] <= 3 and perf['conversion_rate'] > 0:
                insights.append(
                    f"Potential opportunity: {cat} shows promise ({perf['conversion_rate']:.4f} conv rate) but only {perf['count']} shorts - consider creating more"
                )

    # Hook type analysis
    hook_types = {}
    for short in shorts:
        ht = short.get('hook_type', 'unknown')
        if ht not in hook_types:
            hook_types[ht] = {'count': 0, 'total_views': 0, 'total_sales': 0}
        hook_types[ht]['count'] += 1
        hook_types[ht]['total_views'] += short.get('views', 0)
        hook_types[ht]['total_sales'] += short.get('sales', 0)

    # Find best hook type
    for ht, data in hook_types.items():
        if ht != 'unknown' and data['total_views'] > 0:
            conv = data['total_sales'] / data['total_views'] * 1000
            if conv > 0:
                insights.append(
                    f"Hook type '{ht}' converts at {conv:.4f} per 1K views ({data['count']} shorts)"
                )

    return insights


def print_hook_analysis_report(result: dict):
    """
    Prints a formatted hook analysis report.

    Args:
        result: Result from correlate_hooks_with_conversions()
    """
    if not result['success']:
        print(f"Error: {result['error']}")
        return

    print("\n" + "=" * 70)
    print("     HOOK PATTERN ANALYSIS REPORT - THE BRAIN LAB")
    print("=" * 70)

    print(f"\nTotal Shorts Analyzed: {result['total_shorts']}")
    print(f"Sales Data Available: {'Yes' if result['sales_success'] else 'No'}")

    # Category Performance Table
    print(f"\n{'CATEGORY PERFORMANCE':^70}")
    print("-" * 70)
    print(f"{'Category':<20} {'Count':>6} {'Views':>10} {'Sales':>6} {'Conv Rate':>10} {'RPM':>10}")
    print("-" * 70)

    for category, perf in result['category_performance'].items():
        print(f"{category:<20} {perf['count']:>6} {perf['total_views']:>10,} {perf['total_sales']:>6} {perf['conversion_rate']:>10.4f} ${perf['rpm']:>9.2f}")

    # Insights
    print(f"\n{'INSIGHTS':^70}")
    print("-" * 70)

    for insight in result['insights']:
        print(f"  - {insight}")

    # Top Shorts by Category
    print(f"\n{'TOP SHORTS BY CATEGORY':^70}")
    print("-" * 70)

    for category, perf in list(result['category_performance'].items())[:5]:
        if perf['shorts']:
            # Get top short by views in this category
            top_short = max(perf['shorts'], key=lambda x: x.get('views', 0))
            print(f"\n{category}:")
            print(f"  Top: {top_short['title'][:50]}...")
            print(f"  Views: {top_short['views']:,} | Sales: {top_short.get('sales', 0)} | Conv: {top_short.get('conversion_rate', 0):.4f}")

    print("\n" + "=" * 70)


# CLI entry point
if __name__ == "__main__":
    import sys

    # Parse arguments
    days = 30

    for arg in sys.argv[1:]:
        if arg.isdigit():
            days = int(arg)

    print(f"Analyzing hook patterns...")
    print(f"Looking back: {days} days")
    print("-" * 50)

    result = correlate_hooks_with_conversions(days=days)
    print_hook_analysis_report(result)
