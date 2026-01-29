# YouTube Integration Analysis - The Brain Lab Bot

**Audit Date:** 2026-01-29
**Story 5:** YouTube Integration Issues
**Status:** Comprehensive Review Complete

---

## Executive Summary

The Brain Lab bot uses YouTube API v3 for two distinct purposes:
1. **Video Upload** (`youtube_unit.py`) - OAuth2 authenticated uploads with auto-commenting
2. **Analytics Fetching** (`shorts_analytics.py`, `sync_youtube.py`) - API key based read operations

This audit identifies **14 issues** across OAuth handling, upload errors, commenting, metadata, and retry logic.

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 2 | OAuth token expiration, missing upload validation |
| HIGH | 5 | No retry logic, generic error handling, missing timeouts |
| MEDIUM | 4 | Shorts metadata, resumable upload underutilized, duplicate connections |
| LOW | 3 | Logging consistency, hardcoded values, code duplication |

---

## 1. OAuth Token Refresh Mechanism

### Current Implementation

**File:** `modules/youtube_unit.py` (lines 22-31)

```python
creds = Credentials(
    token=None,
    refresh_token=SECRETS["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=SECRETS["GOOGLE_CLIENT_ID"],
    client_secret=SECRETS["GOOGLE_CLIENT_SECRET"]
)

print("Refreshing OAuth token...")
creds.refresh(Request())
```

### Issues Found

#### CRITICAL-1: No Refresh Token Expiration Handling

**Problem:** OAuth refresh tokens can expire or be revoked in several scenarios:
- User revokes app access in Google Account settings
- Refresh token not used for 6+ months
- App exceeds maximum refresh tokens per user (50)
- Google security policy changes

**Current Behavior:** Generic exception handling catches all errors without distinguishing token expiration:

```python
except Exception as e:
    print(f"YOUTUBE ERROR: {e}")
```

**Recommended Fix:**
```python
from google.auth.exceptions import RefreshError

try:
    creds.refresh(Request())
except RefreshError as e:
    error_msg = str(e)
    if 'invalid_grant' in error_msg:
        print("CRITICAL: Refresh token expired or revoked!")
        print("ACTION REQUIRED: Re-authenticate with OAuth flow")
        # Optionally notify via webhook/email
        return None
    elif 'Token has been revoked' in error_msg:
        print("CRITICAL: User revoked app access!")
        return None
    else:
        raise
```

#### HIGH-2: No Token Validation Before Use

**Problem:** Code assumes `SECRETS` values exist and are valid. If any OAuth credential is missing or malformed, the error isn't caught until `creds.refresh()` fails.

**Current Check (main.py):**
```python
required_keys = ["GEMINI_API_KEY", "YOUTUBE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
if not all(SECRETS.get(key) for key in required_keys):
    print("ERROR: Missing YouTube OAuth credentials")
```

**Missing:** Validation that credentials are properly formatted (e.g., refresh token starts with expected prefix).

#### MEDIUM-3: Duplicate YouTube API Connections

Two files create YouTube API connections differently:
- `youtube_unit.py`: OAuth2 credentials (for upload/write operations)
- `sync_youtube.py` / `shorts_analytics.py`: API key only (for read operations)

**Recommendation:** Create unified factory functions:
- `get_youtube_service_oauth()` - For authenticated operations
- `get_youtube_service_api_key()` - For public read operations

---

## 2. Video Upload Error Handling

### Current Implementation

**File:** `modules/youtube_unit.py` (lines 50-56)

```python
media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
response = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
).execute()
```

### Issues Found

#### CRITICAL-4: No Upload Validation or Confirmation

**Problem:** Upload success is assumed if `.execute()` returns without exception. No verification that:
- Video processing completed successfully
- Video wasn't flagged by YouTube's automated checks
- Upload fully committed to YouTube

