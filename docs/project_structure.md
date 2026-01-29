# Project Structure & Code Mapping - The Brain Lab Bot

**Audit Date:** 2026-01-29
**Auditor:** Claude Code

---

## 1. Project Overview

The Brain Lab is an automated YouTube Shorts creation pipeline that:
1. Generates viral psychology/neuroscience content using AI (Gemini)
2. Creates video content with text overlays and background images
3. Uploads to YouTube with SEO-optimized titles and auto-comments
4. Tracks performance with SQLite database
5. Provides analytics dashboards for optimization

---

## 2. File Structure & Dependencies

```
the-brain-lab-official/
├── main.py                    # Main video creation pipeline
├── dashboard.py               # Streamlit control center (original)
├── dashboard_shorts.py        # Conversion analytics dashboard
├── init_demo_data.py          # Demo data generator for testing
├── sync_youtube.py            # YouTube data synchronization
├── winning_hooks.py           # Proven hooks library (30 hooks)
│
├── modules/
│   ├── config.py              # Centralized secrets/configuration
│   ├── database.py            # SQLite database operations
│   ├── ai_brain.py            # Gemini AI content generation
│   ├── video_lab.py           # MoviePy video creation
│   ├── youtube_unit.py        # YouTube OAuth upload/comments
│   ├── analytics.py           # Performance insights engine
│   ├── shorts_analytics.py    # YouTube Shorts-specific analytics
│   ├── gumroad_tracker.py     # Gumroad sales tracking
│   ├── hook_analyzer.py       # AI hook pattern analysis
│   └── content_suggester.py   # AI content idea generator
│
├── reports/
│   └── weekly_summary.py      # Weekly report generator
│
└── docs/
    ├── code_audit.md          # Initial code audit
    └── project_structure.md   # This document
```

---

## 3. Core Module Breakdown

### 3.1 Main Pipeline (`main.py`)

**Purpose:** Orchestrates the video creation workflow

**Dependencies:**
- `modules.config.SECRETS`
- `modules.ai_brain.get_viral_content`
- `modules.video_lab.create_video`
- `modules.youtube_unit.deploy_to_youtube`
- `modules.database.init_database, save_video`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `run_lab_mission()` | Main orchestrator - generates content, creates video, uploads, saves to DB |
| `identify_domain()` | Classifies content by topic using keyword matching |

**Data Flow:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  AI Brain   │───>│  Video Lab  │───>│ YouTube Unit│───>│  Database   │
│(get_viral   │    │(create_video│    │(deploy_to   │    │(save_video) │
│ content)    │    │)            │    │ youtube)    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                   │                  │
   hook,title         MP4 file           video_id           record
   guide                                                    saved
```

---

### 3.2 AI Brain (`modules/ai_brain.py`)

**Purpose:** Generates viral psychology content using Gemini AI

**Dependencies:**
- `google.genai` - Gemini AI client
- `modules.config.SECRETS`
- `winning_hooks.PROVEN_HOOKS, get_random_proven_hook`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `get_viral_content()` | Main entry - 80% proven hooks, 20% AI-generated |
| `parse_response()` | Parses AI response into hook/title/guide |
| `validate_new_rules()` | Validates content against proven formats |
| `get_proven_fallback()` | Returns hardcoded fallback hooks |

**Content Strategy:**
- 80% probability: Select from 30 proven hooks in `winning_hooks.py`
- 20% probability: AI generates new content with strict validation

**Validation Rules:**
1. Hook must start with: `BRAIN FACT:`, `PSYCHOLOGY FACT:`, or `SOCIAL INTELLIGENCE:`
2. Title must include `#TheBrainLab`
3. Title max 15 words
4. Guide max 3 sentences
5. Must include power words: brain, smart, intelligence, research, etc.

---

### 3.3 Video Lab (`modules/video_lab.py`)

**Purpose:** Creates MP4 video files with text overlay

**Dependencies:**
- `moviepy.editor` - Video processing
- `requests` - Unsplash API
- `modules.config.SECRETS`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `get_background_image()` | Fetches Unsplash image for topic |
| `create_video()` | Creates 8-second 1080x1920 video at 25 FPS |

