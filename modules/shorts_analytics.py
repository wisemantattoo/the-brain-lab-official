"""
YouTube Shorts Analytics Module - The Brain Lab
Fetches and analyzes YouTube Shorts performance data.
"""

import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from typing import Optional


def get_youtube_service(api_key: Optional[str] = None):
    """
    Creates a connection to YouTube Data API v3.

    Args:
        api_key: YouTube API key. If not provided, reads from environment.

    Returns:
        YouTube API service object or None if connection fails.
    """
    try:
        if api_key is None:
            api_key = os.environ.get("YOUTUBE_API_KEY")

        if not api_key:
            print("Error: YOUTUBE_API_KEY not found in environment")
            return None

        youtube = build('youtube', 'v3', developerKey=api_key)
        return youtube
    except Exception as e:
        print(f"Error connecting to YouTube API: {e}")
        return None


def get_channel_id_from_handle(youtube, handle: str) -> Optional[str]:
    """
    Converts a YouTube channel handle to channel ID.

    Args:
        youtube: YouTube API service object
        handle: Channel handle (e.g., '@TheBrainLab')

    Returns:
        Channel ID or None if not found.
    """
    try:
        # Remove @ if present
        handle = handle.lstrip('@')

        response = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        ).execute()

        if response.get('items'):
            return response['items'][0]['snippet']['channelId']
        return None
    except Exception as e:
        print(f"Error getting channel ID: {e}")
        return None


def get_channel_uploads_playlist(youtube, channel_id: str) -> Optional[str]:
    """
    Gets the uploads playlist ID for a channel.

    Args:
        youtube: YouTube API service object
        channel_id: YouTube channel ID

    Returns:
        Uploads playlist ID or None if not found.
    """
    try:
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if response.get('items'):
            return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return None
    except Exception as e:
        print(f"Error getting uploads playlist: {e}")
        return None


def fetch_shorts(youtube, channel_id: str, days: int = 30, max_results: int = 50) -> list:
    """
    Fetches YouTube Shorts from a channel within the specified time period.

    Shorts are identified by:
    - Duration <= 60 seconds
    - Vertical aspect ratio (though this requires additional API call)

    Args:
        youtube: YouTube API service object
        channel_id: YouTube channel ID
        days: Number of days to look back (default 30)
        max_results: Maximum number of videos to fetch (default 50)

    Returns:
        List of Shorts with video_id, title, views, likes, published_at
    """
    try:
        # Get uploads playlist
        uploads_playlist_id = get_channel_uploads_playlist(youtube, channel_id)
        if not uploads_playlist_id:
            print("Error: Could not find uploads playlist")
            return []

        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Fetch videos from uploads playlist
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            response = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            ).execute()

            for item in response.get('items', []):
                published_at_str = item['snippet']['publishedAt']
                # Parse ISO 8601 date format
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))

                # Check if video is within date range
                if published_at.replace(tzinfo=None) < date_threshold:
                    # Videos are sorted by date, so we can stop here
                    break

                videos.append({
                    'video_id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'published_at': published_at_str
                })

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        # Get video details (duration, statistics)
        if not videos:
            return []

        video_ids = [v['video_id'] for v in videos]
        shorts = []

        # Batch video details requests (max 50 per request)
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]

            details_response = youtube.videos().list(
                part='contentDetails,statistics,snippet',
                id=','.join(batch_ids)
            ).execute()

            for item in details_response.get('items', []):
                # Parse duration (ISO 8601 format: PT1M30S = 1 min 30 sec)
                duration_str = item['contentDetails']['duration']
                duration_seconds = parse_duration(duration_str)

                # Shorts are <= 60 seconds
                if duration_seconds <= 60:
                    statistics = item.get('statistics', {})
                    snippet = item.get('snippet', {})

                    # Find matching video data
                    video_data = next(
                        (v for v in videos if v['video_id'] == item['id']),
                        {}
                    )

                    shorts.append({
                        'video_id': item['id'],
                        'title': snippet.get('title', ''),
                        'views': int(statistics.get('viewCount', 0)),
                        'likes': int(statistics.get('likeCount', 0)),
                        'comments': int(statistics.get('commentCount', 0)),
                        'duration_seconds': duration_seconds,
                        'published_at': video_data.get('published_at', ''),
                        'description': snippet.get('description', ''),
                        'tags': snippet.get('tags', [])
                    })

        return shorts

    except Exception as e:
        print(f"Error fetching Shorts: {e}")
        return []