**Recommended Fix:**
```python
response = youtube.videos().insert(...).execute()
video_id = response.get('id')

if not video_id:
    print("ERROR: Upload returned no video ID!")
    return None

# Wait for processing status (optional but recommended)
status = response.get('status', {})
upload_status = status.get('uploadStatus')

if upload_status != 'uploaded':
    print(f"WARNING: Upload status is '{upload_status}', not 'uploaded'")
```

#### HIGH-5: No Retry Logic for Transient Failures

**Problem:** YouTube API can return transient errors (rate limits, server errors). Current code fails immediately.

**Common Retryable Errors:**
- `503 Service Unavailable`
- `500 Internal Server Error`
- `403 Rate Limit Exceeded` (with backoff)
- Network timeouts

**Current Behavior:** Single attempt, then failure.

**Recommended Fix:**
```python
import time
from googleapiclient.errors import HttpError

def upload_with_retry(youtube, body, media, max_retries=3):
    """Upload video with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            ).execute()
            return response
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                wait_time = (2 ** attempt) + (random.random())
                print(f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            elif e.resp.status == 403:
                # Check if rate limit
                if 'quotaExceeded' in str(e):
                    print("CRITICAL: YouTube quota exceeded!")
                    raise
                wait_time = (2 ** attempt) * 5
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Upload failed after {max_retries} retries")
```

#### HIGH-6: Resumable Upload Not Fully Utilized

**Problem:** Code sets `resumable=True` but doesn't implement resumption on failure.

**Current:** Uses `-1` chunksize (single chunk upload) which defeats resumable purpose.

```python
media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
```

**Recommendation:** For large videos, use chunked upload with progress tracking:
```python
# For files > 5MB, use chunked upload
media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Upload progress: {int(status.progress() * 100)}%")
```

#### MEDIUM-7: No File Existence Check Before Upload

**Problem:** `MediaFileUpload` is called with `file_path` without verifying the file exists.

**Current Flow (main.py):**
```python
video_file = create_video(hook, title, "minimalist psychology")
if not video_file:
    print("Video creation failed")
    return
# No check if video_file actually exists on disk
video_id = deploy_to_youtube(video_file, title, guide)
```

**Fix:**
```python
# In youtube_unit.py
if not os.path.exists(file_path):
    print(f"ERROR: Video file not found: {file_path}")
    return None

file_size = os.path.getsize(file_path)
if file_size == 0:
    print("ERROR: Video file is empty!")
    return None
```

---

## 3. Auto-Comment Posting Reliability

### Current Implementation

**File:** `modules/youtube_unit.py` (lines 62-78)

```python
try:
    youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": f"Get Started with Protocol #001: {GUMROAD_LINK}"
                    }
                }
            }
        }
    ).execute()
    print("Auto-comment posted!")
except Exception as comment_error:
    print(f"Comment failed (non-critical): {comment_error}")
```

### Issues Found

#### HIGH-8: No Distinction Between Error Types

**Problem:** All comment failures are treated equally as "non-critical", but some indicate serious issues:

| Error | Severity | Action Required |
|-------|----------|-----------------|
| Comments disabled | Expected | Log and continue |
| Quota exceeded | CRITICAL | Stop all operations |
| Spam detected | HIGH | Review comment text |
| Channel suspended | CRITICAL | Alert immediately |

**Recommended Fix:**
```python
from googleapiclient.errors import HttpError

try:
    youtube.commentThreads().insert(...).execute()
    print("Auto-comment posted!")
except HttpError as e:
    error_content = e.content.decode() if hasattr(e, 'content') else str(e)

    if e.resp.status == 403:
        if 'commentsDisabled' in error_content:
            print("INFO: Comments disabled on this video")
        elif 'quotaExceeded' in error_content:
            print("CRITICAL: API quota exceeded!")
        elif 'forbidden' in error_content.lower():
            print("WARNING: Comment forbidden - may be spam filtered")
    elif e.resp.status == 404:
        print("ERROR: Video not found for commenting (upload may have failed)")
    else:
        print(f"Comment error ({e.resp.status}): {error_content[:200]}")
except Exception as e:
    print(f"Unexpected comment error: {e}")
```

#### MEDIUM-9: No Comment Delay After Upload

