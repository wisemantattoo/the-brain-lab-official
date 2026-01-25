"""
AI Content Suggester Module - The Brain Lab
Uses Gemini AI to analyze top performers and generate new Short ideas.
"""

import os
import json
from datetime import datetime
from typing import Optional
from google import genai
from google.genai import types

# Import analytics modules
from modules.shorts_analytics import get_shorts_analytics
from modules.gumroad_tracker import get_sales_analytics, match_sales_to_shorts
from modules.hook_analyzer import (
    HOOK_CATEGORIES,
    categorize_hook_by_rules,
    calculate_category_performance
)


def get_gemini_client(api_key: Optional[str] = None):
    """
    Creates a Gemini AI client.

    Args:
        api_key: Gemini API key. If not provided, reads from environment.

    Returns:
        Gemini client or None if connection fails.
    """
    try:
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment")
            return None

        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error creating Gemini client: {e}")
        return None


def analyze_top_performers(shorts: list, top_n: int = 10) -> dict:
    """
    Analyzes top performing Shorts to identify success patterns.

    Args:
        shorts: List of shorts with views, sales, conversion data
        top_n: Number of top performers to analyze (default 10)

    Returns:
        Dictionary with top performers analysis
    """
    if not shorts:
        return {
            'top_by_views': [],
            'top_by_conversion': [],
            'top_by_revenue': [],
            'common_patterns': []
        }

    # Sort by different metrics
    sorted_by_views = sorted(shorts, key=lambda x: x.get('views', 0), reverse=True)
    sorted_by_conversion = sorted(
        [s for s in shorts if s.get('conversion_rate', 0) > 0],
        key=lambda x: x.get('conversion_rate', 0),
        reverse=True
    )
    sorted_by_revenue = sorted(
        [s for s in shorts if s.get('revenue', 0) > 0],
        key=lambda x: x.get('revenue', 0),
        reverse=True
    )

    # Extract common patterns from titles
    patterns = extract_title_patterns(sorted_by_views[:top_n] + sorted_by_conversion[:top_n])

    return {
        'top_by_views': sorted_by_views[:top_n],
        'top_by_conversion': sorted_by_conversion[:top_n],
        'top_by_revenue': sorted_by_revenue[:top_n],
        'common_patterns': patterns
    }


def extract_title_patterns(shorts: list) -> list:
    """
    Extracts common patterns from successful Short titles.

    Args:
        shorts: List of top performing shorts

    Returns:
        List of common patterns/themes
    """
    patterns = {
        'prefixes': {},
        'themes': {},
        'power_words': {}
    }

    power_word_list = [
        'brain', 'smart', 'intelligence', 'psychology', 'fact',
        'secret', 'truth', 'sign', 'people', 'never', 'always',
        'research', 'studies', 'science', 'habit', 'instantly'
    ]

    for short in shorts:
        title = short.get('title', '').lower()

        # Check for prefixes
        if 'brain fact:' in title:
            patterns['prefixes']['BRAIN FACT'] = patterns['prefixes'].get('BRAIN FACT', 0) + 1
        elif 'psychology fact:' in title or 'psychology says:' in title:
            patterns['prefixes']['PSYCHOLOGY FACT'] = patterns['prefixes'].get('PSYCHOLOGY FACT', 0) + 1
        elif 'social intelligence:' in title:
            patterns['prefixes']['SOCIAL INTELLIGENCE'] = patterns['prefixes'].get('SOCIAL INTELLIGENCE', 0) + 1

        # Check for themes
        category = categorize_hook_by_rules(title)
        patterns['themes'][category] = patterns['themes'].get(category, 0) + 1

        # Check for power words
        for word in power_word_list:
            if word in title:
                patterns['power_words'][word] = patterns['power_words'].get(word, 0) + 1

    # Sort and return most common
    sorted_prefixes = sorted(patterns['prefixes'].items(), key=lambda x: x[1], reverse=True)
    sorted_themes = sorted(patterns['themes'].items(), key=lambda x: x[1], reverse=True)
    sorted_words = sorted(patterns['power_words'].items(), key=lambda x: x[1], reverse=True)

    return {
        'top_prefixes': sorted_prefixes[:3],
        'top_themes': sorted_themes[:5],
        'top_power_words': sorted_words[:10]
    }


