# ==============================
# summarise_discussion.py
# ==============================
import openai

def summarise_post(title, body):
    prompt = f"""
    Summarise this Reddit post and extract the sentiment (positive, neutral, or negative).

    Title: {title}
    Body: {body}
    
    Output as JSON with 'summary', 'sentiment', and 'tags'.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']