**Problem:** Comment is posted immediately after upload. YouTube may not have finished processing the video, leading to `404 Video not found` errors.

**Recommendation:** Add brief delay or verify video exists before commenting:
```python
# Wait for video to be available
import time
time.sleep(5)  # Brief delay for YouTube processing

# Or better: verify video exists
try:
    youtube.videos().list(part="id", id=video_id).execute()
except HttpError as e:
    if e.resp.status == 404:
        print("Video not yet available, retrying comment later...")
```

#### LOW-10: Hardcoded Comment Text

**Problem:** Comment text is hardcoded in the function. Should be configurable.

```python
f"Get Started with Protocol #001: {GUMROAD_LINK}"
```

**Recommendation:** Move to config or accept as parameter:
```python
def deploy_to_youtube(file_path, title, guide, comment_text=None):
    comment_text = comment_text or f"Get Started with Protocol #001: {GUMROAD_LINK}"
```

---

## 4. Shorts-Specific Metadata

### Current Implementation

**File:** `modules/youtube_unit.py` (lines 38-48)

```python
body = {
    "snippet": {
        "title": title,
        "description": full_desc,
        "categoryId": "27"  # Education
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False
    }
}
```

### Issues Found

#### MEDIUM-11: Missing Shorts-Specific Metadata

**Problem:** YouTube Shorts have specific requirements and metadata options not being used:

| Field | Current | Recommended |
|-------|---------|-------------|
| `#Shorts` in title/description | Not enforced | Add automatically |
| Category ID | 27 (Education) | Correct |
| Tags | Missing | Add relevant tags |
| Default language | Missing | Should set |

**Missing Shorts Detection:** YouTube identifies Shorts by:
1. Vertical aspect ratio (9:16)
2. Duration <= 60 seconds
3. `#Shorts` in title or description (helps discoverability)

**Video Lab Check (`video_lab.py`):**
```python
# Current dimensions
bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
# Results in 1080x1920 (9:16 aspect ratio) - CORRECT

duration = 8  # seconds - CORRECT (< 60)
```

**Recommendation:** Add Shorts optimization to upload:
```python
# Ensure #Shorts in title for better discoverability
if '#Shorts' not in title and '#shorts' not in title:
    title = f"{title} #Shorts" if len(title) < 90 else title

# Add recommended tags
body = {
    "snippet": {
        "title": title,
        "description": full_desc,
        "categoryId": "27",
        "tags": ["Shorts", "Psychology", "Brain", "TheBrainLab", "Facts"],
        "defaultLanguage": "en"
    },
    ...
}
```

#### LOW-12: No Duration Validation Before Upload

**Problem:** No validation that video is actually under 60 seconds before upload.

**Recommendation:**
```python
from moviepy.editor import VideoFileClip

def validate_shorts_requirements(file_path):
    """Validate video meets YouTube Shorts requirements."""
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        width, height = clip.size
        clip.close()

        issues = []

        if duration > 60:
            issues.append(f"Duration {duration}s exceeds 60s limit")

        if width > height:
            issues.append(f"Horizontal video ({width}x{height}), Shorts require vertical")

        aspect_ratio = height / width
        if aspect_ratio < 1.5 or aspect_ratio > 2.0:
            issues.append(f"Aspect ratio {aspect_ratio:.2f} should be ~1.78 (9:16)")

        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Validation error: {e}"]
```

---

## 5. Retry Logic Improvements

### Current State Analysis

| Operation | Current Retry | Recommended |
|-----------|---------------|-------------|
| OAuth refresh | None | 2 retries with backoff |
| Video upload | None | 3 retries with exponential backoff |
| Comment posting | None | 2 retries, 5s delay |
| Statistics fetch | None | 3 retries |

### HIGH-13: Missing Global Error Handling Strategy

**Problem:** Each module handles errors differently:
- `youtube_unit.py`: Generic except with traceback
- `sync_youtube.py`: Streamlit error display
- `shorts_analytics.py`: Print and return empty

**Recommendation:** Create unified error handling:

