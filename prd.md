# BRAIN LAB - YouTube Shorts Conversion Optimizer

**Product Requirements Document (PRD)**

---

## 🎯 Project Vision

Build an AI-powered system that learns which YouTube Shorts convert viewers into buyers of the "21-Day Personal Growth Tracker" ($4.99 on Gumroad).

**Core Principle:** Optimize for revenue, not just views.

---

## 📊 Success Metrics

- Conversion rate per Short (views → sales)
- Hook retention in first 3 seconds
- Click-through rate to bio link
- Revenue per 1000 views
- Pattern recognition (what works?)

---

## 🏗️ User Stories & Tasks

---

### **Story 0: Code Audit & Integration Plan**
**Priority:** CRITICAL ⭐⭐⭐
**Status:** ✅ Completed

**As a developer**, I want to understand existing code structure
**So that** I can reuse what works and avoid breaking things

**Tasks:**
- [x] ✅ Scan all .py files in project
- [x] ✅ Document what each file does
- [x] ✅ Identify reusable code
- [x] ✅ Save findings to docs/code_audit.md

**Estimated Time:** 10-15 minutes

---

### **Story 1: YouTube Shorts Analytics**
**Priority:** HIGH ⭐⭐⭐
**Status:** ✅ Completed

**As a creator**, I want to see Shorts performance data

**Tasks:**
- [x] ✅ Create modules/shorts_analytics.py
- [x] ✅ Connect to YouTube API
- [x] ✅ Fetch Shorts from last 30 days
- [x] ✅ Extract: video_id, title, views, likes

**Estimated Time:** 15-20 minutes

---

### **Story 2: Gumroad Sales Tracking**
**Priority:** HIGH ⭐⭐⭐
**Status:** ✅ Completed

**As a creator**, I want to see which sales came from YouTube

**Tasks:**
- [x] ✅ Create modules/gumroad_tracker.py
- [x] ✅ Connect to Gumroad API
- [x] ✅ Fetch sales with referrer data
- [x] ✅ Match sales to Shorts

**Estimated Time:** 15-20 minutes

---

### **Story 3: Conversion Dashboard**
**Priority:** HIGH ⭐⭐⭐
**Status:** ✅ Completed

**As a creator**, I want to see performance + sales together

**Tasks:**
- [x] ✅ Create dashboard_shorts.py
- [x] ✅ Combine YouTube + Gumroad data
- [x] ✅ Calculate conversion rate
- [x] ✅ Display sorted table

**Estimated Time:** 20-25 minutes

---

### **Story 4: Hook Pattern Analysis**
**Priority:** MEDIUM ⭐⭐
**Status:** ⏳ Not Started

**As a creator**, I want to understand which hooks convert

**Tasks:**
- [ ] ⏳ Create modules/hook_analyzer.py
- [ ] ⏳ Use Gemini to analyze titles
- [ ] ⏳ Categorize hook types
- [ ] ⏳ Correlate with conversion rates

**Estimated Time:** 20-25 minutes

---

### **Story 5: AI Content Suggestions**
**Priority:** MEDIUM ⭐⭐
**Status:** ⏳ Not Started

**As a creator**, I want AI to suggest next Short ideas

**Tasks:**
- [ ] ⏳ Create modules/content_suggester.py
- [ ] ⏳ Analyze top performers
- [ ] ⏳ Generate 5 new ideas
- [ ] ⏳ Save to suggestions.md

**Estimated Time:** 15-20 minutes

---

### **Story 6: Weekly Report**
**Priority:** LOW ⭐
**Status:** ⏳ Not Started

**As a creator**, I want weekly summaries

**Tasks:**
- [ ] ⏳ Create reports/weekly_summary.py
- [ ] ⏳ Compile weekly stats
- [ ] ⏳ Generate markdown report

**Estimated Time:** 15 minutes

---

END OF PRD
