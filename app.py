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

# CSS for pill badges
st.markdown("""
<style>
.pill {
    display: inline-block;
    background-color: #eeeeee;
    color: #333;
    padding: 0.35em 0.75em;
    margin: 0.25em 0.25em 0 0;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 999px;
}
</style>
""", unsafe_allow_html=True)

# CSS for sidebar layout
st.markdown("""
<style>
div[data-baseweb="select"] {
    font-size: 0.9rem;
}
.sidebar-section {
    padding: 1rem 0;
    border-bottom: 1px solid #eaeaea;
}
</style>
""", unsafe_allow_html=True)

# App title
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
# Fetch & Enrich
# ---------------------------
@st.cache_data(show_spinner=False)
def get_trend_insights(topic):
    subreddits = [
        "dataengineering", "datascience", "machinelearning",
        "bigdata", "analytics", "learnmachinelearning",
        "devops", "SQL", "CloudComputing"
    ]

    reddit_posts = fetch_reddit_posts(subreddits, topic, total_limit=10)
    hn_posts = fetch_hn_posts(topic, limit=10)
    so_posts = fetch_so_posts(topic, limit=10)

    combined = reddit_posts + hn_posts + so_posts
    enriched = []

    for post in combined:
        summary_raw = summarise_post(post["title"], post["body"])

        try:
            # Ensure we parse a dict safely
            parsed = ast.literal_eval(summary_raw)
            if isinstance(parsed, dict) and "summary" in parsed:
                summary = parsed
            else:
                raise ValueError("Parsed summary is not a valid dict with expected keys.")
        except Exception as e:
            summary = {
                "summary": summary_raw.strip() if summary_raw else "⚠️ Summary could not be parsed.",
                "sentiment": "unknown",
                "tags": []
            }

        post["summary"] = summary
        enriched.append(post)

    return enriched, len(reddit_posts), len(hn_posts), len(so_posts)

# ---------------------------
# Main UI logic
# ---------------------------
if topic:
    with st.spinner("🔍 Fetching posts and generating summaries..."):
        enriched, reddit_count, hn_count, so_count = get_trend_insights(topic)

    st.success(f"✅ Pulled {reddit_count} Reddit, {hn_count} Hacker News, and {so_count} Stack Overflow posts about '{topic}'")

    # Tag extraction
    all_tags = []
    for post in enriched:
        all_tags.extend(post["summary"].get("tags", []))
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(10)

    # Sidebar filter
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🏷 Filter by Tag")

        tag_label_map = {f"{tag} ({count})": tag for tag, count in top_tags}
        display_options = list(tag_label_map.keys())

        selected_display_labels = st.multiselect(
            label="",
            options=display_options,
            placeholder="Choose tags like 'dbt', 'DuckDB', etc.'"
        )

        selected_tags = [tag_label_map[label] for label in selected_display_labels]
        st.markdown('</div>', unsafe_allow_html=True)

    # Filter posts
    if selected_tags:
        filtered = [
            post for post in enriched
            if any(tag in post["summary"].get("tags", []) for tag in selected_tags)
        ]
    else:
        filtered = enriched
    
    # No posts found
    if not filtered:
        st.warning("😕 No posts found for this topic. Try a different keyword or broaden your search.")
        st.stop()

    # Refresh button
    if st.button("🔁 Refresh posts"):
        st.cache_data.clear()
        st.rerun()

    # Show selected tag badges
    if selected_tags:
        st.markdown("### 🏷️ Showing posts tagged with:")
        tag_html = " ".join([
            f"<span class='pill'>{tag}</span>" for tag in selected_tags
        ])
        st.markdown(tag_html, unsafe_allow_html=True)

    # ---------------------------
    # Step 2: Q&A Input
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
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            st.markdown("### 🧠 Community Insight")
            st.write(response.choices[0].message.content.strip())

    # ---------------------------
    # Post Sections
    # ---------------------------
    reddit_posts = [p for p in filtered if p.get("source") == "reddit"]
    hn_posts = [p for p in filtered if p.get("source") == "hackernews"]
    so_posts = [p for p in filtered if p.get("source") == "stackoverflow"]

    if reddit_posts:
        st.subheader("🟠 Reddit Posts")
        for post in reddit_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Reddit]({post['url']})")

    if hn_posts:
        st.subheader("🟧 Hacker News Posts")
        for post in hn_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Hacker News]({post['url']})")

    if so_posts:
        st.subheader("🟦 Stack Overflow Posts")
        for post in so_posts:
            with st.expander(post["title"]):
                st.markdown(post["summary"]["summary"])
                st.markdown(f"**🗣 Sentiment:** {post['summary'].get('sentiment', 'unknown')}")
                st.markdown(f"**🏷 Tags:** {', '.join(post['summary'].get('tags', []))}")
                st.markdown(f"[🔗 View on Stack Overflow]({post['url']})")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("""
<footer style='text-align: center;'>
  🔗 <a href="https://github.com/ronjamino/trendmosiac" target="_blank">View the code on GitHub</a>
</footer>
""", unsafe_allow_html=True)
