# Code Audit Report - The Brain Lab

**Date:** 2026-01-25
**Auditor:** Claude Code (Iteration 1)

---

## Overview

The Brain Lab is an automated YouTube Shorts content creation and analytics system. It generates psychology-themed videos using AI, uploads them to YouTube, and tracks performance via a Streamlit dashboard.

---

## File-by-File Analysis

### Root Files

#### 1. `main.py`
**Purpose:** Main entry point for video creation pipeline
**Key Functions:**
- `run_lab_mission()` - Orchestrates the full workflow: generate content → create video → upload to YouTube → save to database
- `identify_domain(hook, title)` - Categorizes content by keywords into domains (Neuroscience, Body Language, Dark Psychology, etc.)

**Dependencies:** modules/config, ai_brain, video_lab, youtube_unit, database
**Reusable:** Yes - domain identification logic can be reused for Story 4 (Hook Pattern Analysis)

---

#### 2. `dashboard.py`
**Purpose:** Streamlit-based control center dashboard
**Key Features:**
- Overview page with metrics and charts (views over time, domain breakdown)
- Top performers page
- Domain analysis page
- AI insights page
- All videos database view
- YouTube sync page

**Dependencies:** streamlit, pandas, plotly, modules/database, modules/analytics, init_demo_data, sync_youtube
**Reusable:** Yes - chart/visualization patterns can be reused for Story 3 (Conversion Dashboard)

---

#### 3. `init_demo_data.py`
**Purpose:** Demo data generator for testing dashboard
**Key Functions:**
- `create_demo_videos()` - Creates 15 sample videos with realistic stats
- `check_if_demo_needed()` - Checks if database has < 5 videos

**Reusable:** Yes - pattern for generating test data

---

#### 4. `sync_youtube.py`
**Purpose:** Pulls real data from YouTube channel into database
**Key Functions:**
- `get_youtube_service()` - Connects to YouTube API (uses `st.secrets`)
- `get_channel_videos(youtube, channel_id, max_results)` - Fetches all videos from channel
- `get_video_statistics(youtube, video_ids)` - Gets views, likes, comments
- `extract_metadata(title, description, tags)` - Extracts hook and domain
- `sync_youtube_data()` - Main sync orchestration
- `delete_demo_data()` - Removes demo videos

**Dependencies:** streamlit, googleapiclient, modules/database
**Reusable:** **HIGH** - This is perfect for Story 1 (YouTube Shorts Analytics). Already connects to YouTube API and fetches video stats.

---

#### 5. `winning_hooks.py`
**Purpose:** Library of 30 proven hooks with titles and guides
**Key Data:**
- `PROVEN_HOOKS` - List of tuples: (hook, title, guide)
- `CATEGORIES` - Dict mapping category names to counts
- `get_random_proven_hook()` - Returns random hook

**Reusable:** Yes - data structure for categorizing content

---

### Modules Directory

#### 6. `modules/config.py`
**Purpose:** Configuration and secrets management
**Key Data:**
- `SECRETS` - Dict loading from environment variables (GEMINI_API_KEY, YOUTUBE credentials, UNSPLASH_KEY, TIKTOK credentials)
- `GUMROAD_LINK` - Product URL
- `OFFICIAL_DESCRIPTION` - Video description template

**Reusable:** **HIGH** - Central config pattern. Can add Gumroad API key here for Story 2.

---

#### 7. `modules/database.py`
**Purpose:** SQLite database operations
**Tables:**
- `videos` - Main video data (video_id, hook, title, guide, domain, views, likes, comments)
- `performance_history` - Historical snapshots for trends
- `insights` - AI-generated insights storage

**Key Functions:**
- `init_database()` - Creates tables
- `save_video()` - Insert new video
- `update_video_stats()` - Update views/likes/comments
- `get_all_videos()` - Fetch all videos
- `get_top_performers(limit)` - Get top N by views
- `get_domain_performance()` - Aggregate stats by domain
- `get_statistics()` - Overall stats
- `get_performance_timeline()` - Data for time-series charts

**Reusable:** **CRITICAL** - Foundation for all data storage. Will need new table for Gumroad sales in Story 2.

---

#### 8. `modules/analytics.py`
**Purpose:** Automated insights and pattern analysis
**Key Functions:**
- `analyze_hook_patterns()` - Analyzes hook length correlation with performance
- `analyze_domain_performance()` - Finds best/worst performing domains
- `analyze_recent_performance()` - Compares recent vs historical
- `analyze_posting_times()` - (TODO: needs timestamps)
- `get_all_insights()` - Aggregates all insights
- `calculate_virality_score()` - Engagement-based scoring
- `get_performance_summary()` - Comprehensive summary with trends

**Reusable:** **HIGH** - Directly applicable to Story 4 (Hook Pattern Analysis) and Story 6 (Weekly Report)

---

#### 9. `modules/ai_brain.py`
**Purpose:** AI content generation using Gemini
**Key Functions:**
- `get_viral_content()` - 80% proven hooks / 20% AI-generated
- `parse_response(full_text)` - Parses AI output
- `validate_new_rules(hook, guide, title)` - Quality checks
- `get_proven_fallback()` - Fallback to proven content

