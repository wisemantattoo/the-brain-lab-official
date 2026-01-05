"""
מודול ניתוח וinsights אוטומטיים.
מזהה patterns בדאטה ומספק המלצות.
"""

from modules.database import get_all_videos, get_top_performers, get_domain_performance
import statistics

def analyze_hook_patterns():
    """
    מנתח אילו סוגי hooks עובדים הכי טוב.
    """
    videos = get_all_videos()
    
    if len(videos) < 5:
        return None
    
    # מיון לפי ביצועים
    sorted_videos = sorted(videos, key=lambda x: x['views'], reverse=True)
    top_10_percent = sorted_videos[:max(1, len(sorted_videos)//10)]
    
    # ניתוח אורך hook
    top_hook_lengths = [len(v['hook'].split()) for v in top_10_percent if v['views'] > 0]
    all_hook_lengths = [len(v['hook'].split()) for v in videos]
    
    insights = []
    
    if top_hook_lengths and all_hook_lengths:
        avg_top = statistics.mean(top_hook_lengths)
        avg_all = statistics.mean(all_hook_lengths)
        
        if avg_top < avg_all - 0.5:
            insights.append({
                'type': 'hook_length',
                'message': f'Shorter hooks perform better: Top videos average {avg_top:.1f} words vs {avg_all:.1f} overall',
                'recommendation': 'Keep hooks to 3-5 words maximum',
                'confidence': 0.8
            })
    
    # ניתוח patterns במילים
    top_hooks = [v['hook'] for v in top_10_percent if v['views'] > 0]
    
    # בדיקה אם "THE" מופיע
    the_count = sum(1 for h in top_hooks if h.startswith('THE '))
    if the_count / len(top_hooks) > 0.7:
        insights.append({
            'type': 'hook_pattern',
            'message': f'{the_count}/{len(top_hooks)} top videos start with "THE"',
            'recommendation': 'Continue using "THE [NOUN]" pattern',
            'confidence': 0.9
        })
    
    return insights


def analyze_domain_performance():
    """
    מזהה אילו domains/נושאים עובדים הכי טוב.
    """
    domains = get_domain_performance()
    
    if len(domains) < 2:
        return None
    
    insights = []
    
    # מצא את הטובים ביותר
    sorted_domains = sorted(domains, key=lambda x: x['avg_views'], reverse=True)
    best = sorted_domains[0]
    worst = sorted_domains[-1]
    
    # אם יש הבדל משמעותי
    if best['avg_views'] > worst['avg_views'] * 1.5:
        insights.append({
            'type': 'domain_winner',
            'message': f"{best['domain']} performs {(best['avg_views']/worst['avg_views']):.1f}x better than {worst['domain']}",
            'recommendation': f"Create more content in {best['domain']}",
            'confidence': 0.85
        })
    
    # בדיקה אם יש domain עם sample size קטן
    for domain in domains:
        if domain['video_count'] <= 2 and domain['avg_views'] > sorted_domains[len(sorted_domains)//2]['avg_views']:
            insights.append({
                'type': 'domain_potential',
                'message': f"{domain['domain']} shows promise but needs more testing ({domain['video_count']} videos)",
                'recommendation': f"Create 3-5 more videos in {domain['domain']} to validate performance",
                'confidence': 0.6
            })
    
    return insights


def analyze_recent_performance():
    """
    מנתח את הביצועים של הוידאואים האחרונים.
    """
    videos = get_all_videos()
    
    if len(videos) < 10:
        return None
    
    # 5 האחרונים vs הממוצע
    recent = videos[:5]
    all_videos = videos
    
    recent_avg = statistics.mean([v['views'] for v in recent if v['views'] > 0] or [0])
    overall_avg = statistics.mean([v['views'] for v in all_videos if v['views'] > 0] or [0])
    
    insights = []
    
    if recent_avg < overall_avg * 0.6:
        insights.append({
            'type': 'performance_drop',
            'message': f'Recent videos underperforming: {recent_avg:.0f} views vs {overall_avg:.0f} average',
            'recommendation': 'Review recent hooks and domains - consider reverting to proven patterns',
            'confidence': 0.75
        })
    elif recent_avg > overall_avg * 1.4:
        insights.append({
            'type': 'performance_spike',
            'message': f'Recent content performing well: {recent_avg:.0f} views vs {overall_avg:.0f} average',
            'recommendation': 'Analyze what changed and replicate successful patterns',
            'confidence': 0.8
        })
    
    return insights


def analyze_posting_times():
    """
    מנתח אילו זמני פרסום עובדים הכי טוב.
    (צריך יותר דאטה לinsight משמעותי)
    """
    videos = get_all_videos()
    
    if len(videos) < 20:
        return None
    
    # TODO: ניתוח שעות פרסום vs ביצועים
    # דורש timestamps מדויקים יותר
    
    return None


def get_all_insights():
    """
    מחזיר את כל ה-insights המזוהים.
    """
    all_insights = []
    
    # ריצה על כל פונקציות הניתוח
    hook_insights = analyze_hook_patterns()
    if hook_insights:
        all_insights.extend(hook_insights)
    
    domain_insights = analyze_domain_performance()
    if domain_insights:
        all_insights.extend(domain_insights)
    
    recent_insights = analyze_recent_performance()
    if recent_insights:
        all_insights.extend(recent_insights)
    
    # מיון לפי confidence
    all_insights.sort(key=lambda x: x['confidence'], reverse=True)
    
    return all_insights


def calculate_virality_score(views, likes, comments, video_age_hours):
    """
    מחשב ציון virality מנורמל.
    לוקח בחשבון גם את גיל הוידאו.
    """
    if video_age_hours < 1:
        video_age_hours = 1
    
    # ציון בסיסי מבוסס engagement
    engagement = likes + (comments * 2)  # תגובות שוות יותר
    base_score = (views * 0.7) + (engagement * 30)
    
    # נרמול לפי גיל
    normalized_score = base_score / (video_age_hours ** 0.3)
    
    return round(normalized_score, 2)


def get_performance_summary():
    """
    מחזיר סיכום ביצועים מקיף.
    """
    videos = get_all_videos()
    domains = get_domain_performance()
    insights = get_all_insights()
    
    if not videos:
        return {
            'status': 'no_data',
            'message': 'No videos in database yet'
        }
    
    # חישובים בסיסיים
    total_views = sum(v['views'] for v in videos)
    total_likes = sum(v['likes'] for v in videos)
    avg_views = statistics.mean([v['views'] for v in videos if v['views'] > 0] or [0])
    
    # מציאת trends
    if len(videos) >= 10:
        recent_5 = videos[:5]
        prev_5 = videos[5:10]
        
        recent_avg = statistics.mean([v['views'] for v in recent_5 if v['views'] > 0] or [0])
        prev_avg = statistics.mean([v['views'] for v in prev_5 if v['views'] > 0] or [0])
        
        if prev_avg > 0:
            trend = ((recent_avg - prev_avg) / prev_avg) * 100
        else:
            trend = 0
    else:
        trend = 0
    
    return {
        'status': 'success',
        'total_videos': len(videos),
        'total_views': total_views,
        'total_likes': total_likes,
        'avg_views': round(avg_views, 1),
        'trend_percent': round(trend, 1),
        'best_domain': domains[0] if domains else None,
        'insights_count': len(insights),
        'top_insights': insights[:3]
    }
