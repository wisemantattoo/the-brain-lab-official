"""
Weekly Summary Report Generator - The Brain Lab
Generates weekly performance summaries combining YouTube Shorts and Gumroad data.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.shorts_analytics import get_shorts_analytics
from modules.gumroad_tracker import get_sales_analytics, match_sales_to_shorts
from modules.hook_analyzer import categorize_hook_by_rules, calculate_category_performance


def get_week_date_range() -> tuple:
    """
    Calculates the start and end dates for the current week summary.

    Returns:
        Tuple of (start_date, end_date) as datetime objects.
    """
    today = datetime.now()
    # Go back 7 days for weekly summary
    start_date = today - timedelta(days=7)
    return start_date, today


def compile_weekly_stats(days: int = 7) -> dict:
    """
    Compiles all statistics for the weekly summary.

    Args:
        days: Number of days to look back (default 7 for weekly)

    Returns:
        Dictionary with compiled weekly statistics.
    """
    # Fetch YouTube Shorts data
    youtube_result = get_shorts_analytics(days=days)

    if not youtube_result['success']:
        return {
            'success': False,
            'error': f"YouTube fetch failed: {youtube_result['error']}",
            'data': {}
        }

    # Fetch Gumroad sales data
    sales_result = get_sales_analytics(days=days)

    if not sales_result['success']:
        return {
            'success': False,
            'error': f"Gumroad fetch failed: {sales_result['error']}",
            'data': {}
        }

    shorts = youtube_result['shorts']
    sales = sales_result['sales']
    youtube_sales = sales_result['youtube_sales']

    # Match sales to shorts
    matched = match_sales_to_shorts(youtube_sales, shorts)

    # Build conversion data for each short
    shorts_with_sales = {m['video_id']: m for m in matched}

    shorts_data = []
    for short in shorts:
        video_id = short['video_id']
        views = short['views']

        # Get sales data for this short
        matched_data = shorts_with_sales.get(video_id, {})
        sale_count = matched_data.get('sale_count', 0)
        revenue = matched_data.get('total_revenue', 0)

        # Calculate conversion rate
        conversion_rate = (sale_count / views * 1000) if views > 0 else 0
        rpm = (revenue / views * 1000) if views > 0 else 0

        # Categorize hook
        category = categorize_hook_by_rules(short['title'])

        shorts_data.append({
            'video_id': video_id,
            'title': short['title'],
            'views': views,
            'likes': short['likes'],
            'comments': short['comments'],
            'duration_seconds': short.get('duration_seconds', 0),
            'published_at': short.get('published_at', ''),
            'sales': sale_count,
            'revenue': revenue,
            'conversion_rate': round(conversion_rate, 4),
            'rpm': round(rpm, 2),
            'engagement_rate': round((short['likes'] + short['comments']) / views * 100, 2) if views > 0 else 0,
            'category': category
        })

    # Sort by views for display
    shorts_data.sort(key=lambda x: x['views'], reverse=True)

    # Calculate summary statistics
    total_views = sum(s['views'] for s in shorts_data)
    total_likes = sum(s['likes'] for s in shorts_data)
    total_comments = sum(s['comments'] for s in shorts_data)
    total_sales = sum(s['sales'] for s in shorts_data)
    total_revenue = sum(s['revenue'] for s in shorts_data)

    # Category performance
    category_stats = calculate_category_performance(shorts_data)

    # Find best performers
    top_by_views = max(shorts_data, key=lambda x: x['views']) if shorts_data else None
    converting_shorts = [s for s in shorts_data if s['sales'] > 0]
    top_converter = max(converting_shorts, key=lambda x: x['conversion_rate']) if converting_shorts else None
    top_rpm = max(converting_shorts, key=lambda x: x['rpm']) if converting_shorts else None

    # Calculate week-over-week comparison placeholder
    # (In a real implementation, you'd compare with previous week's data)

    summary = {
        'period': {
            'days': days,
            'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'youtube': {
            'total_shorts': len(shorts_data),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views_per_short': round(total_views / len(shorts_data), 1) if shorts_data else 0,
            'avg_engagement_rate': round((total_likes + total_comments) / total_views * 100, 2) if total_views > 0 else 0,
            'top_performer': top_by_views
        },
        'sales': {
            'total_sales': sales_result['summary']['total_sales'],
            'total_revenue': sales_result['summary']['total_revenue'],
            'youtube_sales': len(youtube_sales),
            'youtube_revenue': round(sum(s['price'] for s in youtube_sales) / 100, 2) if youtube_sales else 0,
            'youtube_attribution_rate': round(len(youtube_sales) / sales_result['summary']['total_sales'] * 100, 1) if sales_result['summary']['total_sales'] > 0 else 0,
            'referrer_breakdown': sales_result['summary']['referrer_breakdown']
        },
        'conversions': {
            'shorts_with_sales': len(converting_shorts),
            'conversion_percentage': round(len(converting_shorts) / len(shorts_data) * 100, 1) if shorts_data else 0,
            'total_shorts_sales': total_sales,
            'total_shorts_revenue': round(total_revenue, 2),
            'overall_conversion_rate': round(total_sales / total_views * 1000, 4) if total_views > 0 else 0,
            'overall_rpm': round(total_revenue / total_views * 1000, 2) if total_views > 0 else 0,
            'top_converter': top_converter,
            'top_rpm': top_rpm
        },
        'categories': category_stats,
        'shorts': shorts_data
    }

    return {
        'success': True,
        'error': None,
        'data': summary
    }


def generate_markdown_report(stats: dict, output_file: Optional[str] = None) -> str:
    """
    Generates a markdown-formatted weekly report.

    Args:
        stats: Result from compile_weekly_stats()
        output_file: Optional file path to save the report

    Returns:
        Markdown string of the report.
    """
    if not stats['success']:
        return f"# Weekly Report Error\n\n{stats['error']}"

    data = stats['data']
    period = data['period']
    youtube = data['youtube']
    sales = data['sales']
    conversions = data['conversions']
    categories = data['categories']
    shorts = data['shorts']

    # Build the markdown report
    md = []

    # Header
    md.append(f"# The Brain Lab - Weekly Performance Report")
    md.append(f"")
    md.append(f"**Period:** {period['start_date']} to {period['end_date']}")
    md.append(f"**Generated:** {period['generated_at']}")
    md.append(f"")

    # Summary Section
    md.append(f"---")
    md.append(f"")
    md.append(f"## 📊 Weekly Summary")
    md.append(f"")
    md.append(f"| Metric | This Week |")
    md.append(f"|--------|-----------|")
    md.append(f"| Total Shorts | {youtube['total_shorts']} |")
    md.append(f"| Total Views | {youtube['total_views']:,} |")
    md.append(f"| Avg Views/Short | {youtube['avg_views_per_short']:,.1f} |")
    md.append(f"| Engagement Rate | {youtube['avg_engagement_rate']:.2f}% |")
    md.append(f"| Total Sales | {sales['total_sales']} |")
    md.append(f"| Total Revenue | ${sales['total_revenue']:.2f} |")
    md.append(f"| YouTube Attribution | {sales['youtube_attribution_rate']:.1f}% |")
    md.append(f"")

    # YouTube Performance
    md.append(f"---")
    md.append(f"")
    md.append(f"## 📺 YouTube Shorts Performance")
    md.append(f"")

    if youtube['top_performer']:
        tp = youtube['top_performer']
        md.append(f"### 🏆 Top Performer by Views")
        md.append(f"")
        md.append(f"**{tp['title']}**")
        md.append(f"- Views: {tp['views']:,}")
        md.append(f"- Likes: {tp['likes']:,}")
        md.append(f"- Engagement: {tp.get('engagement_rate', 0):.2f}%")
        md.append(f"- [Watch](https://youtube.com/shorts/{tp['video_id']})")
        md.append(f"")

    # All shorts table
    md.append(f"### All Shorts This Week")
    md.append(f"")
    md.append(f"| # | Title | Views | Likes | Sales | Revenue |")
    md.append(f"|---|-------|-------|-------|-------|---------|")

    for i, short in enumerate(shorts[:15], 1):
        title = short['title'][:40] + "..." if len(short['title']) > 40 else short['title']
        md.append(f"| {i} | {title} | {short['views']:,} | {short['likes']:,} | {short['sales']} | ${short['revenue']:.2f} |")

    if len(shorts) > 15:
        md.append(f"| | *...and {len(shorts) - 15} more* | | | | |")

    md.append(f"")

    # Sales & Conversions
    md.append(f"---")
    md.append(f"")
    md.append(f"## 💰 Sales & Conversions")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Sales | {sales['total_sales']} |")
    md.append(f"| Total Revenue | ${sales['total_revenue']:.2f} |")
    md.append(f"| Sales from YouTube | {sales['youtube_sales']} |")
    md.append(f"| YouTube Revenue | ${sales['youtube_revenue']:.2f} |")
    md.append(f"| Shorts with Sales | {conversions['shorts_with_sales']} ({conversions['conversion_percentage']:.1f}%) |")
    md.append(f"| Conversion Rate | {conversions['overall_conversion_rate']:.4f} per 1K views |")
    md.append(f"| RPM | ${conversions['overall_rpm']:.2f} |")
    md.append(f"")

    # Top converters
    if conversions['top_converter']:
        tc = conversions['top_converter']
        md.append(f"### 🎯 Best Converting Short")
        md.append(f"")
        md.append(f"**{tc['title']}**")
        md.append(f"- Views: {tc['views']:,}")
        md.append(f"- Sales: {tc['sales']}")
        md.append(f"- Revenue: ${tc['revenue']:.2f}")
        md.append(f"- Conversion Rate: {tc['conversion_rate']:.4f} per 1K views")
        md.append(f"- [Watch](https://youtube.com/shorts/{tc['video_id']})")
        md.append(f"")

    if conversions['top_rpm'] and conversions['top_rpm'] != conversions['top_converter']:
        tr = conversions['top_rpm']
        md.append(f"### 💵 Highest RPM Short")
        md.append(f"")
        md.append(f"**{tr['title']}**")
        md.append(f"- Views: {tr['views']:,}")
        md.append(f"- Revenue: ${tr['revenue']:.2f}")
        md.append(f"- RPM: ${tr['rpm']:.2f} per 1K views")
        md.append(f"- [Watch](https://youtube.com/shorts/{tr['video_id']})")
        md.append(f"")

    # Referrer Breakdown
    md.append(f"### 📍 Sales by Traffic Source")
    md.append(f"")
    md.append(f"| Source | Sales | % |")
    md.append(f"|--------|-------|---|")

    for source, info in sales['referrer_breakdown'].items():
        md.append(f"| {source} | {info['count']} | {info['percentage']:.1f}% |")

    md.append(f"")

    # Category Performance
    md.append(f"---")
    md.append(f"")
    md.append(f"## 🏷️ Category Performance")
    md.append(f"")
    md.append(f"| Category | Shorts | Views | Sales | Conversion |")
    md.append(f"|----------|--------|-------|-------|------------|")

    for category, stats_data in sorted(categories.items(), key=lambda x: x[1].get('total_views', 0), reverse=True):
        if stats_data.get('count', 0) > 0:
            md.append(f"| {category} | {stats_data['count']} | {stats_data['total_views']:,} | {stats_data['total_sales']} | {stats_data['conversion_rate']:.4f} |")

    md.append(f"")

    # Key Insights
    md.append(f"---")
    md.append(f"")
    md.append(f"## 💡 Key Insights")
    md.append(f"")

    insights = generate_insights(data)
    for insight in insights:
        md.append(f"- {insight}")

    md.append(f"")

    # Footer
    md.append(f"---")
    md.append(f"")
    md.append(f"*Report generated by The Brain Lab Analytics System*")
    md.append(f"")

    report = "\n".join(md)

    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {output_file}")

    return report


def generate_insights(data: dict) -> list:
    """
    Generates actionable insights from the weekly data.

    Args:
        data: Compiled statistics data

    Returns:
        List of insight strings.
    """
    insights = []

    youtube = data['youtube']
    sales = data['sales']
    conversions = data['conversions']
    categories = data['categories']

    # Views insights
    if youtube['total_views'] > 0:
        avg_views = youtube['avg_views_per_short']
        if avg_views > 10000:
            insights.append(f"Strong views performance with {avg_views:,.0f} average views per Short.")
        elif avg_views > 5000:
            insights.append(f"Good views performance with {avg_views:,.0f} average views per Short.")
        else:
            insights.append(f"Views averaging {avg_views:,.0f} per Short. Consider testing new hook styles.")

    # Engagement insights
    if youtube['avg_engagement_rate'] > 5:
        insights.append(f"Excellent engagement rate of {youtube['avg_engagement_rate']:.2f}% - content is resonating.")
    elif youtube['avg_engagement_rate'] < 2:
        insights.append(f"Engagement rate of {youtube['avg_engagement_rate']:.2f}% is below average. Try more controversial hooks.")

    # Sales insights
    if sales['youtube_attribution_rate'] > 50:
        insights.append(f"YouTube drives {sales['youtube_attribution_rate']:.1f}% of sales - focus on YouTube optimization.")
    elif sales['youtube_attribution_rate'] < 20 and sales['total_sales'] > 0:
        insights.append(f"Only {sales['youtube_attribution_rate']:.1f}% of sales from YouTube. Consider stronger CTAs in Shorts.")

    # Conversion insights
    if conversions['shorts_with_sales'] > 0:
        insights.append(f"{conversions['shorts_with_sales']} Shorts generated sales ({conversions['conversion_percentage']:.1f}%).")
    else:
        insights.append("No Shorts generated trackable sales this week. Ensure bio link is visible.")

    # RPM insights
    if conversions['overall_rpm'] > 0:
        insights.append(f"Revenue per 1K views: ${conversions['overall_rpm']:.2f}")

    # Category insights
    if categories:
        top_category = max(categories.items(), key=lambda x: x[1].get('total_views', 0))
        if top_category[1].get('total_views', 0) > 0:
            insights.append(f"'{top_category[0]}' is your top performing category with {top_category[1]['total_views']:,} views.")

        # Find best converting category
        converting_cats = [(k, v) for k, v in categories.items() if v.get('total_sales', 0) > 0]
        if converting_cats:
            best_conv = max(converting_cats, key=lambda x: x[1].get('conversion_rate', 0))
            if best_conv[0] != top_category[0]:
                insights.append(f"'{best_conv[0]}' has the best conversion rate - consider making more.")

    return insights


def print_weekly_report(stats: dict):
    """
    Prints a formatted weekly report to console.

    Args:
        stats: Result from compile_weekly_stats()
    """
    if not stats['success']:
        print(f"Error: {stats['error']}")
        return

    data = stats['data']
    period = data['period']
    youtube = data['youtube']
    sales = data['sales']
    conversions = data['conversions']

    print("\n" + "=" * 70)
    print("     THE BRAIN LAB - WEEKLY PERFORMANCE REPORT")
    print("=" * 70)
    print(f"\nPeriod: {period['start_date']} to {period['end_date']}")
    print(f"Generated: {period['generated_at']}")

    # YouTube Summary
    print("\n" + "-" * 70)
    print("YOUTUBE SHORTS PERFORMANCE")
    print("-" * 70)
    print(f"  Total Shorts:          {youtube['total_shorts']}")
    print(f"  Total Views:           {youtube['total_views']:,}")
    print(f"  Avg Views/Short:       {youtube['avg_views_per_short']:,.1f}")
    print(f"  Engagement Rate:       {youtube['avg_engagement_rate']:.2f}%")

    if youtube['top_performer']:
        tp = youtube['top_performer']
        print(f"\n  Top Performer: {tp['title'][:50]}...")
        print(f"  Views: {tp['views']:,} | Likes: {tp['likes']:,}")

    # Sales Summary
    print("\n" + "-" * 70)
    print("SALES & REVENUE")
    print("-" * 70)
    print(f"  Total Sales:           {sales['total_sales']}")
    print(f"  Total Revenue:         ${sales['total_revenue']:.2f}")
    print(f"  YouTube Sales:         {sales['youtube_sales']} ({sales['youtube_attribution_rate']:.1f}%)")
    print(f"  YouTube Revenue:       ${sales['youtube_revenue']:.2f}")

    # Conversions Summary
    print("\n" + "-" * 70)
    print("CONVERSION METRICS")
    print("-" * 70)
    print(f"  Shorts with Sales:     {conversions['shorts_with_sales']} ({conversions['conversion_percentage']:.1f}%)")
    print(f"  Conversion Rate:       {conversions['overall_conversion_rate']:.4f} per 1K views")
    print(f"  Revenue/1K Views:      ${conversions['overall_rpm']:.2f}")

    if conversions['top_converter']:
        tc = conversions['top_converter']
        print(f"\n  Best Converter: {tc['title'][:50]}...")
        print(f"  Views: {tc['views']:,} | Sales: {tc['sales']} | Conv: {tc['conversion_rate']:.4f}")

    # Key Insights
    print("\n" + "-" * 70)
    print("KEY INSIGHTS")
    print("-" * 70)

    insights = generate_insights(data)
    for insight in insights:
        print(f"  • {insight}")

    print("\n" + "=" * 70)


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly performance report")
    parser.add_argument('days', nargs='?', type=int, default=7,
                        help='Number of days to look back (default: 7)')
    parser.add_argument('--markdown', '-m', action='store_true',
                        help='Generate markdown report')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output file path for markdown report')

    args = parser.parse_args()

    print(f"Compiling weekly stats...")
    print(f"Looking back: {args.days} days")
    print("-" * 50)

    stats = compile_weekly_stats(days=args.days)

    if stats['success']:
        if args.markdown:
            # Generate markdown report
            output_file = args.output or f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
            report = generate_markdown_report(stats, output_file)

            if not args.output:
                print("\n" + report)
        else:
            # Print console report
            print_weekly_report(stats)
    else:
        print(f"Error: {stats['error']}")