def generate_content_ideas_with_gemini(
    top_performers: dict,
    category_performance: dict,
    num_ideas: int = 5,
    api_key: Optional[str] = None
) -> list:
    """
    Uses Gemini AI to generate new Short ideas based on performance data.

    Args:
        top_performers: Analysis of top performing shorts
        category_performance: Performance metrics by category
        num_ideas: Number of ideas to generate (default 5)
        api_key: Gemini API key (optional, reads from env)

    Returns:
        List of content idea dictionaries
    """
    client = get_gemini_client(api_key)

    if not client:
        print("Warning: Gemini unavailable, using rule-based generation")
        return generate_fallback_ideas(top_performers, category_performance, num_ideas)

    # Build context from performance data
    top_titles = []
    for short in top_performers.get('top_by_views', [])[:5]:
        views = short.get('views', 0)
        sales = short.get('sales', 0)
        top_titles.append(f"- \"{short['title']}\" ({views:,} views, {sales} sales)")

    top_converting = []
    for short in top_performers.get('top_by_conversion', [])[:5]:
        conv = short.get('conversion_rate', 0)
        top_converting.append(f"- \"{short['title']}\" ({conv:.4f} conv rate)")

    category_summary = []
    for cat, perf in list(category_performance.items())[:5]:
        category_summary.append(
            f"- {cat}: {perf['count']} shorts, {perf['total_views']:,} views, "
            f"{perf['conversion_rate']:.4f} conv rate"
        )

    patterns = top_performers.get('common_patterns', {})
    prefixes = [p[0] for p in patterns.get('top_prefixes', [])]
    power_words = [w[0] for w in patterns.get('top_power_words', [])[:5]]

    prompt = f"""You are a content strategist for 'The Brain Lab', a YouTube Shorts channel about psychology and brain science.

MISSION: Generate {num_ideas} NEW YouTube Short ideas that will maximize views AND conversions to product sales.

PERFORMANCE DATA FROM OUR CHANNEL:

Top Performing Shorts (by views):
{chr(10).join(top_titles) if top_titles else "No data available"}

Top Converting Shorts (views to sales):
{chr(10).join(top_converting) if top_converting else "No conversions tracked yet"}

Category Performance:
{chr(10).join(category_summary) if category_summary else "No category data"}

PROVEN PATTERNS:
- Best prefixes: {', '.join(prefixes) if prefixes else 'BRAIN FACT, PSYCHOLOGY FACT'}
- Power words that work: {', '.join(power_words) if power_words else 'brain, smart, people, intelligence, fact'}

RULES FOR NEW IDEAS:
1. MUST use one of these prefixes: BRAIN FACT:, PSYCHOLOGY FACT:, or SOCIAL INTELLIGENCE:
2. MUST include #TheBrainLab hashtag in title
3. Hook should be 4-6 words AFTER the prefix
4. Focus on themes that convert: smart people behaviors, brain patterns, social intelligence
5. Use power words from our proven list
6. Title should be 8-12 words + hashtag
7. Content should be factual and based on real psychology/neuroscience
8. Target emotions: curiosity, self-identification, surprise

Generate {num_ideas} NEW ideas that DON'T duplicate our existing content.

OUTPUT FORMAT (JSON array):
[
  {{
    "hook": "PREFIX: Short Statement",
    "title": "Full YouTube title with #TheBrainLab",
    "description": "2-3 sentence script/guide with scientific backing",
    "target_emotion": "curiosity/surprise/self-identification/fear",
    "predicted_category": "BRAIN FACT/PSYCHOLOGY FACT/etc",
    "reasoning": "Brief explanation of why this should perform well"
  }},
  ...
]

Return ONLY valid JSON, no explanations outside the array."""

    try:
        models_to_try = [
            "gemini-2.0-flash-exp",
            "gemini-flash-latest"
        ]

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        temperature=0.7  # Higher creativity for new ideas
                    ),
                    contents=prompt
                )

                response_text = response.text.strip()

                # Handle markdown code blocks
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()

                ideas = json.loads(response_text)

                # Validate and enhance ideas
                validated_ideas = []
                for idea in ideas[:num_ideas]:
                    if validate_content_idea(idea):
                        validated_ideas.append(idea)

                if validated_ideas:
                    return validated_ideas

            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue

        # All models failed
        print("All Gemini models failed, using fallback generation")
        return generate_fallback_ideas(top_performers, category_performance, num_ideas)

    except Exception as e:
        print(f"Gemini generation failed: {e}")
        return generate_fallback_ideas(top_performers, category_performance, num_ideas)


