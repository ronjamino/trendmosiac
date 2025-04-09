# ==============================
# summarise_discussion.py
# ==============================
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_post(title, body):
    body = body.strip()[:1000] # Limit body to 1000 characters

    prompt = f"""
Summarise this post and extract the sentiment (positive, neutral, or negative).

Title: {title}
Body: {body}

Output as JSON with keys:
- 'summary': A brief summary of the discussion.
- 'sentiment': positive, neutral, or negative.
- 'tags': a list of named technologies, tools, frameworks, or concepts mentioned (e.g. 'dbt', 'Snowflake', 'DuckDB').

Keep the response under 3-5 sentences.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "{'summary': '⚠️ Failed to summarise due to API error.', 'sentiment': 'unknown', 'tags': []}"
