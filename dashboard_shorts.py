"""
Conversion Dashboard - The Brain Lab
Combines YouTube Shorts analytics with Gumroad sales data to show conversion rates.
"""

import os
from datetime import datetime
from typing import Optional

# Import our analytics modules
from modules.shorts_analytics import get_shorts_analytics
from modules.gumroad_tracker import (
    get_sales_analytics,
    match_sales_to_shorts,
    extract_video_id_from_referrer
)


def get_conversion_data(
    channel_id: Optional[str] = None,
    youtube_api_key: Optional[str] = None,
    gumroad_token: Optional[str] = None,
    product_id: Optional[str] = None,
    days: int = 30
) -> dict:
    """
    Fetches and combines YouTube Shorts + Gumroad sales data.

    Args:
        channel_id: YouTube channel ID (or from env)
        youtube_api_key: YouTube API key (or from env)
        gumroad_token: Gumroad access token (or from env)
        product_id: Optional Gumroad product ID filter
        days: Number of days to look back

    Returns:
        Dictionary with combined analytics and conversion metrics.
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
            'shorts': [],
            'sales': [],
            'conversions': []
        }

    # Fetch Gumroad sales data
    sales_result = get_sales_analytics(
        access_token=gumroad_token,
        product_id=product_id,
        days=days
    )

    if not sales_result['success']:
        return {
            'success': False,
            'error': f"Gumroad fetch failed: {sales_result['error']}",
            'shorts': youtube_result['shorts'],
            'sales': [],
            'conversions': []
        }

    shorts = youtube_result['shorts']
    sales = sales_result['sales']
    youtube_sales = sales_result['youtube_sales']

    # Match sales to shorts
    matched = match_sales_to_shorts(youtube_sales, shorts)

    # Build conversion data for each short
    conversions = []
    shorts_with_sales = {m['video_id']: m for m in matched}

    for short in shorts:
        video_id = short['video_id']
        views = short['views']

        # Get sales data for this short
        matched_data = shorts_with_sales.get(video_id, {})
        sale_count = matched_data.get('sale_count', 0)
        revenue = matched_data.get('total_revenue', 0)

        # Calculate conversion rate (sales per 1000 views)
        conversion_rate = (sale_count / views * 1000) if views > 0 else 0

        # Calculate revenue per 1000 views (RPM)
        rpm = (revenue / views * 1000) if views > 0 else 0

        conversions.append({
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
            'engagement_rate': round((short['likes'] + short['comments']) / views * 100, 2) if views > 0 else 0
        })

    # Sort by conversion rate (highest first)
    conversions.sort(key=lambda x: x['conversion_rate'], reverse=True)

    # Calculate summary statistics
    total_views = sum(c['views'] for c in conversions)
    total_sales = sum(c['sales'] for c in conversions)
    total_revenue = sum(c['revenue'] for c in conversions)

    # Shorts that generated sales
    converting_shorts = [c for c in conversions if c['sales'] > 0]

    summary = {
        'total_shorts': len(conversions),
        'total_views': total_views,
        'total_sales_all': sales_result['summary']['total_sales'],
        'total_sales_from_shorts': total_sales,
        'total_revenue_all': sales_result['summary']['total_revenue'],
        'total_revenue_from_shorts': round(total_revenue, 2),
        'youtube_attribution_rate': round(total_sales / sales_result['summary']['total_sales'] * 100, 1) if sales_result['summary']['total_sales'] > 0 else 0,
        'overall_conversion_rate': round(total_sales / total_views * 1000, 4) if total_views > 0 else 0,
        'overall_rpm': round(total_revenue / total_views * 1000, 2) if total_views > 0 else 0,
        'converting_shorts_count': len(converting_shorts),
        'conversion_percentage': round(len(converting_shorts) / len(conversions) * 100, 1) if conversions else 0,
        'top_converter': conversions[0] if conversions and conversions[0]['sales'] > 0 else None,
        'top_rpm': max(conversions, key=lambda x: x['rpm']) if conversions else None
    }

    return {
        'success': True,
        'error': None,
        'shorts': shorts,
        'sales': sales,
        'youtube_sales': youtube_sales,
        'conversions': conversions,
        'summary': summary,
        'youtube_summary': youtube_result['summary'],
        'sales_summary': sales_result['summary']
    }


def print_conversion_dashboard(data: dict):
    """
    Prints a formatted conversion dashboard.

    Args:
        data: Result from get_conversion_data()
    """
    if not data['success']:
        print(f"Error: {data['error']}")
        return

    summary = data['summary']
    conversions = data['conversions']

    print("\n" + "=" * 70)
    print("     YOUTUBE SHORTS CONVERSION DASHBOARD - THE BRAIN LAB")
    print("=" * 70)

    # Summary section
    print(f"\n{'SUMMARY':^70}")
    print("-" * 70)

    col_width = 33

    # Row 1
    print(f"{'Total Shorts:':<{col_width}} {summary['total_shorts']:>10}")
    print(f"{'Total Views:':<{col_width}} {summary['total_views']:>10,}")

    # Row 2
    print(f"{'Total Sales (All Sources):':<{col_width}} {summary['total_sales_all']:>10}")
    print(f"{'Sales from YouTube Shorts:':<{col_width}} {summary['total_sales_from_shorts']:>10}")

    # Row 3
    print(f"{'Total Revenue (All):':<{col_width}} ${summary['total_revenue_all']:>9.2f}")
    print(f"{'Revenue from Shorts:':<{col_width}} ${summary['total_revenue_from_shorts']:>9.2f}")

    print("-" * 70)

    # Key Metrics
    print(f"\n{'KEY CONVERSION METRICS':^70}")
    print("-" * 70)

    print(f"{'YouTube Attribution Rate:':<{col_width}} {summary['youtube_attribution_rate']:>9.1f}%")
    print(f"{'Conversion Rate (per 1K views):':<{col_width}} {summary['overall_conversion_rate']:>10.4f}")
    print(f"{'Revenue per 1K Views (RPM):':<{col_width}} ${summary['overall_rpm']:>9.2f}")
    print(f"{'Shorts with Sales:':<{col_width}} {summary['converting_shorts_count']:>10} ({summary['conversion_percentage']:.1f}%)")

    # Top performers
    if summary['top_converter']:
        print(f"\n{'TOP CONVERTING SHORT':^70}")
        print("-" * 70)
        tc = summary['top_converter']
        print(f"  Title: {tc['title'][:55]}...")
        print(f"  Views: {tc['views']:,} | Sales: {tc['sales']} | Revenue: ${tc['revenue']:.2f}")
        print(f"  Conversion Rate: {tc['conversion_rate']:.4f} per 1K views")

    if summary['top_rpm'] and summary['top_rpm']['rpm'] > 0:
        print(f"\n{'HIGHEST RPM SHORT':^70}")
        print("-" * 70)
        tr = summary['top_rpm']
        print(f"  Title: {tr['title'][:55]}...")
        print(f"  Views: {tr['views']:,} | Revenue: ${tr['revenue']:.2f}")
        print(f"  RPM: ${tr['rpm']:.2f} per 1K views")

    # Conversion table
    print(f"\n{'ALL SHORTS - SORTED BY CONVERSION RATE':^70}")
    print("-" * 70)
    print(f"{'#':<3} {'Title':<30} {'Views':>10} {'Sales':>6} {'Rev':>8} {'Conv':>8} {'RPM':>8}")
    print("-" * 70)

    for i, conv in enumerate(conversions[:20], 1):  # Top 20
        title = conv['title'][:28] + ".." if len(conv['title']) > 30 else conv['title']
        print(f"{i:<3} {title:<30} {conv['views']:>10,} {conv['sales']:>6} ${conv['revenue']:>6.2f} {conv['conversion_rate']:>8.4f} ${conv['rpm']:>6.2f}")

    if len(conversions) > 20:
        print(f"... and {len(conversions) - 20} more shorts")

    # Insights
    print(f"\n{'INSIGHTS':^70}")
    print("-" * 70)

    if summary['converting_shorts_count'] == 0:
        print("  - No Shorts have generated trackable sales yet.")
        print("  - Ensure your Gumroad link is in your YouTube bio.")
        print("  - Consider adding clearer CTAs in your Shorts.")
    else:
        # Average conversion rate for converting shorts
        converting_shorts = [c for c in conversions if c['sales'] > 0]
        avg_conv = sum(c['conversion_rate'] for c in converting_shorts) / len(converting_shorts)

        print(f"  - {summary['converting_shorts_count']} out of {summary['total_shorts']} Shorts ({summary['conversion_percentage']:.1f}%) have generated sales.")
        print(f"  - Average conversion rate for performing Shorts: {avg_conv:.4f} per 1K views")

        # Find patterns in top performers
        if len(converting_shorts) >= 3:
            top_3 = converting_shorts[:3]
            avg_views = sum(c['views'] for c in top_3) / 3
            avg_engagement = sum(c['engagement_rate'] for c in top_3) / 3
            print(f"  - Top 3 converters avg {avg_views:,.0f} views with {avg_engagement:.2f}% engagement.")

    print("\n" + "=" * 70)


def export_conversion_csv(data: dict, filename: str = "conversions.csv"):
    """
    Exports conversion data to a CSV file.

    Args:
        data: Result from get_conversion_data()
        filename: Output filename
    """
    import csv

    if not data['success'] or not data['conversions']:
        print(f"No data to export")
        return

    conversions = data['conversions']

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Rank', 'Video ID', 'Title', 'Views', 'Likes', 'Comments',
            'Engagement Rate', 'Sales', 'Revenue', 'Conversion Rate', 'RPM',
            'Published At', 'Duration (sec)'
        ])

        # Data
        for i, conv in enumerate(conversions, 1):
            writer.writerow([
                i,
                conv['video_id'],
                conv['title'],
                conv['views'],
                conv['likes'],
                conv['comments'],
                conv['engagement_rate'],
                conv['sales'],
                conv['revenue'],
                conv['conversion_rate'],
                conv['rpm'],
                conv['published_at'],
                conv['duration_seconds']
            ])

    print(f"Exported {len(conversions)} records to {filename}")


# CLI entry point
if __name__ == "__main__":
    import sys

    # Parse arguments
    days = 30
    export_csv = False

    for arg in sys.argv[1:]:
        if arg.isdigit():
            days = int(arg)
        elif arg == "--csv":
            export_csv = True

    print(f"Fetching conversion data...")
    print(f"Looking back: {days} days")
    print("-" * 50)

    data = get_conversion_data(days=days)

    if data['success']:
        print_conversion_dashboard(data)

        if export_csv:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"conversions_{timestamp}.csv"
            export_conversion_csv(data, filename)
    else:
        print(f"Error: {data['error']}")
