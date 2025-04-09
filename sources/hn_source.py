import requests
from datetime import datetime

def fetch_hn_posts(topic, limit=10):
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": topic,
        "tags": "story",
        "hitsPerPage": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data["hits"]:
        results.append({
            "title": item.get("title"),
            "body": item.get("story_text") or item.get("title"),  # HN often lacks full text
            "url": item.get("url") or f"https://news.ycombinator.com/item?id={item.get('objectID')}",
            "created_utc": datetime.utcfromtimestamp(item.get("created_at_i")).isoformat(),
            "source": "hackernews"
        })

    return results
