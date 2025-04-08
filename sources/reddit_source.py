import random

def get_reddit_context(posts, max_posts=5):
    """
    Returns a joined string of top Reddit summaries from TrendMosaic output.
    """
    valid_posts = [p for p in posts if isinstance(p.get("summary"), dict)]
    selected = random.sample(valid_posts, min(max_posts, len(valid_posts)))
    summaries = [p["summary"]["summary"] for p in selected]
    return "\n\n".join(summaries)
