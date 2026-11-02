import feedparser
import json
import os
import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

NEWS_SOURCES = {
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "NPR World": "https://feeds.npr.org/1004/rss.xml",
    "UN News": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "DW News": "https://rss.dw.com/rdf/rss-en-world",
}

def collect_news():
    articles = []
    seen = set()

    for source, url in NEWS_SOURCES.items():
        print(f"Checking {source}...")

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "").strip()

                if not title or not link:
                    continue

                article_id = hashlib.sha256(
                    link.encode("utf-8")
                ).hexdigest()

                if article_id in seen:
                    continue

                seen.add(article_id)

                published = entry.get(
                    "published",
                    entry.get("updated", "")
                )

                try:
                    date = parsedate_to_datetime(published)
                    published = date.isoformat()
                except Exception:
                    pass

                articles.append({
                    "id": article_id,
                    "source": source,
                    "title": title,
                    "summary": summary,
                    "url": link,
                    "published": published
                })

        except Exception as error:
            print(f"Error with {source}: {error}")

    articles.sort(
        key=lambda item: item["published"],
        reverse=True
    )

    os.makedirs("data", exist_ok=True)

    with open(
        "data/news.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            articles,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Collected {len(articles)} articles.")

    return articles


if __name__ == "__main__":
    collect_news()