def validate_content_idea(idea: dict) -> bool:
    """
    Validates a content idea meets our requirements.

    Args:
        idea: Content idea dictionary

    Returns:
        True if valid, False otherwise
    """
    if not idea.get('hook') or not idea.get('title'):
        return False

    hook = idea['hook'].upper()
    title = idea['title']

    # Check for valid prefix
    valid_prefixes = ["BRAIN FACT:", "PSYCHOLOGY FACT:", "SOCIAL INTELLIGENCE:"]
    has_valid_prefix = any(hook.startswith(prefix) for prefix in valid_prefixes)

    if not has_valid_prefix:
        return False

    # Check for hashtag
    if "#TheBrainLab" not in title and "#thebrainlab" not in title.lower():
        return False

    return True


def generate_fallback_ideas(
    top_performers: dict,
    category_performance: dict,
    num_ideas: int = 5
) -> list:
    """
    Generates content ideas using rule-based approach when AI unavailable.

    Args:
        top_performers: Analysis of top performing shorts
        category_performance: Performance metrics by category
        num_ideas: Number of ideas to generate

    Returns:
        List of content idea dictionaries
    """
    # Fallback ideas based on proven patterns
    fallback_ideas = [
        {
            "hook": "BRAIN FACT: Daydreaming",
            "title": "Brain Fact: Daydreaming is a sign of intelligence... #TheBrainLab",
            "description": "Neuroscience shows intelligent minds wander more. Your brain's default mode network activates during daydreaming, connecting disparate ideas and solving problems unconsciously.",
            "target_emotion": "self-identification",
            "predicted_category": "BRAIN FACT",
            "reasoning": "Self-identification hook + intelligence theme proven to perform"
        },
        {
            "hook": "PSYCHOLOGY FACT: Reading People",
            "title": "Psychology Fact: Smart people can read others instantly... #TheBrainLab",
            "description": "Research shows high IQ correlates with superior pattern recognition in social situations. Your brain processes thousands of micro-signals simultaneously to assess others.",
            "target_emotion": "curiosity",
            "predicted_category": "PSYCHOLOGY FACT",
            "reasoning": "Social intelligence angle + smart people theme"
        },
        {
            "hook": "BRAIN FACT: Music Preference",
            "title": "Brain Fact: Your music taste reveals your intelligence... #TheBrainLab",
            "description": "Studies link complex music preference to higher cognitive function. Your brain seeks patterns that match its processing capability, gravitating toward complexity it can decode.",
            "target_emotion": "curiosity",
            "predicted_category": "BRAIN FACT",
            "reasoning": "Universal appeal + self-reflection trigger"
        },
        {
            "hook": "SOCIAL INTELLIGENCE: Compliment Test",
            "title": "Social Intelligence: How you receive compliments reveals your character... #TheBrainLab",
            "description": "Psychologists observe that deflecting compliments indicates low self-worth, while accepting them gracefully shows emotional intelligence and security.",
            "target_emotion": "self-identification",
            "predicted_category": "SOCIAL INTELLIGENCE",
            "reasoning": "Social dynamics + character reveal theme"
        },
        {
            "hook": "PSYCHOLOGY FACT: Memory Editing",
            "title": "Psychology Fact: Your brain edits memories every time you recall them... #TheBrainLab",
            "description": "Neuroscience proves each memory recall is a reconstruction, not playback. Your brain subtly alters memories based on current emotions and knowledge, making them less reliable over time.",
            "target_emotion": "surprise",
            "predicted_category": "PSYCHOLOGY FACT",
            "reasoning": "Mind-blowing fact + universal relevance"
        },
        {
            "hook": "BRAIN FACT: Problem Solving",
            "title": "Brain Fact: Your best ideas come when you stop thinking... #TheBrainLab",
            "description": "Neuroscience shows the 'aha moment' occurs when your conscious mind relaxes. Your subconscious continues processing, finding solutions your focused attention missed.",
            "target_emotion": "curiosity",
            "predicted_category": "BRAIN FACT",
            "reasoning": "Productivity angle + surprising insight"
        },
        {
            "hook": "SOCIAL INTELLIGENCE: Angry Response",
            "title": "Social Intelligence: How you respond to criticism reveals everything... #TheBrainLab",
            "description": "Behavioral psychologists note that defensive reactions indicate insecurity, while calm acknowledgment shows emotional maturity and self-awareness.",
            "target_emotion": "self-identification",
            "predicted_category": "SOCIAL INTELLIGENCE",
            "reasoning": "Character reveal + self-reflection"
        }
    ]

    return fallback_ideas[:num_ideas]