**Video Specifications:**
- Resolution: 1080x1920 (9:16 vertical for Shorts)
- Duration: 8 seconds
- FPS: 25
- Codec: libx264
- Audio: AAC (from `Resolution - Wayne Jones.mp3`)
- Text: Arial-Bold, 65pt, white, centered

---

### 3.4 YouTube Unit (`modules/youtube_unit.py`)

**Purpose:** Handles YouTube OAuth upload and auto-comments

**Dependencies:**
- `google.oauth2.credentials`
- `googleapiclient.discovery`
- `modules.config.SECRETS, GUMROAD_LINK, OFFICIAL_DESCRIPTION`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `deploy_to_youtube()` | Uploads video, posts auto-comment with CTA |

**Features:**
- OAuth2 token refresh
- Resumable upload
- Category 27 (Education)
- Auto-comment with Gumroad link
- Description includes official branding + guide

---

### 3.5 Database (`modules/database.py`)

**Purpose:** SQLite database operations for video tracking

**Tables:**
```sql
videos (
    id INTEGER PRIMARY KEY,
    video_id TEXT UNIQUE NOT NULL,
    hook TEXT NOT NULL,
    title TEXT NOT NULL,
    guide TEXT,
    domain TEXT,
    created_at TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    last_updated TIMESTAMP
)

performance_history (
    id INTEGER PRIMARY KEY,
    video_id TEXT FOREIGN KEY,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    recorded_at TIMESTAMP
)

insights (
    id INTEGER PRIMARY KEY,
    insight_type TEXT,
    insight_text TEXT,
    confidence_score REAL,
    created_at TIMESTAMP
)
```

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `init_database()` | Creates tables if not exist |
| `save_video()` | Saves new video record |
| `update_video_stats()` | Updates views/likes/comments |
| `get_all_videos()` | Returns all videos for dashboard |
| `get_top_performers()` | Returns top N by views |
| `get_domain_performance()` | Aggregates by domain |
| `get_statistics()` | Returns summary stats |
| `get_performance_timeline()` | Returns daily views data |

---

### 3.6 Configuration (`modules/config.py`)

**Purpose:** Centralized secrets and constants

**Environment Variables:**
- `GEMINI_API_KEY` - Google Gemini AI
- `UNSPLASH_ACCESS_KEY` - Background images
- `GOOGLE_CLIENT_ID` - YouTube OAuth
- `GOOGLE_CLIENT_SECRET` - YouTube OAuth
- `YOUTUBE_REFRESH_TOKEN` - YouTube OAuth
- `TIKTOK_CLIENT_KEY` - (Reserved for future)
- `TIKTOK_CLIENT_SECRET` - (Reserved for future)

**Constants:**
- `GUMROAD_LINK` - Product URL
- `OFFICIAL_DESCRIPTION` - YouTube description template

---

### 3.7 Analytics (`modules/analytics.py`)

**Purpose:** Generates insights from video performance data

**Dependencies:**
- `modules.database`
- `statistics`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `analyze_hook_patterns()` | Identifies winning hook characteristics |
| `analyze_domain_performance()` | Compares domain effectiveness |
| `analyze_recent_performance()` | Detects performance trends |
| `get_all_insights()` | Aggregates all insights |
| `calculate_virality_score()` | Calculates normalized virality score |
| `get_performance_summary()` | Returns comprehensive summary |

---

### 3.8 Shorts Analytics (`modules/shorts_analytics.py`)

**Purpose:** YouTube Shorts-specific analytics via YouTube Data API

**Dependencies:**
- `googleapiclient.discovery`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `get_youtube_service()` | Creates API connection |
| `get_channel_uploads_playlist()` | Gets uploads playlist ID |
| `fetch_shorts()` | Fetches Shorts (videos ≤60s) with stats |
| `parse_duration()` | Parses ISO 8601 duration |
| `get_shorts_analytics()` | Main entry - returns shorts + summary |

---

### 3.9 Gumroad Tracker (`modules/gumroad_tracker.py`)

