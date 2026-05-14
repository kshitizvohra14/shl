import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(CATALOG_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

cards = soup.find_all("a")

results = []
visited = set()

for card in cards:
    href = card.get("href")

    if not href:
        continue

    if "/products/" not in href:
        continue

    url = urljoin(BASE_URL, href)

    if url in visited:
        continue

    visited.add(url)

    try:
        page = requests.get(url, headers=headers)
        psoup = BeautifulSoup(page.text, "html.parser")

        title = psoup.find("h1")
        title = title.text.strip() if title else "Unknown"

        text = psoup.get_text(" ", strip=True)

        item = {
            "name": title,
            "url": url,
            "description": text[:5000]
        }

        results.append(item)
        print("Added:", title)

    except Exception as e:
        print(e)

with open("data/shl_catalog.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} assessments")