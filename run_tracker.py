
import smtplib
from email.message import EmailMessage
import os
import yaml
import json
import feedparser
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "latest.html"

SEEN_FILE = Path("seen_items.json")

def send_email(results):
    print("DEBUG: send_email çalıştı")

    body_lines = []

    for journal, articles in results.items():
        if articles:
            body_lines.append(f"\n{journal}")
            for title, link in articles:
                body_lines.append(f"- {title}\n  {link}")

    msg = EmailMessage()
    msg["Subject"] = "TEST – Academic Tracker Mail"
    msg["From"] = os.environ["MAIL_USER"]
    msg["To"] = os.environ["MAIL_RECEIVER"]
    msg.set_content("\n".join(body_lines) or "TEST MAIL")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(
            os.environ["MAIL_USER"],
            os.environ["MAIL_PASSWORD"]
        )
        smtp.send_message(msg)

def load_journals():
    with open("journals.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), indent=2),
        encoding="utf-8"
    )


def fetch_rss(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if title and link:
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
            html.append("<p>No new items since last scan.</p>")
        else:
            html.append("<ul>")
            for title, link in articles:
                html.append(f'<li><a href="{link}" target="_blank">{title}</a></li>')
            html.append("</ul>")

    html.append("</body></html>")
    return "\n".join(html)


def main():
    journals = load_journals()
    seen = load_seen()
    new_seen = set(seen)
    results = {}

    for journal in journals:
        journal_name = journal["name"]
        results[journal_name] = []

        for section in journal["sections"]:
            rss_url = section.get("rss")
            if not rss_url:
                continue

            for title, link in fetch_rss(rss_url):
                if link not in seen:
                    results[journal_name].append((title, link))
                    new_seen.add(link)

    save_seen(new_seen)

    html = build_html(results)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    send_email(results)

if __name__ == "__main__":
    main()
