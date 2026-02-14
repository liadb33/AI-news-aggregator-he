import asyncio
import os
import time
from datetime import datetime
from telegram import Bot
from telegram.error import RetryAfter, TimedOut
from telegram.constants import ParseMode
import html # For html.escape

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not installed, will use system environment variables

# Import functions from other modules
from utils import get_rss_feed_items, get_hacker_news_items, get_github_trending_repos, get_source_emoji
from db import load_sent_links, save_sent_link, initialize_db
from scoring import filter_and_rank  # Removed translate_to_hebrew

# --- Configuration Variables ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Initialize the Telegram Bot object with your token.
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Channel ID for display in the Telegram post footer.
TELEGRAM_CHANNEL_ID_FOR_FOOTER = TELEGRAM_CHANNEL_ID

# Telegram message character limit
TELEGRAM_MAX_LENGTH = 4096


# --- Function Definitions ---

def collect_all_news(sent_links):
    """
    Collects and aggregates news items from various sources (RSS, GitHub Trending, Hacker News).
    Ensures uniqueness of news items based on their links by filtering against `sent_links`.

    Args:
        sent_links (set): A set of previously sent links to avoid duplicates.

    Returns:
        list: A list of tuples, each containing (title, link, summary, source_name_for_emoji_lookup).
    """
    all_news_items = []

    print("\n--- Starting News Collection ---")

    # 1. Collect from RSS Feeds
    all_news_items.extend(get_rss_feed_items("https://hf.co/blog/feed.xml", "Hugging Face Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://jamesg.blog/hf-papers.xml", "Hugging Face Paper", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://www.reddit.com/r/MachineLearning/.rss", "ML Reddit", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://openai.com/blog/rss.xml", "OpenAI Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://thegradient.pub/rss/", "The Gradient", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://jalammar.github.io/feed.xml", "Jay Alammar", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://deepmind.google/blog/rss.xml", "DeepMind Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://news.mit.edu/rss/topic/artificial-intelligence2", "AI From MIT News", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://www.technologyreview.com/feed/", "General News From MIT News", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://blogs.microsoft.com/ai/feed/", "Microsoft AI Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://machinelearningmastery.com/blog/feed/", "machinelearningmastery Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://blogs.nvidia.com/blog/category/ai/feed/", "Nvidia AI Blog", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("https://towardsdatascience.com/feed/", "Towards Data Science", sent_links, limit=10))
    all_news_items.extend(get_rss_feed_items("http://theverge.com/rss/index.xml", "The Verge", sent_links, limit=20))

    # 2. Collect from GitHub Trending
    all_news_items.extend(get_github_trending_repos(language="python", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="jupyter-notebook", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="google colab", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="Artificial Intelligence", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="AI", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="machine-learning", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="deep-learning", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="nlp", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="Natural Language Processing", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="CV", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="Computer Vision", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="Data Science", sent_links=sent_links, limit=10))
    all_news_items.extend(get_github_trending_repos(language="Awesome Lists", sent_links=sent_links, limit=10))

    # 3. Collect from Hacker News API
    all_news_items.extend(get_hacker_news_items(sent_links=sent_links, limit=20))

    # Remove duplicates from collected items that might come from different sources
    unique_news_items = {}
    for title, link, summary, source_name_for_emoji_lookup in all_news_items:
        unique_news_items[link] = (title, link, summary, source_name_for_emoji_lookup)
    
    final_news_list = list(unique_news_items.values())

    print(f"Total unique new items collected: {len(final_news_list)}")
    print("--- News Collection Finished ---")

    return final_news_list


def format_digest_message(scored_items):
    """
    Formats all scored news items into a single Hebrew daily digest message.
    Items are grouped into categories:
      - 🚀 שחרורים גדולים (Big Releases) — high score, non-GitHub items
      - 🔥 חם בגיטהאב (Hot on GitHub) — GitHub Trending items
      - ⚡ חדשות הבזק (Flash News) — remaining items

    Titles are translated to Hebrew using Google Translate.

    Args:
        scored_items (list): List of tuples (title, link, summary, source_name, score).

    Returns:
        list: A list of HTML-formatted message strings (split if exceeding Telegram's limit).
    """
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Categorize items
    big_releases = []    # score >= 5, non-GitHub
    github_trending = [] # GitHub Trending items
    flash_news = []      # everything else

    for title, link, summary, source_name, score in scored_items:
        if "GitHub Trending" in source_name:
            github_trending.append((title, link, summary, source_name, score))
        elif score >= 5:
            big_releases.append((title, link, summary, source_name, score))
        else:
            flash_news.append((title, link, summary, source_name, score))

    # Build the digest message
    lines = []
    lines.append(f"📰 <b>סיכום חדשות AI יומי</b>")
    lines.append(f"🗓 {now}")
    lines.append("")

    # --- Big Releases Section ---
    if big_releases:
        lines.append("🚀 <b>שחרורים גדולים</b>")
        lines.append("")
        for title, link, summary, source_name, score in big_releases:
            emoji = get_source_emoji(source_name)
            escaped_title = html.escape(title)
            lines.append(f"{emoji} <b>{escaped_title}</b>")
            lines.append(f"   🔗 <a href='{link}'>Read More</a>")
            lines.append("")

    # --- GitHub Trending Section ---
    if github_trending:
        lines.append("🔥 <b>חם בגיטהאב</b>")
        lines.append("")
        for title, link, summary, source_name, score in github_trending:
            emoji = get_source_emoji(source_name)
            repo_display = title.split(": ", 1)[-1] if ": " in title else title
            escaped_repo = html.escape(repo_display)
            escaped_summary = html.escape(summary) if summary and summary != "No description available." else ""
            
            if escaped_summary:
                lines.append(f"{emoji} <b>{escaped_repo}</b> — {escaped_summary}")
            else:
                lines.append(f"{emoji} <b>{escaped_repo}</b>")
            lines.append(f"   🔗 <a href='{link}'>Read More</a>")
            lines.append("")

    # --- Flash News Section ---
    if flash_news:
        lines.append("⚡ <b>חדשות הבזק</b>")
        lines.append("")
        for title, link, summary, source_name, score in flash_news:
            emoji = get_source_emoji(source_name)
            escaped_title = html.escape(title)
            lines.append(f"{emoji} <a href='{link}'>{escaped_title}</a>")

        lines.append("")

    # --- Footer ---
    lines.append(f"📣 Channel: {TELEGRAM_CHANNEL_ID_FOR_FOOTER}")

    # Handle "no items" case
    if not big_releases and not github_trending and not flash_news:
        return [f"📰 <b>סיכום חדשות AI יומי</b>\n🗓 {now}\n\nאין חדשות חדשות היום 🤷\n\n📣 Channel: {TELEGRAM_CHANNEL_ID_FOR_FOOTER}"]

    # Join all lines into a single message
    full_message = "\n".join(lines)

    # Split into multiple messages if exceeding Telegram's limit
    if len(full_message) <= TELEGRAM_MAX_LENGTH:
        return [full_message]
    
    # Split into parts
    messages = []
    current_msg = ""
    part_num = 1
    
    for line in lines:
        test_line = line + "\n"
        if len(current_msg) + len(test_line) > TELEGRAM_MAX_LENGTH - 50:  # Leave room for part header
            messages.append(current_msg.strip())
            current_msg = f"📰 <b>המשך סיכום ({part_num + 1})</b>\n\n"
            part_num += 1
        current_msg += test_line
    
    if current_msg.strip():
        messages.append(current_msg.strip())

    print(f"Digest split into {len(messages)} messages due to length")
    return messages


async def send_digest_to_telegram(scored_items):
    """
    Formats and sends the daily digest to the Telegram channel.
    Saves all included links to the database after successful sending.

    Args:
        scored_items (list): List of tuples (title, link, summary, source_name, score).
    """
    print("\n--- Starting to send digest to Telegram ---")
    
    if not scored_items:
        print("No items passed the scoring filter. Nothing to send.")
        return

    # Format the digest message(s)
    print("\n--- Formatting digest ---")
    digest_messages = format_digest_message(scored_items)
    print(f"Digest formatted: {len(digest_messages)} message(s) to send")

    # Send each message part
    for i, msg in enumerate(digest_messages):
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=msg,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True  # Avoid preview clutter in digest
            )
            print(f"SUCCESS: Digest part {i + 1}/{len(digest_messages)} sent to Telegram.")
            if i < len(digest_messages) - 1:
                await asyncio.sleep(3)  # Wait between parts
        except RetryAfter as e:
            wait_time = e.retry_after + 1
            print(f"Telegram Flood Control: Waiting for {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                print(f"SUCCESS (retry): Digest part {i + 1} sent after waiting.")
            except Exception as retry_e:
                print(f"ERROR (retry failed): Could not send digest part {i + 1}: {retry_e}")
                return  # Don't save links if sending failed
        except TimedOut:
            print(f"TIMEOUT: Telegram API timed out. Retrying in 5 seconds.")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"ERROR: Could not send digest to Telegram: {e}")
            return  # Don't save links if sending failed

    # Save all links to DB only after successful sending
    for title, link, summary, source_name, score in scored_items:
        save_sent_link(link)
    
    print(f"Saved {len(scored_items)} links to database.")
    print("--- Finished sending digest to Telegram ---")


async def main_bot_run():
    """
    Orchestrates the entire news bot operation:
    1. Initializes the database for sent links.
    2. Loads previously sent links from the database.
    3. Collects news from all configured sources.
    4. Scores and filters news by relevance.
    5. Sends one consolidated Hebrew digest to Telegram.
    6. Measures and prints the total execution time.
    """
    start_time = time.time()

    print(f"\n--- Bot run started at: {time.ctime()} ---")

    # Ensure the database is initialized
    initialize_db()
    
    # Load previously sent links from the database
    initial_sent_links = load_sent_links()
    print(f"Number of previously sent links loaded from DB: {len(initial_sent_links)}")

    # Collect news from all sources
    collected_news = collect_all_news(initial_sent_links)

    # Score and filter news items
    print("\n--- Scoring and Filtering News ---")
    scored_news = filter_and_rank(collected_news)

    # Send the consolidated digest
    await send_digest_to_telegram(scored_news)

    end_time = time.time()
    duration = end_time - start_time

    print(f"--- Bot run finished at: {time.ctime()} ---")
    print(f"Total execution time: {duration:.2f} seconds")

# This block ensures main_bot_run() is executed when the script is run directly.
if __name__ == "__main__":
    asyncio.run(main_bot_run())