**Dependencies:** google.genai, modules/config, winning_hooks
**Reusable:** Yes - Gemini API integration pattern for Story 5 (AI Content Suggestions)

---

#### 10. `modules/video_lab.py`
**Purpose:** Video creation using MoviePy
**Key Functions:**
- `get_background_image(query)` - Fetches from Unsplash API
- `create_video(insight, title, topic)` - Creates MP4 with text overlay and audio

**Dependencies:** moviepy, requests, modules/config
**Reusable:** Not directly for analytics stories

---

#### 11. `modules/youtube_unit.py`
**Purpose:** YouTube upload via OAuth
**Key Functions:**
- `deploy_to_youtube(file_path, title, guide)` - Full upload with OAuth refresh, description, and auto-comment

**Dependencies:** google.oauth2, googleapiclient, modules/config
**Reusable:** Yes - OAuth pattern for YouTube API

---

## Reusable Code Summary

### For Story 1 (YouTube Shorts Analytics)
| File | Reusable Elements |
|------|-------------------|
| `sync_youtube.py` | **DIRECT REUSE** - Already has `get_youtube_service()`, `get_channel_videos()`, `get_video_statistics()` |
| `modules/database.py` | Database structure ready, just need to extract Shorts specifically |

**Recommendation:** Extract core functions from `sync_youtube.py` into `modules/shorts_analytics.py` and filter for Shorts (videos < 60 seconds or from Shorts shelf).

---

### For Story 2 (Gumroad Sales Tracking)
| File | Reusable Elements |
|------|-------------------|
| `modules/config.py` | Add GUMROAD_API_KEY to SECRETS dict |
| `modules/database.py` | Pattern for new `sales` table |

**Recommendation:** Create `modules/gumroad_tracker.py` with similar structure to database.py patterns.

---

### For Story 3 (Conversion Dashboard)
| File | Reusable Elements |
|------|-------------------|
| `dashboard.py` | Streamlit patterns, Plotly charts, page structure |
| `modules/database.py` | Query patterns |

**Recommendation:** Create `dashboard_shorts.py` using same structure as existing dashboard.

---

### For Story 4 (Hook Pattern Analysis)
| File | Reusable Elements |
|------|-------------------|
| `modules/analytics.py` | **DIRECT REUSE** - `analyze_hook_patterns()` already exists |
| `modules/ai_brain.py` | Gemini API integration for AI analysis |
| `main.py` | `identify_domain()` logic |

**Recommendation:** Enhance existing `analytics.py` with Gemini-powered analysis.

---

### For Story 5 (AI Content Suggestions)
| File | Reusable Elements |
|------|-------------------|
| `modules/ai_brain.py` | Gemini API setup, prompt engineering patterns |
| `winning_hooks.py` | Data structure for proven hooks |

**Recommendation:** Create `modules/content_suggester.py` using ai_brain patterns.

---

### For Story 6 (Weekly Report)
| File | Reusable Elements |
|------|-------------------|
| `modules/analytics.py` | `get_performance_summary()`, insight functions |
| `modules/database.py` | `get_performance_timeline()` |

**Recommendation:** Create `reports/weekly_summary.py` using existing analytics functions.

---

## Architecture Diagram

```
                    +-----------------+
                    |    main.py      |
                    | (Video Pipeline)|
                    +-----------------+
                            |
          +-----------------+-----------------+
          |                 |                 |
    +----------+      +-----------+     +------------+
    | ai_brain |      | video_lab |     | youtube_   |
    | (Gemini) |      | (MoviePy) |     | unit       |
    +----------+      +-----------+     +------------+
          |                                   |
          v                                   v
    +------------+                    +-------------+
    | winning_   |                    | sync_       |
    | hooks      |                    | youtube     |
    +------------+                    +-------------+
                                            |
                                            v
                    +-------------------+
                    |  modules/database |
                    |  (SQLite)         |
                    +-------------------+
                            |
          +-----------------+-----------------+
          |                                   |
    +-----------+                      +------------+
    | analytics |                      | dashboard  |
    | (Insights)|                      | (Streamlit)|
    +-----------+                      +------------+
```

---

## Key Findings

1. **Strong Foundation:** Database and analytics modules are well-structured and can be extended
2. **YouTube Integration Ready:** `sync_youtube.py` already does 80% of what Story 1 needs
3. **Gemini Integration Working:** AI content generation patterns are established
4. **Missing:** Gumroad API integration (Story 2), Shorts-specific filtering (Story 1)
5. **Dashboard Pattern:** Existing Streamlit dashboard provides template for new dashboards

---

## Recommended Next Steps

1. **Story 1:** Refactor `sync_youtube.py` → `modules/shorts_analytics.py`
2. **Story 2:** Add Gumroad API integration to `modules/config.py` and create `modules/gumroad_tracker.py`
3. **Story 3:** Create `dashboard_shorts.py` combining YouTube + Gumroad data
4. **Story 4:** Enhance `modules/analytics.py` with Gemini-powered hook analysis
5. **Story 5:** Create `modules/content_suggester.py` based on `ai_brain.py`
6. **Story 6:** Create `reports/weekly_summary.py` using existing analytics

---

*End of Code Audit Report*
