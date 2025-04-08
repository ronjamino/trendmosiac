# ==============================
# pipeline.py
# ==============================
from fetch_reddit_posts import fetch_reddit_posts
from summarise_discussion import summarise_post
import json
import time

SUBREDDITS = ["dataengineering", "datascience"]
KEYWORD = "dbt"

if __name__ == "__main__":
    posts = fetch_reddit_posts(SUBREDDITS, KEYWORD)
    enriched = []

    for post in posts:
        print(f"Summarising post: {post['title']}")
        summary = summarise_post(post['title'], post['body'])
        post['summary'] = json.loads(summary)  # <--- convert string to dict
        enriched.append(post)
        time.sleep(1)  # avoid hitting rate limits

    with open("trendmosiac_output.json", "w") as f:
        json.dump(enriched, f, indent=2)
