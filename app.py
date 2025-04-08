# ==============================
# app.py (Streamlit UI)
# ==============================
import streamlit as st
import json

with open("trendmosiac_output.json") as f:
    data = json.load(f)

st.title("TrendMosaic – Reddit Trend Explorer")
topic = st.selectbox("Select a subreddit post:", [d['title'] for d in data])

post = next(p for p in data if p['title'] == topic)
st.write("**Summary:**", post['summary']['summary'])
st.write("**Sentiment:**", post['summary']['sentiment'])
st.write("**Tags:**", ", ".join(post['summary']['tags']))
st.write("[View on Reddit](%s)" % post['url'])

st.markdown("---")
st.markdown("🔗 [View the code on GitHub](https://github.com/ronjamino/trendmosiac)")