import streamlit as st
import os
import openai
import ast
from dotenv import load_dotenv
from fetch_reddit_posts import fetch_reddit_posts
from summarise_discussion import summarise_post

# Load API keys
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="TrendMosaic", layout="centered")
st.markdown("# 🧩 TrendMosaic – Reddit Trend Explorer")

# ---------------------------
# Step 1: Context Input
# ---------------------------
st.subheader("1️⃣ What tech topic are you interested in?")
topic = st.text_input(
    "Enter a topic you'd like to explore across Reddit (e.g. 'DuckDB', 'dbt', 'data engineering')",
    key="context_input",
    placeholder="Type something and press Enter..."
)

# ---------------------------
# Caching Reddit post fetch/summarisation
# ---------------------------
@st.cache_data(show_spinner=False)
def get_reddit_insights(topic):
    posts = fetch_reddit_posts(["dataengineering", "datascience"], topic, limit=12)
    enriched = []

    for post in posts:
        summary_raw = summarise_post(post["title"], post["body"])
        try:
            summary = ast.literal_eval(summary_raw)
        except Exception:
            summary = {"summary": summary_raw, "sentiment": "unknown", "tags": []}
        post["summary"] = summary
        enriched.append(post)

    return enriched

# ---------------------------
# When topic is submitted
# ---------------------------
if topic:
    with st.spinner("🔍 Fetching Reddit posts and generating summaries..."):
        enriched = get_reddit_insights(topic)

    st.success(f"✅ Pulled {len(enriched)} posts about '{topic}'")

    # Optional: Force re-fetch button
    if st.button("🔁 Refresh Reddit posts"):
        st.cache_data.clear()
        st.experimental_rerun()

    # ---------------------------
    # Step 2: User Q&A Input
    # ---------------------------
    st.subheader("2️⃣ Ask a question about this topic")
    user_query = st.text_input(
        "What would you like to know based on these discussions?",
        key="qa_input",
        placeholder="e.g. What are the pros and cons of dbt?"
    )

    if user_query:
        with st.spinner("💬 Generating insight from Reddit discussions..."):
            context = "\n\n".join([p["summary"]["summary"] for p in enriched])
            prompt = f"""
            Based on the following Reddit summaries, answer the question: "{user_query}"

            Reddit Summaries:
            {context}

            Please respond with a concise and clear community-sourced answer, summarising any disagreements if relevant.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            st.markdown("### 🧠 Community Insight")
            st.write(response.choices[0].message.content)

    # ---------------------------
    # Step 3: Reference Reddit Posts
    # ---------------------------
    st.subheader("📚 Supporting Reddit Posts")
    for post in enriched:
        with st.expander(post["title"]):
            st.markdown(post["summary"]["summary"])
            st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
            st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
            st.markdown(f"[🔗 View on Reddit]({post['url']})")

# Footer
st.markdown("---")
st.markdown(
    """
    <footer style='text-align: center;'>
      🔗 <a href="https://github.com/ronjamino/trendmosiac" target="_blank">View the code on GitHub</a>
    </footer>
    """,
    unsafe_allow_html=True
)
