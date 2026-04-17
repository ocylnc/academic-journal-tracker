import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "latest.html"


def load_journals():
    with open("journals.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def scrape_sage(section):
    r = requests.get(section["url"], timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    articles = []

    for item in soup.select("article"):
        title_tag = item.select_one("h5 a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://journals.sagepub.com" + title_tag.get("href")
        articles.append((title, link))

    return articles


def scrape_wiley(section):
    r = requests.get(section["url"], timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    articles = []

    for item in soup.select("li.search__item"):
        title_tag = item.select_one("h2 a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://onlinelibrary.wiley.com" + title_tag.get("href")
        articles.append((title, link))

    return articles


def scrape_etui(section):
    r = requests.get(section["url"], timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = []

    for item in soup.select("h3 a"):
        title = item.get_text(strip=True)
        link = item["href"]
        if link.startswith("/"):
            link = "https://www.etui.org" + link
        articles.append((title, link))

    return articles


def scrape_bristol(section):
    r = requests.get(section["url"], timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = []

    for item in soup.select("div.product-listing-item"):
        title_tag = item.select_one("h3 a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag["href"]
        articles.append((title, link))

    return articles


def scrape_section(platform, section):
    if platform == "sage":
        return scrape_sage(section)
    if platform == "wiley":
        return scrape_wiley(section)
    if platform == "etui":
        return scrape_etui(section)
    if platform == "bristol":
        return scrape_bristol(section)
    return []


def build_html(results):
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    html = [f"<h1>Academic Journal Monitoring</h1>",
            f"<p><em>Last scan: {now}</em></p>"]

    for journal, sections in results.items():
        html.append(f"<h2>{journal}</h2>")
        for section_name, articles in sections.items():
            html.append(f"<h3>{section_name}</h3>")
            if not articles:
                html.append("<p>No items found.</p>")
            else:
                html.append("<ul>")
                for title, link in articles:
                    html.append(f'<li><a href="{link}">{title}</a></li>')
                html.append("</ul>")

    return "\n".join(html)


def main():
    journals = load_journals()
    results = {}

    for journal in journals:
        journal_name = journal["name"]
        platform = journal["platform"]
        results[journal_name] = {}

        for section in journal["sections"]:
            section_name = section["type"]
            articles = scrape_section(platform, section)
            results[journal_name][section_name] = articles

    html = build_html(results)
    OUTPUT_FILE.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