```python
# modules/youtube_errors.py

from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import time
import random

class YouTubeError(Exception):
    """Base exception for YouTube operations."""
    pass

class QuotaExceededError(YouTubeError):
    """Daily API quota exceeded."""
    pass

class AuthenticationError(YouTubeError):
    """OAuth authentication failed."""
    pass

class RateLimitError(YouTubeError):
    """Temporary rate limit, should retry."""
    pass

def handle_http_error(e: HttpError):
    """Convert HttpError to specific exception type."""
    status = e.resp.status
    content = e.content.decode() if hasattr(e, 'content') else ''

    if status == 403:
        if 'quotaExceeded' in content:
            raise QuotaExceededError("Daily API quota exceeded")
        elif 'rateLimitExceeded' in content:
            raise RateLimitError("Rate limit exceeded")
    elif status == 401:
        raise AuthenticationError("Invalid or expired credentials")
    elif status in [500, 502, 503, 504]:
        raise RateLimitError(f"Server error: {status}")

    raise YouTubeError(f"HTTP {status}: {content[:200]}")

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Execute function with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
            print(f"Rate limited, retrying in {delay:.1f}s...")
            time.sleep(delay)
        except (QuotaExceededError, AuthenticationError):
            raise  # Don't retry these
    raise YouTubeError(f"Operation failed after {max_retries} retries")
```

### HIGH-14: No Timeout Configuration

**Problem:** API calls can hang indefinitely with no timeout.

**Affected Operations:**
- `youtube.videos().insert()` - Large file upload
- `youtube.commentThreads().insert()` - Comment posting
- `youtube.channels().list()` - Channel lookup

**Recommendation:** Set socket timeout:
```python
import socket

# Set default timeout for all socket operations
socket.setdefaulttimeout(60)  # 60 seconds

# Or per-request using httplib2
import httplib2
http = httplib2.Http(timeout=60)
youtube = build('youtube', 'v3', credentials=creds, http=http)
```

---

## Summary of Recommendations

### Immediate Fixes (< 1 hour)

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| 1 | No refresh token error handling | Add RefreshError catch | 15 min |
| 7 | No file existence check | Add os.path.exists | 5 min |
| 10 | Hardcoded comment text | Move to config | 10 min |
| 11 | Missing #Shorts tag | Add automatic tagging | 10 min |

### Short-term Improvements (1-4 hours)

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| 5 | No upload retry logic | Implement backoff retry | 2 hours |
| 8 | Generic comment error handling | Add error type detection | 1 hour |
| 13 | No unified error strategy | Create error module | 2 hours |
| 14 | No timeout configuration | Add socket timeouts | 30 min |

### Long-term Improvements (1+ days)

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| 4 | No upload validation | Add status verification | 4 hours |
| 6 | Resumable upload underused | Implement chunked upload | 1 day |
| 12 | No pre-upload validation | Create validator function | 2 hours |

---

## Architecture Recommendation

```
+------------------+     +-------------------+     +------------------+
|   main.py        | --> | youtube_service   | --> | YouTube API      |
|                  |     | (new unified)     |     |                  |
+------------------+     +-------------------+     +------------------+
                               |
                    +----------+----------+
                    |                     |
            +-------v--------+    +-------v--------+
            | upload_manager |    | analytics_mgr  |
            | - OAuth2 auth  |    | - API key auth |
            | - Retry logic  |    | - Caching      |
            | - Validation   |    | - Batching     |
            +----------------+    +----------------+
```

---

## Files Analyzed

- `modules/youtube_unit.py` - Video upload and commenting
- `modules/shorts_analytics.py` - Shorts data fetching
- `sync_youtube.py` - YouTube sync for dashboard
- `modules/config.py` - Credentials configuration
- `modules/video_lab.py` - Video creation (aspect ratio check)
- `main.py` - Main pipeline integration

---

**Report Generated:** 2026-01-29
**Analyst:** Claude Code (Opus 4.5)
**Project:** The Brain Lab Bot - YouTube Integration Audit