**Purpose:** Tracks Gumroad sales with YouTube attribution

**Dependencies:**
- `requests`

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `fetch_sales()` | Fetches sales with filters |
| `fetch_all_sales()` | Handles pagination |
| `parse_sale()` | Standardizes sale format |
| `extract_youtube_referrals()` | Filters YouTube-attributed sales |
| `extract_video_id_from_referrer()` | Extracts video ID from URL |
| `match_sales_to_shorts()` | Links sales to specific Shorts |
| `get_referrer_breakdown()` | Analyzes traffic sources |

---

### 3.10 Hook Analyzer (`modules/hook_analyzer.py`)

**Purpose:** AI-powered hook pattern analysis with conversion correlation

**Dependencies:**
- `google.genai` - Gemini AI
- `modules.shorts_analytics`
- `modules.gumroad_tracker`

**Hook Categories:**
- BRAIN FACT
- PSYCHOLOGY FACT
- SOCIAL INTELLIGENCE
- BODY LANGUAGE
- DARK PSYCHOLOGY
- PERFORMANCE
- OTHER

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `categorize_hook_by_rules()` | Rule-based categorization |
| `analyze_hooks_with_gemini()` | AI-powered batch analysis |
| `calculate_category_performance()` | Aggregates metrics per category |
| `correlate_hooks_with_conversions()` | Main entry - full analysis |
| `generate_hook_insights()` | Generates actionable insights |

---

### 3.11 Content Suggester (`modules/content_suggester.py`)

**Purpose:** AI-generated content ideas based on performance data

**Dependencies:**
- `google.genai` - Gemini AI
- All analytics modules

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `analyze_top_performers()` | Identifies success patterns |
| `extract_title_patterns()` | Finds common patterns (prefixes, words) |
| `generate_content_ideas_with_gemini()` | AI-powered idea generation |
| `validate_content_idea()` | Validates against rules |
| `generate_fallback_ideas()` | Rule-based fallback (7 ideas) |
| `save_suggestions_to_markdown()` | Exports to `suggestions.md` |

---

### 3.12 Weekly Summary (`reports/weekly_summary.py`)

**Purpose:** Generates comprehensive weekly performance reports

**Dependencies:**
- All analytics modules

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `compile_weekly_stats()` | Aggregates all metrics for period |
| `generate_markdown_report()` | Creates markdown report |
| `generate_insights()` | Creates actionable insights |
| `print_weekly_report()` | Console-formatted report |

---

## 4. Data Flow Diagram