def save_suggestions_to_markdown(
    ideas: list,
    top_performers: dict,
    category_performance: dict,
    filename: str = "suggestions.md"
) -> str:
    """
    Saves content suggestions to a markdown file.

    Args:
        ideas: List of content idea dictionaries
        top_performers: Analysis of top performers
        category_performance: Category performance data
        filename: Output filename (default suggestions.md)

    Returns:
        Path to saved file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = f"""# Content Suggestions - The Brain Lab

**Generated:** {timestamp}

---

## 📊 Performance Analysis

### Top Performing Shorts (by views)

| Title | Views | Sales | Conv Rate |
|-------|-------|-------|-----------|
"""

    for short in top_performers.get('top_by_views', [])[:5]:
        title = short.get('title', '')[:40] + "..."
        views = short.get('views', 0)
        sales = short.get('sales', 0)
        conv = short.get('conversion_rate', 0)
        content += f"| {title} | {views:,} | {sales} | {conv:.4f} |\n"

    content += """
### Top Converting Shorts (by conversion rate)

| Title | Views | Sales | Conv Rate |
|-------|-------|-------|-----------|
"""

    for short in top_performers.get('top_by_conversion', [])[:5]:
        title = short.get('title', '')[:40] + "..."
        views = short.get('views', 0)
        sales = short.get('sales', 0)
        conv = short.get('conversion_rate', 0)
        content += f"| {title} | {views:,} | {sales} | {conv:.4f} |\n"

    content += """
### Category Performance

| Category | Shorts | Views | Conv Rate | RPM |
|----------|--------|-------|-----------|-----|
"""

    for cat, perf in list(category_performance.items())[:7]:
        content += f"| {cat} | {perf['count']} | {perf['total_views']:,} | {perf['conversion_rate']:.4f} | ${perf['rpm']:.2f} |\n"

    content += """
---

## 💡 New Content Ideas

"""

    for i, idea in enumerate(ideas, 1):
        content += f"""### Idea {i}: {idea.get('hook', 'Untitled')}

**Title:** {idea.get('title', '')}

**Category:** {idea.get('predicted_category', 'Unknown')}

**Target Emotion:** {idea.get('target_emotion', 'Unknown')}

**Script/Description:**
> {idea.get('description', '')}

**Why This Should Work:**
{idea.get('reasoning', 'Based on proven patterns from top performers.')}

---

"""

    content += """
## 📝 Usage Instructions

1. Pick an idea from above
2. Create the Short following the hook and description
3. Use the exact title format provided
4. Post and track performance in dashboard

---

