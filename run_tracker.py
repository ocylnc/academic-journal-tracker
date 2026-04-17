import yaml
import feedparser
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "latest.html"


def load_journals():
    with open("journals.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_rss(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:15]:  # en fazla 15 madde
        title = entry.get("title", "").strip()
        link = entry.get("link", "")
        items.append((title, link))
    return items


def build_html(results):
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    html = [
        "<html><head><meta charset='utf-8'><title>Academic Monitoring</title></head><body>",
        "<h1>Academic Journal Monitoring</h1>",
        f"<p><em>Last scan: {now}</em></p>"
    ]

    for journal, articles in results.items():
        html.append(f"<h2>{journal}</h2>")
        if not articles:
            html.append("<p>No new items.</p>")
        else:
            html.append("<ul>")
            for title, link in articles:
                html.append(f"<li><a href='{link}' target='_blank'>{title}</a></li>")
            html.append("</ul>")

    html.append("</body></html>")
    return "\n".join(html)


def main():
    journals = load_journals()
    results = {}

    for journal in journals:
        journal_name = journal["name"]
        results[journal_name] = []

        for section in journal["sections"]:
            rss_url = section.get("rss")
            if rss_url:
                results[journal_name].extend(fetch_rss(rss_url))

    html = build_html(results)
    OUTPUT_FILE.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