```
                                CONTENT CREATION PIPELINE
                                ========================

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐   │
│  │  winning_hooks   │ 80% │                  │     │                  │   │
│  │  (30 proven)     │────>│    AI Brain      │────>│   Video Lab      │   │
│  └──────────────────┘     │  (get_viral_     │     │  (create_video)  │   │
│                           │   content)       │     │                  │   │
│  ┌──────────────────┐ 20% │                  │     └────────┬─────────┘   │
│  │  Gemini AI       │────>│                  │              │             │
│  │  (generate new)  │     └──────────────────┘              │             │
│  └──────────────────┘                                       │             │
│                                                             v             │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐   │
│  │                  │     │                  │     │   YouTube Unit   │   │
│  │    Database      │<────│  main.py         │<────│  (deploy_to_     │   │
│  │  (save_video)    │     │  (run_lab_       │     │   youtube)       │   │
│  │                  │     │   mission)       │     │                  │   │
│  └──────────────────┘     └──────────────────┘     └──────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


                                ANALYTICS PIPELINE
                                ==================

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐   │
│  │  YouTube API     │────>│ shorts_analytics │────>│                  │   │
│  │  (channel data)  │     │ (fetch_shorts)   │     │  hook_analyzer   │   │
│  └──────────────────┘     └──────────────────┘     │  (correlate)     │   │
│                                    │               │                  │   │
│  ┌──────────────────┐     ┌────────v─────────┐     └────────┬─────────┘   │
│  │  Gumroad API     │────>│ gumroad_tracker  │              │             │
│  │  (sales data)    │     │ (match_sales_to_ │              v             │
│  └──────────────────┘     │  shorts)         │     ┌──────────────────┐   │
│                           └──────────────────┘     │content_suggester │   │
│                                                    │ (generate_ideas) │   │
│                                                    └────────┬─────────┘   │
│                                                             │             │
│  ┌──────────────────┐     ┌──────────────────┐              │             │
│  │  dashboard_      │<────│  weekly_summary  │<─────────────┘             │
│  │  shorts.py       │     │  (compile_stats) │                            │
│  └──────────────────┘     └──────────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Duplicate Code & Redundancies Identified

### 5.1 Gemini Client Creation
**Files:** `ai_brain.py`, `hook_analyzer.py`, `content_suggester.py`
**Issue:** Each file creates its own Gemini client with similar code
**Recommendation:** Create shared `get_gemini_client()` in `config.py` or new `utils.py`

### 5.2 YouTube API Connection
**Files:** `sync_youtube.py`, `shorts_analytics.py`
**Issue:** Both create YouTube API connections separately
**Note:** Different auth methods (Streamlit secrets vs env vars) - may be intentional

### 5.3 Hook Categorization
**Files:** `main.py:identify_domain()`, `hook_analyzer.py:categorize_hook_by_rules()`
**Issue:** Similar keyword-based classification logic
**Recommendation:** Consolidate into single function in `analytics.py` or `hook_analyzer.py`

### 5.4 Date Range Calculation
**Files:** `shorts_analytics.py`, `gumroad_tracker.py`, `weekly_summary.py`
**Issue:** Similar date threshold calculation
**Recommendation:** Create shared utility function

### 5.5 Module Overlap
**Observation:** `modules/analytics.py` (older) and `modules/hook_analyzer.py` (newer) have overlapping functionality
**Recommendation:** Consider consolidating or clearly separating concerns

---

## 6. External Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| google-genai | - | Gemini AI content generation |
| moviepy | - | Video creation |
| requests | - | HTTP requests (Unsplash, Gumroad) |
| google-oauth2 | - | YouTube OAuth |
| google-api-python-client | - | YouTube/Google APIs |
| streamlit | - | Dashboard UI |
| pandas | - | Data manipulation |
| plotly | - | Charts/graphs |
| python-dotenv | - | Environment variables |
| sqlite3 | stdlib | Database |

---

## 7. Environment Variables Required

| Variable | Required For |
|----------|--------------|
| `GEMINI_API_KEY` | AI content generation |
| `UNSPLASH_ACCESS_KEY` | Background images |
| `GOOGLE_CLIENT_ID` | YouTube OAuth |
| `GOOGLE_CLIENT_SECRET` | YouTube OAuth |
| `YOUTUBE_REFRESH_TOKEN` | YouTube OAuth |
| `YOUTUBE_API_KEY` | YouTube Data API (read-only) |
| `CHANNEL_ID` | YouTube channel identifier |
| `GUMROAD_ACCESS_TOKEN` | Gumroad sales API |

---

## 8. Entry Points Summary

| Script | Purpose | Usage |
|--------|---------|-------|
| `main.py` | Create and upload video | `python main.py` |
| `dashboard.py` | Streamlit dashboard | `streamlit run dashboard.py` |
| `dashboard_shorts.py` | Conversion dashboard | `python dashboard_shorts.py [days] [--csv]` |
| `sync_youtube.py` | Sync YT data | Via dashboard |
| `init_demo_data.py` | Create test data | `python init_demo_data.py` |
| `modules/shorts_analytics.py` | YT Shorts stats | `python modules/shorts_analytics.py` |
| `modules/gumroad_tracker.py` | Gumroad sales | `python modules/gumroad_tracker.py [days]` |
| `modules/hook_analyzer.py` | Hook analysis | `python modules/hook_analyzer.py [days]` |
| `modules/content_suggester.py` | Content ideas | `python modules/content_suggester.py [days] [--ideas=N]` |
| `reports/weekly_summary.py` | Weekly report | `python reports/weekly_summary.py [days] [--markdown]` |

---

*This documentation was generated as part of Story 1: Project Structure & Code Mapping*
