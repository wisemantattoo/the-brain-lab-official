# Performance Optimization Report - The Brain Lab

**Generated:** 2026-01-29
**Scope:** Video creation speed, API efficiency, caching, parallel processing

---

## Executive Summary

This report identifies performance bottlenecks in The Brain Lab codebase and provides actionable optimization recommendations. The analysis covers:

1. **Video Creation Pipeline** (MoviePy operations)
2. **API Call Efficiency** (Gemini, YouTube, Unsplash, Gumroad)
3. **Image Download & Processing**
4. **Caching Opportunities**
5. **Async/Parallel Processing Improvements**

**Priority Matrix:**
| Impact | Effort | Recommendations |
|--------|--------|-----------------|
| HIGH | LOW | Image caching, API response caching |
| HIGH | MEDIUM | Async API calls, batch processing |
| MEDIUM | MEDIUM | Video encoding optimization |
| MEDIUM | HIGH | Full async pipeline |

---

## 1. Video Creation Speed Analysis

### Current Implementation (`modules/video_lab.py`)

```python
# Lines 18-41
def create_video(insight, title, topic):
    fps = 25
    duration = 8

    bg_file = get_background_image(topic)  # Blocking HTTP call
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)

    txt = TextClip(insight, fontsize=65, ...)
    video = CompositeVideoClip([bg, txt])
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
```

### Performance Issues Identified

#### Issue 1.1: No FFmpeg Optimization Flags
**Location:** `video_lab.py:40`
**Impact:** HIGH
**Current State:** Default encoding settings used

```python
video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
```

**Recommendation:** Add FFmpeg preset and tune parameters:

```python
video.write_videofile(
    output,
    fps=fps,
    codec="libx264",
    audio_codec="aac",
    preset="ultrafast",      # 5-10x faster encoding
    ffmpeg_params=[
        "-tune", "fastdecode",
        "-crf", "23",        # Quality vs speed tradeoff
        "-threads", "4"      # Multi-threaded encoding
    ]
)
```

**Expected Improvement:** 5-10x faster video encoding

---

#### Issue 1.2: Synchronous Image Download Inside Video Creation
**Location:** `video_lab.py:6-16`
**Impact:** HIGH
**Current State:** Blocking HTTP request in video pipeline

```python
def get_background_image(query):
    res = requests.get(url).json()       # Blocking
    requests.get(img_url).content        # Another blocking call
```

**Recommendation:** Download image before video creation or use async:

```python
import aiohttp
import asyncio

async def get_background_image_async(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
        async with session.get(data['urls']['regular']) as resp:
            content = await resp.read()
    return content
```

**Expected Improvement:** 1-3 seconds saved per video

---

#### Issue 1.3: Full-Size Image Download
**Location:** `video_lab.py:11`
**Impact:** MEDIUM
**Current State:** Downloads 'regular' size (1080px width)

```python
img_url = res['urls']['regular']  # 1080px width
```

**Recommendation:** Use smaller size for faster download:

```python
# Unsplash provides multiple sizes
img_url = res['urls']['small']  # 400px - faster but may need upscaling
# OR
img_url = f"{res['urls']['raw']}&w=1080&h=1920&fit=crop"  # Exact size needed
```

**Expected Improvement:** 30-50% faster image download

---

#### Issue 1.4: No Resource Cleanup
**Location:** `video_lab.py:18-41`
**Impact:** MEDIUM (memory leaks)
**Current State:** Clips not explicitly closed

**Recommendation:**

```python
def create_video(insight, title, topic):
    try:
        bg_file = get_background_image(topic)
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        txt = TextClip(insight, fontsize=65, ...)
        video = CompositeVideoClip([bg, txt])
        video.write_videofile(output, ...)
        return output
    finally:
        # Clean up MoviePy resources
        if 'video' in locals(): video.close()
        if 'bg' in locals(): bg.close()
        if 'txt' in locals(): txt.close()
        if bg_file and os.path.exists("bg.jpg"):
            os.remove("bg.jpg")  # Remove temp file
```

---

## 2. Unnecessary API Calls

