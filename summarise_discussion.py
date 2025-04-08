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
Summarise this Reddit post and extract the sentiment (positive, neutral, or negative).

Title: {title}
Body: {body}

Output as JSON with 'summary', 'sentiment', and 'tags'.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300  # 🧠 limit token usage for summarisation
    )

    return response.choices[0].message.content.strip()
