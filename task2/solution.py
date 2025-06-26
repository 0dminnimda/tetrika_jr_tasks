import logging
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from collections import Counter
from urllib.parse import urljoin
from collections.abc import Mapping


logger = logging.getLogger(__name__)

BASE_URL = "https://ru.wikipedia.org"
START_URL = urljoin(BASE_URL, "wiki/Категория:Животные_по_алфавиту")
OUTPUT_FILE = "beasts.csv"
SORT_COUNTS = False


def fetch_page(url: str) -> "str | None":
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def parse_animals_and_next_page_link(animal_counts: Counter[str], html: str) -> "str | None":
    soup = BeautifulSoup(html, "html.parser")

    letter_groups = soup.select("div#mw-pages div.mw-category-group")
    for group in letter_groups:
        letter_tag = group.find("h3")
        if not letter_tag:
            continue

        letter = letter_tag.text.strip().upper()
        if len(letter) == 1:
            items = group.find_all("li")
            animal_counts[letter] += len(items)
        else:
            logger.warning(f"Group tag is not a letter: '{letter}'")

    next_page_link = None
    next_page_tag = soup.find("a", string="Следующая страница")
    if isinstance(next_page_tag, Tag):
        href = next_page_tag.get("href")
        if href:
            next_page_link = urljoin(BASE_URL, str(href))

    return next_page_link


def scrape_and_count_animals(start_url: str) -> Counter[str]:
    logger.info(f"Starting animal scraper for URL: {start_url}")

    animal_counts = Counter[str]()
    visited_urls = set()
    current_url: str | None = start_url
    page_num = 1

    while current_url is not None:
        if current_url in visited_urls:
            logger.warning(f"Cycle detected. Already visited {current_url}. Stopping.")
            break
        visited_urls.add(current_url)

        logger.info(f"Fetching page #{page_num}: {current_url}")

        html = fetch_page(current_url)
        if not html:
            logger.warning(f"Failed to fetch {current_url}, stopping.")
            break

        current_url = parse_animals_and_next_page_link(animal_counts, html)
        page_num += 1

    logger.info("Scraping complete.")
    return animal_counts


def save_counts_to_csv(counts: Mapping[str, int], filename: str):
    with open(filename, "w", encoding="utf-8") as file:
        # file.write(f"Letter,Count\n")
        for letter, count in counts.items():
            file.write(f"{letter},{count}\n")

    logger.info(f"Data saved to {filename}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    animal_counts = scrape_and_count_animals(START_URL)
    if SORT_COUNTS:
        animal_counts = dict(sorted(animal_counts.items()))
    save_counts_to_csv(animal_counts, OUTPUT_FILE)


if __name__ == "__main__":
    main()
