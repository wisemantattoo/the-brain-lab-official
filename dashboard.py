"""
🧠 The Brain Lab - Control Center Dashboard
להרצה: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.database import (
    get_all_videos, 
    get_top_performers, 
    get_domain_performance,
    get_statistics,
    get_performance_timeline,
    update_video_stats
)
from modules.analytics import get_all_insights, get_performance_summary

# ייבוא מודול נתוני דמו
try:
    from init_demo_data import check_if_demo_needed, create_demo_videos
    
    # יצירת נתוני דמו אם צריך (רק בפעם הראשונה)
    if check_if_demo_needed():
        with st.spinner("🎬 Creating demo data for the first time..."):
            create_demo_videos()
            st.success("✅ Demo data created! Refresh the page.")
            st.rerun()
except Exception as e:
    st.warning(f"⚠️ Could not load demo data: {e}")

# הגדרות עמוד
st.set_page_config(
    page_title="The Brain Lab Dashboard",
    page_icon="🧠",
    layout="wide"
)

# כותרת ראשית
st.title("🧠 The Brain Lab - Control Center")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎛️ Controls")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    stats = get_statistics()
    st.metric("Total Videos", stats['total_videos'])
    st.metric("Total Views", f"{stats['total_views']:,}")
    st.metric("Avg Views/Video", f"{stats['avg_views']:.1f}")
    
    st.markdown("---")
    st.markdown("### 🎯 Navigation")
    page = st.radio(
        "Select Page:",
        ["📊 Overview", "🏆 Top Performers", "🎯 Domain Analysis", "💡 Insights", "📈 All Videos"]
    )

# =================== PAGE: OVERVIEW ===================
if page == "📊 Overview":
    st.header("📊 Performance Overview")
    
    # מדדים עיקריים
    col1, col2, col3, col4 = st.columns(4)
    
    stats = get_statistics()
    summary = get_performance_summary()
    
    with col1:
        st.metric(
            "Total Videos",
            stats['total_videos'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Total Views",
            f"{stats['total_views']:,}",
            delta=f"{summary.get('trend_percent', 0):+.1f}%" if summary['status'] == 'success' else None
        )
    
    with col3:
        st.metric(
            "Avg Views/Video",
            f"{stats['avg_views']:.1f}",
            delta=None
        )
    
    with col4:
        best = stats['best_performer']
        st.metric(
            "Best Performer",
            best['hook'][:20] + "..." if len(best['hook']) > 20 else best['hook'],
            delta=f"↑ {best['views']} views"
        )
    
    st.markdown("---")
    
    # גרף ביצועים לאורך זמן
    st.subheader("📈 Views Over Time")
    
    timeline = get_performance_timeline()
    if timeline:
        df_timeline = pd.DataFrame(timeline)
        
        fig = px.line(
            df_timeline,
            x='date',
            y='total_views',
            markers=True,
            title="Total Views per Day"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Views",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for timeline yet. Keep posting!")
    
    # Domain breakdown
    st.subheader("🎯 Performance by Domain")
    domains = get_domain_performance()
    
    if domains:
        df_domains = pd.DataFrame(domains)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                df_domains,
                x='domain',
                y='avg_views',
                title="Average Views by Domain",
                color='avg_views',
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart
            fig = px.pie(
                df_domains,
                values='total_views',
                names='domain',
                title="View Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

# =================== PAGE: TOP PERFORMERS ===================
elif page == "🏆 Top Performers":
    st.header("🏆 Top Performing Videos")
    
    top_videos = get_top_performers(20)
    
    if top_videos:
        for i, video in enumerate(top_videos, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.markdown(f"### #{i}")
                
                with col2:
                    st.markdown(f"**{video['hook']}**")
                    st.caption(video['title'][:60] + "..." if len(video['title']) > 60 else video['title'])
                
                with col3:
                    st.metric("Views", f"{video['views']:,}")
                
                with col4:
                    st.markdown(f"🎯 *{video['domain'] or 'Unknown'}*")
                    if not video['video_id'].startswith('DEMO_'):
                        st.markdown(f"[Watch →](https://youtube.com/shorts/{video['video_id']})")
                    else:
                        st.caption("📊 Demo Video")
                
                st.markdown("---")
    else:
        st.info("No videos with views yet. Give it some time!")

# =================== PAGE: DOMAIN ANALYSIS ===================
elif page == "🎯 Domain Analysis":
    st.header("🎯 Domain Performance Analysis")
    
    domains = get_domain_performance()
    
    if domains:
        st.subheader("📊 Detailed Breakdown")
        
        df = pd.DataFrame(domains)
        st.dataframe(
            df,
            column_config={
                "domain": "Domain",
                "video_count": st.column_config.NumberColumn("Videos", format="%d"),
                "avg_views": st.column_config.NumberColumn("Avg Views", format="%.1f"),
                "max_views": st.column_config.NumberColumn("Best", format="%d"),
                "total_views": st.column_config.NumberColumn("Total", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("🎯 Recommendations")
        
        sorted_domains = sorted(domains, key=lambda x: x['avg_views'], reverse=True)
        best = sorted_domains[0]
        worst = sorted_domains[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"**✅ Best Performing: {best['domain']}**")
            st.write(f"- Average: {best['avg_views']:.1f} views")
            st.write(f"- Total: {best['total_views']:,} views")
            st.write(f"- Videos: {best['video_count']}")
            st.write("💡 *Create more content in this domain*")
        
        with col2:
            st.warning(f"**⚠️ Needs Work: {worst['domain']}**")
            st.write(f"- Average: {worst['avg_views']:.1f} views")
            st.write(f"- Total: {worst['total_views']:,} views")
            st.write(f"- Videos: {worst['video_count']}")
            
            if worst['video_count'] < 3:
                st.write("💡 *More testing needed - create 3-5 videos*")
            else:
                st.write("💡 *Consider focusing on better domains*")
    
    else:
        st.info("Not enough data yet. Create more videos!")

# =================== PAGE: INSIGHTS ===================
elif page == "💡 Insights":
    st.header("💡 AI-Generated Insights")
    
    insights = get_all_insights()
    
    if insights:
        st.subheader("🔍 Discoveries")
        
        for insight in insights:
            confidence = insight['confidence']
            
            if confidence >= 0.8:
                st.success(f"**{insight['message']}** (Confidence: {confidence:.0%})")
            elif confidence >= 0.6:
                st.info(f"**{insight['message']}** (Confidence: {confidence:.0%})")
            else:
                st.warning(f"**{insight['message']}** (Confidence: {confidence:.0%})")
            
            st.write(f"💡 Recommendation: {insight['recommendation']}")
            st.markdown("---")
    
    else:
        st.info("Not enough data to generate insights yet. Create at least 10 videos with views.")
    
    # Performance summary
    st.subheader("📊 Performance Summary")
    summary = get_performance_summary()
    
    if summary['status'] == 'success':
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Recent Trend", f"{summary['trend_percent']:+.1f}%")
            if summary['trend_percent'] > 10:
                st.success("📈 Growing!")
            elif summary['trend_percent'] < -10:
                st.error("📉 Declining - review strategy")
            else:
                st.info("➡️ Stable")
        
        with col2:
            if summary['best_domain']:
                st.metric("Best Domain", summary['best_domain']['domain'])
                st.write(f"{summary['best_domain']['avg_views']:.1f} avg views")

# =================== PAGE: ALL VIDEOS ===================
elif page == "📈 All Videos":
    st.header("📈 All Videos Database")
    
    videos = get_all_videos()
    
    if videos:
        # פילטרים
        col1, col2 = st.columns(2)
        
        with col1:
            domains = list(set(v['domain'] for v in videos if v['domain']))
            domain_filter = st.multiselect(
                "Filter by Domain:",
                options=['All'] + domains,
                default=['All']
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by:",
                options=['Date (Newest)', 'Date (Oldest)', 'Views (High)', 'Views (Low)']
            )
        
        # סינון ומיון
        filtered = videos
        
        if 'All' not in domain_filter and domain_filter:
            filtered = [v for v in filtered if v['domain'] in domain_filter]
        
        if sort_by == 'Date (Oldest)':
            filtered = sorted(filtered, key=lambda x: x['created_at'])
        elif sort_by == 'Views (High)':
            filtered = sorted(filtered, key=lambda x: x['views'], reverse=True)
        elif sort_by == 'Views (Low)':
            filtered = sorted(filtered, key=lambda x: x['views'])
        
        # הצגה
        st.write(f"Showing {len(filtered)} videos")
        
        for video in filtered:
            with st.expander(f"{video['hook']} - {video['views']} views"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Title:** {video['title']}")
                    st.markdown(f"**Domain:** {video['domain'] or 'N/A'}")
                    st.markdown(f"**Created:** {video['created_at']}")
                    if not video['video_id'].startswith('DEMO_'):
                        st.markdown(f"[Watch on YouTube →](https://youtube.com/shorts/{video['video_id']})")
                    else:
                        st.info("📊 This is demo data")
                
                with col2:
                    st.metric("Views", video['views'])
                    st.metric("Likes", video['likes'])
                    st.metric("Comments", video['comments'])
    
    else:
        st.info("No videos in database yet. Run the bot to create your first video!")

# Footer
st.markdown("---")
st.caption("🧠 The Brain Lab Dashboard v1.0 | Data updates in real-time")
st.caption("📊 Demo mode - showing sample data")