### Issue 2.1: Duplicate Gemini Client Creation
**Locations:**
- `ai_brain.py:35`
- `hook_analyzer.py:109`
- `content_suggester.py:41`

**Impact:** LOW (initialization overhead)
**Current State:** Each module creates its own client

```python
# ai_brain.py:35
client = genai.Client(api_key=SECRETS["GEMINI_API_KEY"])

# hook_analyzer.py:109
client = genai.Client(api_key=api_key)

# content_suggester.py:41
client = genai.Client(api_key=api_key)
```

**Recommendation:** Create shared utility module:

```python
# modules/api_clients.py
from functools import lru_cache
from google import genai

@lru_cache(maxsize=1)
def get_gemini_client(api_key=None):
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)
```

---

### Issue 2.2: Duplicate YouTube API Connection
**Locations:**
- `sync_youtube.py`
- `shorts_analytics.py:22-31`

**Impact:** LOW
**Current State:** Two different YouTube connection patterns

**Recommendation:** Unify in `api_clients.py`:

```python
@lru_cache(maxsize=1)
def get_youtube_service(api_key=None):
    api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
    return build('youtube', 'v3', developerKey=api_key)
```

---

### Issue 2.3: Repeated Analytics Fetching
**Location:** Multiple modules call same APIs repeatedly
**Impact:** HIGH

When running the full analytics pipeline:
1. `weekly_summary.py` calls `get_shorts_analytics()`
2. `hook_analyzer.py` calls `get_shorts_analytics()` again
3. `content_suggester.py` calls `get_shorts_analytics()` again

**Recommendation:** Implement data sharing layer:

```python
# modules/analytics_cache.py
from functools import lru_cache
from datetime import datetime, timedelta

_cache = {}
_cache_time = {}

def get_cached_shorts(channel_id, days, cache_minutes=10):
    cache_key = f"{channel_id}:{days}"

    if cache_key in _cache:
        if datetime.now() - _cache_time[cache_key] < timedelta(minutes=cache_minutes):
            return _cache[cache_key]

    result = get_shorts_analytics(channel_id=channel_id, days=days)
    _cache[cache_key] = result
    _cache_time[cache_key] = datetime.now()
    return result
```

**Expected Improvement:** 2-3x faster for multi-module pipelines

---

## 3. Image Download & Processing Efficiency

### Issue 3.1: No Image Caching
**Location:** `video_lab.py:6-16`
**Impact:** HIGH
**Current State:** Downloads new image every video

**Recommendation:** Implement disk-based image cache:

```python
import hashlib
import os

CACHE_DIR = ".image_cache"

def get_cached_background(query):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_key = hashlib.md5(query.encode()).hexdigest()
    cache_path = f"{CACHE_DIR}/{cache_key}.jpg"

    # Check cache first
    if os.path.exists(cache_path):
        cache_age = time.time() - os.path.getmtime(cache_path)
        if cache_age < 86400:  # 24 hours
            return cache_path

    # Download and cache
    img_content = download_from_unsplash(query)
    if img_content:
        with open(cache_path, 'wb') as f:
            f.write(img_content)
        return cache_path

    return None
```

**Expected Improvement:** 1-3 seconds saved per cached video

---

### Issue 3.2: Synchronous Image Processing
**Location:** `video_lab.py:26-27`
**Impact:** MEDIUM

```python
bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
```

**Recommendation:** Pre-process images using Pillow (faster than MoviePy):

```python
from PIL import Image

def preprocess_background(img_path, output_path="processed_bg.jpg"):
    with Image.open(img_path) as img:
        # Resize maintaining aspect
        aspect = img.width / img.height
        target_height = 1920
        target_width = int(target_height * aspect)
        img = img.resize((target_width, target_height), Image.LANCZOS)

        # Center crop to 1080x1920
        left = (target_width - 1080) // 2
        img = img.crop((left, 0, left + 1080, 1920))

        img.save(output_path, quality=85)
    return output_path
```

---

### Issue 3.3: No Timeout on Image Download
**Location:** `video_lab.py:10`
**Impact:** CRITICAL (can hang indefinitely)

