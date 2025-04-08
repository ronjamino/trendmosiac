# ==============================
# app.py (Streamlit UI)
# ==============================
import streamlit as st
import os
import openai
import ast
from dotenv import load_dotenv
from fetch_reddit_posts import fetch_reddit_posts
from summarise_discussion import summarise_post

# Load env vars
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# App config
st.set_page_config(page_title="TrendMosaic", layout="centered")
st.title("🧩 TrendMosaic – Reddit Trend Explorer")

# User input: Topic search
topic = st.text_input(
    "🔍 Search Reddit for posts about a topic (e.g. 'dbt', 'DuckDB', 'data pipelines')",
    key="context_input"
)
    

if topic:
    st.markdown("---")
    st.markdown(f"Searching for posts related to: `{topic}`")

    with st.spinner("Fetching Reddit posts and generating summaries..."):
        try:
            posts = fetch_reddit_posts(["dataengineering", "datascience"], topic, limit=10)
            enriched = []

            for post in posts:
                summary_raw = summarise_post(post["title"], post["body"])
                try:
                    summary = ast.literal_eval(summary_raw)
                except Exception:
                    summary = {"summary": summary_raw, "sentiment": "unknown", "tags": []}
                post["summary"] = summary
                enriched.append(post)

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
            st.stop()

    st.success(f"✅ Pulled {len(enriched)} posts about '{topic}'")

    # User selects a post to view
    titles = [p["title"] for p in enriched]
    selected_title = st.selectbox("📌 Choose a Reddit post to explore:", titles)
    selected_post = next(p for p in enriched if p["title"] == selected_title)

    st.markdown("### ✍️ Summary")
    st.write(selected_post["summary"]["summary"])
    st.markdown(f"**🗣 Sentiment:** {selected_post['summary'].get('sentiment', 'unknown')}")
    st.markdown(f"**🏷 Tags:** {', '.join(selected_post['summary'].get('tags', []))}")
    st.markdown(f"[🔗 View on Reddit]({selected_post['url']})")

    # Q&A input
    st.markdown("---")
    user_query = st.text_input(
        "🧠 Ask a question about these Reddit posts:",
        key="qa_input"
    )

    if user_query:
        with st.spinner("Generating insight..."):
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

# Footer
st.markdown("---")
st.markdown("""
<footer style='text-align: center;'>
  🔗 <a href="https://github.com/ronjamino/trendmosiac" target="_blank">View the code on GitHub</a>
</footer>
""", unsafe_allow_html=True)
