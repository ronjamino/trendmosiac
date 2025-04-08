# ==============================
# fetch_reddit_posts.py
# ==============================
import praw
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_reddit_posts(subreddits, keyword, days=7, limit=20):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "TrendMosaicBot")
    )

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    results = []

    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.search(keyword, sort="top", time_filter="week", limit=limit):
            results.append({
                "title": post.title,
                "body": post.selftext,
                "score": post.score,
                "url": post.url,
                "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
                "subreddit": sub
            })
    return results