```python
res = requests.get(url).json()  # No timeout!
```

**Recommendation:**

```python
res = requests.get(url, timeout=10).json()
img_content = requests.get(img_url, timeout=30).content
```

---

## 4. Caching Opportunities

### 4.1 AI Response Caching
**Location:** `ai_brain.py`
**Impact:** HIGH
**Opportunity:** Cache AI responses for similar prompts

```python
import hashlib
import json
import os

CACHE_DIR = ".ai_cache"

def get_cached_ai_response(prompt, max_age_hours=24):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    cache_path = f"{CACHE_DIR}/{cache_key}.json"

    if os.path.exists(cache_path):
        cache_age = time.time() - os.path.getmtime(cache_path)
        if cache_age < max_age_hours * 3600:
            with open(cache_path) as f:
                return json.load(f)
    return None

def save_ai_response(prompt, response):
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    cache_path = f"{CACHE_DIR}/{cache_key}.json"
    with open(cache_path, 'w') as f:
        json.dump(response, f)
```

---

### 4.2 YouTube Data Caching
**Location:** `shorts_analytics.py`
**Impact:** MEDIUM
**Opportunity:** Cache API responses for 10-15 minutes

```python
from functools import lru_cache
from datetime import datetime

@lru_cache(maxsize=128)
def fetch_shorts_cached(channel_id: str, days: int, cache_time: str):
    """
    cache_time should be rounded to 15-min intervals for effective caching
    e.g., cache_time = datetime.now().strftime('%Y%m%d%H') + str(datetime.now().minute // 15)
    """
    return fetch_shorts(youtube, channel_id, days)
```

---

### 4.3 Gumroad Sales Caching
**Location:** `gumroad_tracker.py`
**Impact:** MEDIUM
**Opportunity:** Sales data doesn't change frequently

```python
# Add 5-minute cache for sales data
# Especially useful when running multiple reports

SALES_CACHE = {}
SALES_CACHE_TIME = None

def get_cached_sales(days, cache_minutes=5):
    global SALES_CACHE, SALES_CACHE_TIME

    if SALES_CACHE_TIME and (datetime.now() - SALES_CACHE_TIME).seconds < cache_minutes * 60:
        if days in SALES_CACHE:
            return SALES_CACHE[days]

    result = fetch_all_sales(days=days)
    SALES_CACHE[days] = result
    SALES_CACHE_TIME = datetime.now()
    return result
```

---

### 4.4 Hook Category Caching
**Location:** `hook_analyzer.py:58-88`
**Impact:** LOW
**Opportunity:** Rule-based categorization can be memoized

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def categorize_hook_by_rules(title: str) -> str:
    # ... existing implementation
```

---

## 5. Async/Parallel Processing Improvements

### 5.1 Parallel API Calls in Analytics Pipeline
**Location:** `hook_analyzer.py:304-346`, `content_suggester.py:508-619`
**Impact:** HIGH
**Current State:** Sequential API calls

```python
# Current (sequential)
youtube_result = get_shorts_analytics(...)  # Wait
sales_result = get_sales_analytics(...)      # Wait again
```

**Recommendation:** Use asyncio for parallel fetching:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_all_data_parallel(channel_id, days):
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=3) as executor:
        youtube_future = loop.run_in_executor(
            executor,
            lambda: get_shorts_analytics(channel_id=channel_id, days=days)
        )
        sales_future = loop.run_in_executor(
            executor,
            lambda: get_sales_analytics(days=days)
        )

        youtube_result, sales_result = await asyncio.gather(
            youtube_future,
            sales_future
        )

    return youtube_result, sales_result
```

**Expected Improvement:** 40-50% faster data fetching

---

### 5.2 Batch YouTube API Requests
**Location:** `shorts_analytics.py:159-165`
**Impact:** MEDIUM
**Current State:** Already batching (good!)

```python
# Already batching in groups of 50 (API limit)
for i in range(0, len(video_ids), 50):
    batch_ids = video_ids[i:i+50]
    details_response = youtube.videos().list(
        part='contentDetails,statistics,snippet',
        id=','.join(batch_ids)
    ).execute()
```

