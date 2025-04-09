# 🧩 TrendMosaic – Tech Trend Explorer

**TrendMosaic** is your AI-powered radar for tracking emerging technologies, tools, and sentiment in real time across developer communities. It aggregates posts from Reddit, Hacker News, and Stack Overflow, then uses LLMs to summarise discussions, tag technologies, and surface trends.

---

## 🔍 What It Does

- Aggregates real-world tech discussions from multiple sources
- Uses GPT to summarise and analyse sentiment
- Auto-tags technologies, frameworks, and tools
- Lets users ask natural-language questions about community sentiment
- Filters and groups content by platform and tags
- Built for rapid prototyping, insight hunting, or trend analysis

---

## 🖼 Screenshot / Demo

> _Live demo coming soon_

<img src="docs/screenshot.png" alt="TrendMosaic Screenshot" width="100%">

---

## 🚀 Getting Started Locally

### 1. Clone the repo

```bash
git clone https://github.com/ronjamino/trendmosiac.git
cd trendmosiac
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Copy the template and add your API keys:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your_openai_key_here
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=TrendMosaicBot/1.0
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🌐 Deployment (Optional)

TrendMosaic is ready to deploy to:

- [Streamlit Cloud](https://streamlit.io/cloud) – easiest
- Render / Fly.io / Heroku – for more control
- Docker (coming soon)

---

## 🧠 Tech Stack

| Layer         | Tech                                 |
|---------------|--------------------------------------|
| Backend       | Python, OpenAI (GPT), `praw`         |
| Frontend      | Streamlit                            |
| Data Sources  | Reddit, Hacker News, Stack Overflow  |
| Tagging       | GPT-driven entity extraction         |
| Storage       | In-memory (MVP), Vector DB planned   |

---

## 📄 License

MIT

---

## 🙌 Built by [@ronjamino](https://github.com/ronjamino)  
Pull requests welcome ✨
