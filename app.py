import streamlit as st
import os
import openai
import ast
from dotenv import load_dotenv
from sources.reddit_source import fetch_reddit_posts
from sources.hn_source import fetch_hn_posts
from sources.so_source import fetch_so_posts
from summarise_discussion import summarise_post
from collections import Counter

# Load API keys
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="TrendMosaic", layout="centered")

st.markdown("""
<style>
/* Clean up multiselect appearance in the sidebar */
div[data-baseweb="select"] {
    font-size: 0.9rem;
}
.sidebar-section {
    padding: 1rem 0;
    border-bottom: 1px solid #eaeaea;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧩 TrendMosaic – Tech Trend Explorer")

# ---------------------------
# Step 1: Context Input
# ---------------------------
st.subheader("1️⃣ What tech topic are you interested in?")
topic = st.text_input(
    "Enter a topic you'd like to explore (e.g. 'DuckDB', 'dbt', 'data engineering')",
    key="context_input",
    placeholder="Type something and press Enter..."
)

# ---------------------------
# Caching Reddit post fetch/summarisation
# ---------------------------
@st.cache_data(show_spinner=False)
def get_trend_insights(topic):
    subreddits = [
        "dataengineering",
        "datascience",
        "machinelearning",
        "bigdata",
        "analytics",
        "learnmachinelearning",
        "devops",
        "SQL",
        "CloudComputing"
    ]

    # Fetch from Reddit
    reddit_posts = fetch_reddit_posts(subreddits, topic, total_limit=10)

    # Fetch from Hacker News
    hn_posts = fetch_hn_posts(topic, limit=10)

    # Fetch from Stack Overflow
    so_posts = fetch_so_posts(topic, limit=10)

    combined = reddit_posts + hn_posts + so_posts
    enriched = []

    for post in combined:
        summary_raw = summarise_post(post["title"], post["body"])
        try:
            summary = ast.literal_eval(summary_raw)
        except Exception:
            summary = {"summary": summary_raw, "sentiment": "unknown", "tags": []}
        post["summary"] = summary
        enriched.append(post)

    return enriched, len(reddit_posts), len(hn_posts), len(so_posts)


# ---------------------------
# When topic is submitted
# ---------------------------
if topic:
    with st.spinner("🔍 Fetching posts and generating summaries..."):
        enriched, reddit_count, hn_count, so_count = get_trend_insights(topic)

    st.success(f"✅ Pulled {reddit_count} Reddit, {hn_count} Hacker News, and {so_count} Stack Overflow posts about '{topic}'")

    from collections import Counter

    # Extract tags from all summaries
    all_tags = []
    for post in enriched:
        tags = post["summary"].get("tags", [])
        all_tags.extend(tags)

    # Count tag frequencies
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(10)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🏷 Filter by Tag")

        # Convert top_tags into label → tag map
        tag_label_map = {f"{tag} ({count})": tag for tag, count in top_tags}
        display_options = list(tag_label_map.keys())

        selected_display_labels = st.multiselect(
            label="",
            options=display_options,
            placeholder="Choose tags like 'dbt', 'DuckDB', etc.'"
        )

    selected_tags = [tag_label_map[label] for label in selected_display_labels]

    st.markdown('</div>', unsafe_allow_html=True)

    # Convert selected labels back to raw tag values
    selected_tags = [tag_label_map[label] for label in selected_display_labels]

    # Refresh button
    if st.button("🔁 Refresh posts"):
        st.cache_data.clear()
        st.rerun()

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
        with st.spinner("💬 Generating insight from discussions..."):
            context = "\n\n".join([p["summary"]["summary"] for p in enriched])
            prompt = f"""
Based on the following Reddit summaries, answer the question: "{user_query}"

Summaries:
{context}

Please respond with a concise and clear community-sourced answer, summarising any disagreements if relevant.
"""

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4"
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400  # 🧠 Limit token usage to control cost
            )

            st.markdown("### 🧠 Community Insight")
            st.write(response.choices[0].message.content.strip())

    # =============================
    # 📚 Supporting Reddit Posts
    # =============================
    reddit_posts = [p for p in enriched if p.get("source") == "reddit"]
    if reddit_posts:
        st.subheader("🟠 Reddit Posts")
        for post in reddit_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Reddit]({post['url']})")

    # =============================
    # 📚 Supporting Hacker News Posts
    # =============================
    hn_posts = [p for p in enriched if p.get("source") == "hackernews"]
    if hn_posts:
        st.subheader("🟧 Hacker News Posts")
        for post in hn_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Hacker News]({post['url']})")

    # =============================
    # 📚 Supporting Stack Overflow Posts
    # =============================
    so_posts = [p for p in enriched if p.get("source") == "stackoverflow"]
    if so_posts:
        st.subheader("🟦 Stack Overflow Posts")
        for post in so_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Stack Overflow]({post['url']})")

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
