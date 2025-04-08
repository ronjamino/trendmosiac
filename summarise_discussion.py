# ==============================
# summarise_discussion.py
# ==============================
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_post(title, body):
    prompt = f"""
    Summarise this Reddit post and extract the sentiment (positive, neutral, or negative).

    Title: {title}
    Body: {body}
    
    Output as JSON with 'summary', 'sentiment', and 'tags'.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