*Generated by The Brain Lab Content Suggester*
"""

    # Save to file
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def get_content_suggestions(
    channel_id: Optional[str] = None,
    youtube_api_key: Optional[str] = None,
    gumroad_token: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    product_id: Optional[str] = None,
    days: int = 30,
    num_ideas: int = 5,
    save_to_file: bool = True
) -> dict:
    """
    Main function to generate content suggestions based on performance data.

    Args:
        channel_id: YouTube channel ID (or from env)
        youtube_api_key: YouTube API key (or from env)
        gumroad_token: Gumroad access token (or from env)
        gemini_api_key: Gemini API key (or from env)
        product_id: Optional Gumroad product ID filter
        days: Number of days to look back
        num_ideas: Number of ideas to generate
        save_to_file: Whether to save suggestions to markdown file

    Returns:
        Dictionary with content suggestions and analysis
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
            'ideas': [],
            'analysis': {}
        }

    shorts = youtube_result['shorts']

    # Fetch Gumroad sales data
    sales_result = get_sales_analytics(
        access_token=gumroad_token,
        product_id=product_id,
        days=days
    )

    # Match sales to shorts if available
    if sales_result['success'] and sales_result['youtube_sales']:
        matched = match_sales_to_shorts(sales_result['youtube_sales'], shorts)
        matched_map = {m['video_id']: m for m in matched}

        for short in shorts:
            video_id = short['video_id']
            if video_id in matched_map:
                short['sales'] = matched_map[video_id]['sale_count']
                short['revenue'] = matched_map[video_id]['total_revenue']
            else:
                short['sales'] = 0
                short['revenue'] = 0

            views = short.get('views', 0)
            short['conversion_rate'] = round(short['sales'] / views * 1000, 4) if views > 0 else 0
            short['rpm'] = round(short['revenue'] / views * 1000, 2) if views > 0 else 0
    else:
        for short in shorts:
            short['sales'] = 0
            short['revenue'] = 0
            short['conversion_rate'] = 0
            short['rpm'] = 0

    # Add category to each short
    for short in shorts:
        short['category'] = categorize_hook_by_rules(short['title'])

    # Analyze top performers
    top_performers = analyze_top_performers(shorts)

    # Calculate category performance
    category_performance = calculate_category_performance(shorts)

    # Generate content ideas
    ideas = generate_content_ideas_with_gemini(
        top_performers=top_performers,
        category_performance=category_performance,
        num_ideas=num_ideas,
        api_key=gemini_api_key
    )

    # Save to file if requested
    file_path = None
    if save_to_file:
        file_path = save_suggestions_to_markdown(
            ideas=ideas,
            top_performers=top_performers,
            category_performance=category_performance
        )

    return {
        'success': True,
        'error': None,
        'ideas': ideas,
        'top_performers': top_performers,
        'category_performance': category_performance,
        'total_shorts_analyzed': len(shorts),
        'file_saved': file_path,
        'youtube_summary': youtube_result['summary'],
        'sales_available': sales_result['success']
    }


def print_suggestions_report(result: dict):
    """
    Prints a formatted content suggestions report.

    Args:
        result: Result from get_content_suggestions()
    """
    if not result['success']:
        print(f"Error: {result['error']}")
        return

    print("\n" + "=" * 70)
    print("     CONTENT SUGGESTIONS REPORT - THE BRAIN LAB")
    print("=" * 70)

    print(f"\nData Analyzed: {result['total_shorts_analyzed']} Shorts")
    print(f"Sales Data Available: {'Yes' if result['sales_available'] else 'No'}")

    # Top Performers Summary
    print(f"\n{'TOP PERFORMERS':^70}")
    print("-" * 70)

    top = result.get('top_performers', {})
    print("\nBy Views:")
    for short in top.get('top_by_views', [])[:3]:
        print(f"  - {short['title'][:50]}... ({short['views']:,} views)")

    print("\nBy Conversion:")
    for short in top.get('top_by_conversion', [])[:3]:
        print(f"  - {short['title'][:50]}... ({short.get('conversion_rate', 0):.4f} conv)")

    # Content Ideas
    print(f"\n{'NEW CONTENT IDEAS':^70}")
    print("-" * 70)

    for i, idea in enumerate(result['ideas'], 1):
        print(f"\n{i}. {idea.get('hook', 'Untitled')}")
        print(f"   Title: {idea.get('title', '')[:60]}...")
        print(f"   Category: {idea.get('predicted_category', 'Unknown')}")
        print(f"   Target: {idea.get('target_emotion', 'Unknown')}")
        print(f"   Why: {idea.get('reasoning', '')[:60]}...")

    # File saved
    if result.get('file_saved'):
        print(f"\n{'FILE SAVED':^70}")
        print("-" * 70)
        print(f"  Suggestions saved to: {result['file_saved']}")

    print("\n" + "=" * 70)


# CLI entry point
if __name__ == "__main__":
    import sys

    # Parse arguments
    days = 30
    num_ideas = 5

    for arg in sys.argv[1:]:
        if arg.isdigit():
            days = int(arg)
        elif arg.startswith('--ideas='):
            num_ideas = int(arg.split('=')[1])

    print(f"Generating content suggestions...")
    print(f"Looking back: {days} days")
    print(f"Ideas to generate: {num_ideas}")
    print("-" * 50)

    result = get_content_suggestions(days=days, num_ideas=num_ideas)
    print_suggestions_report(result)