def parse_duration(duration_str: str) -> int:
    """
    Parses ISO 8601 duration format to seconds.

    Examples:
        PT1M30S -> 90 seconds
        PT45S -> 45 seconds
        PT1H2M3S -> 3723 seconds

    Args:
        duration_str: ISO 8601 duration string

    Returns:
        Duration in seconds
    """
    import re

    # Remove PT prefix
    duration_str = duration_str.replace('PT', '')

    hours = 0
    minutes = 0
    seconds = 0

    # Extract hours
    hours_match = re.search(r'(\d+)H', duration_str)
    if hours_match:
        hours = int(hours_match.group(1))

    # Extract minutes
    minutes_match = re.search(r'(\d+)M', duration_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))

    # Extract seconds
    seconds_match = re.search(r'(\d+)S', duration_str)
    if seconds_match:
        seconds = int(seconds_match.group(1))

    return hours * 3600 + minutes * 60 + seconds


def get_shorts_analytics(channel_id: str = None, api_key: str = None, days: int = 30) -> dict:
    """
    Main function to get YouTube Shorts analytics.

    Args:
        channel_id: YouTube channel ID. If not provided, reads from CHANNEL_ID env var.
        api_key: YouTube API key. If not provided, reads from YOUTUBE_API_KEY env var.
        days: Number of days to look back (default 30)

    Returns:
        Dictionary with:
        - shorts: List of Short data (video_id, title, views, likes)
        - summary: Aggregate statistics
        - success: Boolean indicating if fetch was successful
        - error: Error message if any
    """
    # Get credentials
    if channel_id is None:
        channel_id = os.environ.get("CHANNEL_ID")

    if not channel_id:
        return {
            'shorts': [],
            'summary': {},
            'success': False,
            'error': 'CHANNEL_ID not provided or found in environment'
        }

    # Connect to YouTube
    youtube = get_youtube_service(api_key)
    if not youtube:
        return {
            'shorts': [],
            'summary': {},
            'success': False,
            'error': 'Failed to connect to YouTube API'
        }

    # Fetch Shorts
    shorts = fetch_shorts(youtube, channel_id, days=days)

    if not shorts:
        return {
            'shorts': [],
            'summary': {},
            'success': True,
            'error': None,
            'message': f'No Shorts found in the last {days} days'
        }

    # Calculate summary statistics
    total_views = sum(s['views'] for s in shorts)
    total_likes = sum(s['likes'] for s in shorts)
    total_comments = sum(s['comments'] for s in shorts)

    summary = {
        'total_shorts': len(shorts),
        'total_views': total_views,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avg_views': round(total_views / len(shorts), 1) if shorts else 0,
        'avg_likes': round(total_likes / len(shorts), 1) if shorts else 0,
        'avg_engagement_rate': round((total_likes + total_comments) / total_views * 100, 2) if total_views > 0 else 0,
        'top_performer': max(shorts, key=lambda x: x['views']) if shorts else None
    }

    return {
        'shorts': shorts,
        'summary': summary,
        'success': True,
        'error': None
    }


def print_shorts_report(analytics_result: dict):
    """
    Prints a formatted report of Shorts analytics.

    Args:
        analytics_result: Result from get_shorts_analytics()
    """
    if not analytics_result['success']:
        print(f"Error: {analytics_result['error']}")
        return

    summary = analytics_result['summary']
    shorts = analytics_result['shorts']

    print("\n" + "=" * 60)
    print("YOUTUBE SHORTS ANALYTICS REPORT")
    print("=" * 60)

    if not shorts:
        print(analytics_result.get('message', 'No Shorts found'))
        return

    print(f"\nSummary (Last 30 Days)")
    print("-" * 40)
    print(f"Total Shorts:      {summary['total_shorts']}")
    print(f"Total Views:       {summary['total_views']:,}")
    print(f"Total Likes:       {summary['total_likes']:,}")
    print(f"Avg Views/Short:   {summary['avg_views']:,.1f}")
    print(f"Engagement Rate:   {summary['avg_engagement_rate']}%")

    if summary['top_performer']:
        print(f"\nTop Performer:")
        print(f"  Title: {summary['top_performer']['title'][:50]}...")
        print(f"  Views: {summary['top_performer']['views']:,}")

    print("\n" + "-" * 60)
    print("All Shorts (sorted by views)")
    print("-" * 60)

    # Sort by views descending
    sorted_shorts = sorted(shorts, key=lambda x: x['views'], reverse=True)

    for i, short in enumerate(sorted_shorts, 1):
        print(f"\n{i}. {short['title'][:50]}...")
        print(f"   Video ID: {short['video_id']}")
        print(f"   Views: {short['views']:,} | Likes: {short['likes']:,} | Comments: {short['comments']:,}")

    print("\n" + "=" * 60)


# CLI entry point
if __name__ == "__main__":
    import sys

    # Allow passing channel_id as argument
    channel_id = sys.argv[1] if len(sys.argv) > 1 else None
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    print(f"Fetching YouTube Shorts analytics...")
    print(f"Channel ID: {channel_id or 'from environment'}")
    print(f"Looking back: {days} days")

    result = get_shorts_analytics(channel_id=channel_id, days=days)
    print_shorts_report(result)
