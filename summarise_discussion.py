# ==============================
# summarise_discussion.py
# ==============================
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarise_post(title, body):
    prompt = f"""
Summarise this post and extract the sentiment (positive, neutral, or negative).

Title: {title}
Body: {body}

Output as JSON with keys:
- 'summary': A brief summary of the discussion.
- 'sentiment': positive, neutral, or negative.
- 'tags': a list of named technologies, tools, frameworks, or concepts mentioned (e.g. 'dbt', 'Snowflake', 'DuckDB').
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300  # 🧠 limit token usage for summarisation
    )

    return response.choices[0].message.content.strip()
