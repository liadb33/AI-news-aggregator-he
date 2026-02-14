# 🤖📰 AI News Aggregator Bot with Smart Filtering

> **Forked from**: [hrnrxb/AI-News-Aggregator-Bot](https://github.com/hrnrxb/AI-News-Aggregator-Bot)  
> Enhanced with keyword-based scoring and consolidated daily digest format.

Tired of drowning in 100+ individual AI news notifications? This enhanced Telegram bot **intelligently filters** AI news based on relevance and delivers it as **one clean, organized daily digest** to your Telegram channel.

## 🎯 What Makes This Version Different?

### ✨ Smart Keyword Scoring
- **Automatically scores** news items based on relevance keywords (GPT, Claude, Sora, video models, releases, etc.)
- **Filters out noise** — only items scoring ≥3 make it to your digest
- **Prioritizes** new model releases, breakthrough announcements, and trending GitHub repos

### 📰 Consolidated Daily Digest
Instead of sending 100+ individual messages, the bot now sends **1-2 organized messages** grouped by category:
- 🚀 **שחרורים גדולים** (Big Releases) — High-impact news (score ≥5)
- 🔥 **חם בגיטהאב** (Hot on GitHub) — Trending repos
- ⚡ **חדשות הבזק** (Flash News) — Other relevant updates

All titles remain in **English** with Hebrew category headers for visual organization.

### 🎨 Example Digest Output
```
📰 סיכום חדשות AI יומי
🗓 14/02/2026 12:00

🚀 שחרורים גדולים

✨ GPT-5.2 derives a new result in theoretical physics
   🔗 Read More

🔬 Gemini 3 Flash: frontier intelligence built for speed
   🔗 Read More

🔥 חם בגיטהאב

🐍 karpathy/nanochat — Lightweight chat framework
   🔗 Read More

⚡ חדשות הבזק

💻 Microsoft open sources farm toolkit — Read More
🚀 Nvidia: New AI Blog Update — Read More

📣 Channel: @YourChannel
```

---

## 📊 Data Sources

This bot aggregates news from **26+ authoritative sources**:

### 🔬 Research Blogs
- Hugging Face, OpenAI, DeepMind, Google AI, Microsoft AI, Meta AI, Nvidia AI

### 🎓 Academic & Knowledge Platforms
- The Gradient, Jay Alammar, machinelearningmastery, Towards Data Science, MIT News

### 👥 Community & Trends
- Reddit (r/MachineLearning), Hacker News, The Verge

### 💻 GitHub Trending
- Tracks 13 languages/topics: Python, Jupyter Notebook, AI, ML, DL, NLP, CV, Data Science, etc.

---

## 🚀 Technologies Used

- **Python 3.11+** — Core language
- **`python-telegram-bot`** — Telegram Bot API wrapper
- **`feedparser`** — RSS/Atom feed parsing
- **`requests`** — HTTP requests for APIs
- **`BeautifulSoup4`** — Web scraping (GitHub Trending)
- **`sqlite3`** — Persistent duplicate tracking
- **`python-dotenv`** — Environment variable management
- **GitHub Actions** — Automated CI/CD deployment

---

## ⚙️ Local Setup & Testing

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/AI-News-Aggregator-Bot.git
cd AI-News-Aggregator-Bot
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Telegram Credentials

#### Create Your Bot
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy your **bot token** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Get Your Channel ID
1. Create a Telegram channel (can be private)
2. Add your bot as an **administrator** with "Post Messages" permission
3. Get the channel ID:
   - **Option A**: Use [@userinfobot](https://t.me/userinfobot) — add it to your channel and it will show the ID
   - **Option B**: Use the web URL (e.g., `web.telegram.org/k/#-1027404691` → ID is `-1027404691`)
   - **Option C**: Run the included helper script:
     ```bash
     python get_chat_id.py
     ```

#### Create `.env` File
In the project root, create a `.env` file:
```env
TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHANNEL_ID="-1027404691"
```

### 5️⃣ Test the Bot Locally
```bash
# Test connection
python test_bot.py

# Run the full bot
python src/main.py
```

You should see:
- News being collected from 26+ sources
- Items being scored and filtered
- One digest message sent to your Telegram channel

---

## 🚀 Deploy to GitHub Actions (Automated)

### Step 1: Push to GitHub

Make sure you have these files in your repo:
```
AI-News-Aggregator-Bot/
├── .github/
│   └── workflows/
│       └── main.yml
├── src/
│   ├── main.py
│   ├── utils.py
│   ├── db.py
│   └── scoring.py
├── requirements.txt
└── README.md
```

Push to GitHub:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Configure GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add these two secrets:

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHANNEL_ID` | Your channel ID (e.g., `-1027404691`) |

![GitHub Secrets](https://docs.github.com/assets/cb-48796/mw-1440/images/help/repository/actions-secrets-add.webp)

### Step 3: Enable GitHub Actions

1. Go to the **Actions** tab in your repo
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"AI News Aggregator Bot"**

### Step 4: Manual Test Run (Optional)

1. In the **Actions** tab, click on **"AI News Aggregator Bot"**
2. Click the **"Run workflow"** dropdown on the right
3. Select the branch (`main`) and click **"Run workflow"**
4. Watch it run in real-time — the logs will show:
   - News collection
   - Scoring and filtering
   - Digest being sent to Telegram

### Step 5: Verify Automatic Scheduling

The bot is configured to run **every 5 hours** automatically via `cron: '0 */5 * * *'` in `.github/workflows/main.yml`.

To change the schedule, edit this line in `main.yml`:
```yaml
schedule:
  - cron: '0 */5 * * *'  # Every 5 hours
  # - cron: '0 9 * * *'  # Every day at 9:00 AM UTC
  # - cron: '0 */1 * * *'  # Every hour
```

Use [crontab.guru](https://crontab.guru/) to build custom schedules.

---

## 🔧 Customization

### Adjust Scoring Keywords

Edit `src/scoring.py` to customize what's considered "important":

```python
KEYWORDS = {
    "gpt": 5,           # Very important
    "sora": 5,          # Very important
    "release": 4,       # Important
    "trending": 2,      # Less important
    # Add your own keywords
}

MIN_SCORE = 3  # Minimum score to include in digest
MAX_ITEMS = 30  # Maximum items per digest
```

### Change Message Format

Edit the `format_digest_message()` function in `src/main.py` to customize:
- Section headers
- Emojis
- Layout
- Footer text

---

## 🗄️ How Duplicate Prevention Works

The bot uses SQLite (`sent_links.db`) to track sent links across runs:

1. **Before sending**, checks if link exists in DB
2. **After successful send**, saves link to DB
3. **On GitHub Actions**, the DB is cached between runs using:
   - **Short-term**: GitHub Actions cache (7 days)
   - **Long-term**: Daily artifact backups

If the cache is lost, the bot will resend recent news once, then resume normal operation.

---

## 🐛 Troubleshooting

### "Chat not found" Error
- Verify bot is added to channel as **administrator**
- Verify bot has **"Post Messages"** permission
- Double-check `TELEGRAM_CHANNEL_ID` is correct (use `get_chat_id.py`)

### "No items passed filter"
- Lower `MIN_SCORE` in `src/scoring.py` (try `MIN_SCORE = 2`)
- Check keyword weights — maybe your interests need different keywords

### Database Errors
Delete the database and restart:
```bash
rm sent_links.db
python src/main.py
```

---

## 🤝 Contributing

Contributions are welcome! Ideas:
- Add new news sources
- Improve keyword scoring algorithm
- Add support for multiple languages
- Create a web dashboard to customize keywords

---

## 📜 Credits

- **Original Bot**: [hrnrxb/AI-News-Aggregator-Bot](https://github.com/hrnrxb/AI-News-Aggregator-Bot)
- **Enhancements**: Keyword scoring, consolidated digest format, improved filtering

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star This Repo!

If you find this bot useful, please ⭐ **star this repository** to show your support!
