"""
Keyword-based scoring and filtering for news items.
Scores news items by relevance to AI topics and filters low-score items.
"""

import time

# --- Keyword Scoring ---

# Keywords mapped to relevance scores.
# Higher score = more relevant to the user's interests.
KEYWORDS = {
    # High priority — new model releases & names
    "gpt": 5, "gpt-4": 5, "gpt-5": 5, "chatgpt": 5,
    "claude": 5, "gemini": 5, "llama": 5, "mistral": 5,
    "sora": 5, "veo": 5, "deepseek": 5, "phi": 4,
    "qwen": 4, "gemma": 4, "stable diffusion": 5,
    "midjourney": 5, "whisper": 4, "copilot": 4,
    "dall-e": 5, "flux": 4, "ideogram": 4,

    # High priority — video & image generation
    "video model": 5, "text-to-video": 5, "video generation": 5,
    "text-to-image": 4, "image generation": 4, "image model": 4,

    # Medium priority — general AI concepts
    "release": 4, "released": 4, "launch": 4, "launches": 4,
    "announce": 4, "announcing": 4, "introducing": 4,
    "open-source": 4, "open source": 4, "breakthrough": 4,
    "state-of-the-art": 4, "sota": 4, "new model": 5,
    "benchmark": 3, "multimodal": 4, "agent": 3, "agents": 3,
    "reasoning": 3, "fine-tune": 3, "fine-tuning": 3,
    "training": 3, "transformer": 3, "diffusion": 3,
    "robotics": 3, "self-driving": 3, "autonomous": 3,

    # Medium priority — ecosystem & tools
    "hugging face": 3, "openai": 4, "anthropic": 4,
    "deepmind": 4, "google ai": 3, "meta ai": 3,
    "microsoft ai": 3, "nvidia": 3,
    "trending": 2, "framework": 2, "library": 2,
    "api": 2, "sdk": 2, "dataset": 2, "tool": 2,
}

# Minimum score for an item to be included in the digest.
MIN_SCORE = 3

# Maximum number of items to include in the digest.
MAX_ITEMS = 30


def score_item(title, summary):
    """
    Scores a news item based on keyword matches in its title and summary.

    Args:
        title (str): The news item title.
        summary (str): The news item summary.

    Returns:
        int: The relevance score (sum of matched keyword weights).
    """
    text = f"{title} {summary}".lower()
    score = 0
    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight
    return score


def filter_and_rank(news_items, min_score=MIN_SCORE, max_items=MAX_ITEMS):
    """
    Scores all news items, filters those below the threshold,
    sorts by score (highest first), and caps at max_items.

    Args:
        news_items (list): List of tuples (title, link, summary, source_name).
        min_score (int): Minimum score to include an item.
        max_items (int): Maximum number of items to return.

    Returns:
        list: Filtered and ranked list of tuples
              (title, link, summary, source_name, score).
    """
    scored_items = []
    for title, link, summary, source_name in news_items:
        item_score = score_item(title, summary)
        if item_score >= min_score:
            scored_items.append((title, link, summary, source_name, item_score))
        else:
            print(f"FILTERED OUT (score={item_score}): {title}")

    # Sort by score descending
    scored_items.sort(key=lambda x: x[4], reverse=True)

    # Cap at max_items
    result = scored_items[:max_items]

    print(f"\nScoring complete: {len(news_items)} collected → {len(scored_items)} passed filter → {len(result)} in digest")
    return result
