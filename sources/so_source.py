import requests
from datetime import datetime

def fetch_so_posts(topic, limit=10):
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "votes",
        "q": topic,
        "site": "stackoverflow",
        "pagesize": limit,
        "filter": "default"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "body": item.get("title"),  # SO search doesn't return full body unless you use a deeper filter
            "url": item.get("link"),
            "score": item.get("score"),
            "created_utc": datetime.utcfromtimestamp(item.get("creation_date")).isoformat(),
            "source": "stackoverflow"
        })

    return results
