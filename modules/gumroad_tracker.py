"""
Gumroad Sales Tracker Module - The Brain Lab
Fetches and tracks Gumroad sales with referrer data for YouTube attribution.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional


# Gumroad API configuration
GUMROAD_API_BASE = "https://api.gumroad.com/v2"


def get_gumroad_client(access_token: Optional[str] = None) -> dict:
    """
    Creates authentication headers for Gumroad API.

    Args:
        access_token: Gumroad access token. If not provided, reads from environment.

    Returns:
        Dictionary with headers and success status.
    """
    if access_token is None:
        access_token = os.environ.get("GUMROAD_ACCESS_TOKEN")

    if not access_token:
        return {
            'success': False,
            'error': 'GUMROAD_ACCESS_TOKEN not found in environment',
            'headers': None
        }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    return {
        'success': True,
        'error': None,
        'headers': headers,
        'access_token': access_token
    }


def fetch_sales(access_token: Optional[str] = None,
                product_id: Optional[str] = None,
                email: Optional[str] = None,
                after: Optional[str] = None,
                before: Optional[str] = None,
                page: int = 1) -> dict:
    """
    Fetches sales from Gumroad API with optional filters.

    Args:
        access_token: Gumroad access token
        product_id: Filter by specific product
        email: Filter by customer email
        after: Only return sales after this date (YYYY-MM-DD)
        before: Only return sales before this date (YYYY-MM-DD)
        page: Page number for pagination

    Returns:
        Dictionary with sales list and metadata.
    """
    client = get_gumroad_client(access_token)
    if not client['success']:
        return {
            'sales': [],
            'success': False,
            'error': client['error']
        }

    # Build request parameters
    params = {
        'access_token': client['access_token']
    }

    if product_id:
        params['product_id'] = product_id
    if email:
        params['email'] = email
    if after:
        params['after'] = after
    if before:
        params['before'] = before
    if page > 1:
        params['page'] = page

    try:
        response = requests.get(
            f"{GUMROAD_API_BASE}/sales",
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return {
                'sales': [],
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }

        data = response.json()

        if not data.get('success', False):
            return {
                'sales': [],
                'success': False,
                'error': data.get('message', 'Unknown API error')
            }

        return {
            'sales': data.get('sales', []),
            'next_page_url': data.get('next_page_url'),
            'success': True,
            'error': None
        }

    except requests.exceptions.RequestException as e:
        return {
            'sales': [],
            'success': False,
            'error': f'Request failed: {str(e)}'
        }
    except ValueError as e:
        return {
            'sales': [],
            'success': False,
            'error': f'Invalid JSON response: {str(e)}'
        }


def fetch_all_sales(access_token: Optional[str] = None,
                    product_id: Optional[str] = None,
                    days: int = 30) -> dict:
    """
    Fetches all sales from Gumroad, handling pagination.

    Args:
        access_token: Gumroad access token
        product_id: Filter by specific product (optional)
        days: Number of days to look back (default 30)

    Returns:
        Dictionary with all sales and metadata.
    """
    # Calculate date range
    after_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')

    all_sales = []
    page = 1
    max_pages = 100  # Safety limit

    while page <= max_pages:
        result = fetch_sales(
            access_token=access_token,
            product_id=product_id,
            after=after_date,
            page=page
        )

        if not result['success']:
            if all_sales:
                # Return what we have so far
                return {
                    'sales': all_sales,
                    'success': True,
                    'error': f'Partial fetch: {result["error"]}',
                    'total_fetched': len(all_sales)
                }
            return result

        all_sales.extend(result['sales'])

        # Check for more pages
        if not result.get('next_page_url'):
            break

        page += 1

    return {
        'sales': all_sales,
        'success': True,
        'error': None,
        'total_fetched': len(all_sales)
    }


def parse_sale(sale: dict) -> dict:
    """
    Parses a sale record into a standardized format.

    Args:
        sale: Raw sale data from Gumroad API

    Returns:
        Standardized sale dictionary.
    """
    return {
        'sale_id': sale.get('id', ''),
        'product_id': sale.get('product_id', ''),
        'product_name': sale.get('product_name', ''),
        'email': sale.get('email', ''),
        'price': sale.get('price', 0),
        'currency': sale.get('currency', 'USD'),
        'created_at': sale.get('created_at', ''),
        'referrer': sale.get('referrer', 'direct'),
        'country': sale.get('country', ''),
        'ip_country': sale.get('ip_country', ''),
        'quantity': sale.get('quantity', 1),
        'is_gift': sale.get('is_gift_receiver_purchase', False),
        'variants': sale.get('variants', {}),
        'affiliate': sale.get('affiliate', {}),
        'offer_code': sale.get('offer_code', {})
    }


def extract_youtube_referrals(sales: list) -> list:
    """
    Filters sales that came from YouTube referrals.

    Args:
        sales: List of parsed sales

    Returns:
        List of sales with YouTube as referrer.
    """
    youtube_patterns = [
        'youtube.com',
        'youtu.be',
        'm.youtube.com',
        'youtube',
        'yt'
    ]

    youtube_sales = []
    for sale in sales:
        referrer = (sale.get('referrer') or '').lower()
        if any(pattern in referrer for pattern in youtube_patterns):
            youtube_sales.append(sale)

    return youtube_sales


def extract_video_id_from_referrer(referrer: str) -> Optional[str]:
    """
    Attempts to extract a YouTube video ID from a referrer URL.

    Args:
        referrer: Referrer URL string

    Returns:
        Video ID if found, None otherwise.
    """
    import re

    if not referrer:
        return None

    referrer = referrer.lower()

    # Pattern for youtube.com/watch?v=VIDEO_ID
    watch_pattern = r'(?:youtube\.com/watch\?.*v=|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'
    match = re.search(watch_pattern, referrer, re.IGNORECASE)
    if match:
        return match.group(1)

    # Pattern for youtu.be/VIDEO_ID
    short_pattern = r'youtu\.be/([a-zA-Z0-9_-]{11})'
    match = re.search(short_pattern, referrer, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def match_sales_to_shorts(sales: list, shorts: list) -> list:
    """
    Matches sales to YouTube Shorts based on referrer data.

    Args:
        sales: List of parsed sales from Gumroad
        shorts: List of Shorts from YouTube analytics (must have 'video_id' field)

    Returns:
        List of matched records with Short data and associated sales.
    """
    # Create a lookup of shorts by video_id
    shorts_lookup = {s['video_id']: s for s in shorts}
    short_ids = set(shorts_lookup.keys())

    # Track sales per video
    video_sales = {}

    for sale in sales:
        referrer = sale.get('referrer', '')
        video_id = extract_video_id_from_referrer(referrer)

        if video_id and video_id in short_ids:
            if video_id not in video_sales:
                video_sales[video_id] = {
                    'video_id': video_id,
                    'short': shorts_lookup[video_id],
                    'sales': [],
                    'total_revenue': 0,
                    'sale_count': 0
                }

            video_sales[video_id]['sales'].append(sale)
            video_sales[video_id]['total_revenue'] += sale.get('price', 0) / 100  # Convert cents to dollars
            video_sales[video_id]['sale_count'] += 1

    return list(video_sales.values())


def get_sales_analytics(access_token: Optional[str] = None,
                        product_id: Optional[str] = None,
                        days: int = 30) -> dict:
    """
    Main function to get Gumroad sales analytics with YouTube attribution.

    Args:
        access_token: Gumroad access token. If not provided, reads from environment.
        product_id: Filter by specific product (optional)
        days: Number of days to look back (default 30)

    Returns:
        Dictionary with:
        - sales: List of parsed sales
        - youtube_sales: Sales from YouTube referrers
        - summary: Aggregate statistics
        - success: Boolean indicating if fetch was successful
        - error: Error message if any
    """
    # Fetch all sales
    result = fetch_all_sales(access_token=access_token, product_id=product_id, days=days)

    if not result['success']:
        return {
            'sales': [],
            'youtube_sales': [],
            'summary': {},
            'success': False,
            'error': result['error']
        }

    # Parse sales
    parsed_sales = [parse_sale(s) for s in result['sales']]

    # Filter YouTube referrals
    youtube_sales = extract_youtube_referrals(parsed_sales)

    # Calculate summary statistics
    total_revenue = sum(s['price'] for s in parsed_sales) / 100  # Convert cents to dollars
    youtube_revenue = sum(s['price'] for s in youtube_sales) / 100

    summary = {
        'total_sales': len(parsed_sales),
        'total_revenue': round(total_revenue, 2),
        'youtube_sales': len(youtube_sales),
        'youtube_revenue': round(youtube_revenue, 2),
        'youtube_percentage': round(len(youtube_sales) / len(parsed_sales) * 100, 1) if parsed_sales else 0,
        'avg_sale_price': round(total_revenue / len(parsed_sales), 2) if parsed_sales else 0,
        'referrer_breakdown': get_referrer_breakdown(parsed_sales)
    }

    return {
        'sales': parsed_sales,
        'youtube_sales': youtube_sales,
        'summary': summary,
        'success': True,
        'error': None
    }


def get_referrer_breakdown(sales: list) -> dict:
    """
    Analyzes referrer sources and counts.

    Args:
        sales: List of parsed sales

    Returns:
        Dictionary with referrer counts and percentages.
    """
    referrer_counts = {}

    for sale in sales:
        referrer = sale.get('referrer', 'direct') or 'direct'

        # Categorize referrer
        referrer_lower = referrer.lower()
        if 'youtube' in referrer_lower or 'youtu.be' in referrer_lower:
            category = 'YouTube'
        elif 'twitter' in referrer_lower or 'x.com' in referrer_lower:
            category = 'Twitter/X'
        elif 'instagram' in referrer_lower:
            category = 'Instagram'
        elif 'tiktok' in referrer_lower:
            category = 'TikTok'
        elif 'facebook' in referrer_lower:
            category = 'Facebook'
        elif 'google' in referrer_lower:
            category = 'Google'
        elif 'gumroad' in referrer_lower:
            category = 'Gumroad Discover'
        elif referrer_lower in ['direct', '']:
            category = 'Direct'
        else:
            category = 'Other'

        referrer_counts[category] = referrer_counts.get(category, 0) + 1

    # Calculate percentages
    total = sum(referrer_counts.values())
    return {
        source: {
            'count': count,
            'percentage': round(count / total * 100, 1) if total > 0 else 0
        }
        for source, count in sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)
    }


def print_sales_report(analytics_result: dict):
    """
    Prints a formatted report of Gumroad sales analytics.

    Args:
        analytics_result: Result from get_sales_analytics()
    """
    if not analytics_result['success']:
        print(f"Error: {analytics_result['error']}")
        return

    summary = analytics_result['summary']
    sales = analytics_result['sales']
    youtube_sales = analytics_result['youtube_sales']

    print("\n" + "=" * 60)
    print("GUMROAD SALES ANALYTICS REPORT")
    print("=" * 60)

    if not sales:
        print("No sales found in the specified period.")
        return

    print(f"\nSummary (Last 30 Days)")
    print("-" * 40)
    print(f"Total Sales:       {summary['total_sales']}")
    print(f"Total Revenue:     ${summary['total_revenue']:.2f}")
    print(f"Avg Sale Price:    ${summary['avg_sale_price']:.2f}")
    print(f"\nYouTube Attribution:")
    print(f"  Sales from YT:   {summary['youtube_sales']} ({summary['youtube_percentage']:.1f}%)")
    print(f"  YT Revenue:      ${summary['youtube_revenue']:.2f}")

    print(f"\nReferrer Breakdown:")
    print("-" * 40)
    for source, data in summary['referrer_breakdown'].items():
        print(f"  {source:20s} {data['count']:3d} sales ({data['percentage']:.1f}%)")

    if youtube_sales:
        print(f"\n" + "-" * 60)
        print("YouTube-Attributed Sales (Latest 10)")
        print("-" * 60)

        for i, sale in enumerate(youtube_sales[:10], 1):
            created = sale['created_at'][:10] if sale['created_at'] else 'N/A'
            print(f"\n{i}. {sale['product_name']}")
            print(f"   Date: {created} | Price: ${sale['price']/100:.2f}")
            print(f"   Referrer: {sale['referrer'][:60]}...")
            video_id = extract_video_id_from_referrer(sale['referrer'])
            if video_id:
                print(f"   Video ID: {video_id}")

    print("\n" + "=" * 60)


# CLI entry point
if __name__ == "__main__":
    import sys

    # Allow passing days as argument
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    print(f"Fetching Gumroad sales analytics...")
    print(f"Looking back: {days} days")

    result = get_sales_analytics(days=days)
    print_sales_report(result)