**Status:** Well implemented. No changes needed.

---

### 5.3 Parallel Content Generation
**Location:** `content_suggester.py:145-284`
**Impact:** MEDIUM
**Opportunity:** Generate multiple ideas in parallel

```python
import asyncio

async def generate_ideas_parallel(num_ideas, context):
    """Generate multiple ideas concurrently"""
    tasks = []
    for i in range(num_ideas):
        task = generate_single_idea(context, variation=i)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
```

---

### 5.4 Background Video Processing
**Location:** `main.py:21-48`
**Impact:** HIGH
**Current State:** Synchronous pipeline

**Recommendation:** Use background tasks for non-blocking operation:

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

async def run_lab_mission_async():
    loop = asyncio.get_event_loop()

    # Generate content (fast)
    hook, title, guide = await loop.run_in_executor(None, get_viral_content)

    # Create video (slow - use process pool for CPU-bound work)
    with ProcessPoolExecutor() as pool:
        video_file = await loop.run_in_executor(
            pool,
            create_video,
            hook, title, "minimalist psychology"
        )

    # Upload (I/O bound)
    video_id = await loop.run_in_executor(None, deploy_to_youtube, video_file, title, guide)

    return video_id
```

---

## 6. Quick Wins Summary

### Immediate (< 30 min each)

| # | Optimization | File | Expected Gain |
|---|-------------|------|---------------|
| 1 | Add FFmpeg `preset="ultrafast"` | video_lab.py:40 | 5-10x encoding speed |
| 2 | Add request timeouts | video_lab.py:10 | Prevent hangs |
| 3 | Memoize `categorize_hook_by_rules` | hook_analyzer.py:58 | Minor CPU savings |
| 4 | Add `lru_cache` to API clients | All modules | Reduced overhead |

### Short-term (1-2 hours each)

| # | Optimization | Files | Expected Gain |
|---|-------------|-------|---------------|
| 5 | Implement image caching | video_lab.py | 1-3 sec/video |
| 6 | Create shared api_clients.py | New file | Code consolidation |
| 7 | Add in-memory API response cache | Analytics modules | 2-3x faster pipelines |
| 8 | Use Pillow for image preprocessing | video_lab.py | Faster processing |

### Medium-term (4+ hours)

| # | Optimization | Files | Expected Gain |
|---|-------------|-------|---------------|
| 9 | Async parallel API fetching | hook_analyzer, content_suggester | 40-50% faster |
| 10 | Background video processing | main.py | Non-blocking operation |
| 11 | Full async pipeline | All modules | Maximum throughput |

---

## 7. Performance Monitoring Recommendations

### Add Timing Decorators

```python
import time
import functools

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[PERF] {func.__name__}: {elapsed:.2f}s")
        return result
    return wrapper

# Usage
@timing_decorator
def create_video(insight, title, topic):
    ...
```

### Track Key Metrics

```python
# Add to each major operation
import logging

performance_logger = logging.getLogger('performance')

def log_performance(operation, duration, success=True):
    performance_logger.info(f"{operation},{duration:.3f},{success}")
```

---

## 8. Benchmark Targets

| Operation | Current (est.) | Target | Method |
|-----------|---------------|--------|--------|
| Video creation | 30-60s | 10-20s | FFmpeg optimization |
| Image download | 2-5s | <1s | Caching |
| AI content generation | 3-5s | 3-5s | Already optimized |
| YouTube data fetch | 5-10s | 2-5s | Caching + parallel |
| Gumroad data fetch | 2-5s | 1-3s | Caching |
| Full analytics pipeline | 30-60s | 10-20s | All optimizations |

---

## Conclusion

The most impactful optimizations are:

1. **FFmpeg encoding optimization** - 5-10x faster video creation
2. **Image caching** - Eliminates redundant downloads
3. **Parallel API fetching** - 40-50% faster data pipelines
4. **Request timeouts** - Prevents system hangs

Implementation priority should follow the Quick Wins section, starting with FFmpeg optimization and image caching for immediate impact.

---

*Report generated by Claude Code - Performance Audit Module*
